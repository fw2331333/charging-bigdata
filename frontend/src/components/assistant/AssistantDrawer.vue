<template>
  <Teleport to="body">
    <!-- 收起态：底部小条，点击展开 -->
    <Transition name="assistant-fade">
      <button
        v-if="ui === 'minimized'"
        type="button"
        class="assistant-mini"
        :title="t('assistant.expand')"
        @click="ui = 'open'"
      >
        <span class="assistant-mini-icon" aria-hidden="true">◫</span>
        <span class="assistant-mini-title">{{ t('assistant.title') }}</span>
        <span v-if="messages.length" class="assistant-mini-badge">{{ messages.length }}</span>
        <svg class="assistant-mini-chevron" viewBox="0 0 24 24" aria-hidden="true">
          <path fill="currentColor" d="M7.41 15.41 12 10.83l4.59 4.58L18 14l-6-6-6 6z" />
        </svg>
      </button>
    </Transition>

    <!-- 展开态：聊天面板 -->
    <Transition name="assistant-panel">
      <div v-if="ui === 'open'" class="assistant-panel" role="dialog" :aria-label="t('assistant.title')">
        <header class="assistant-header">
          <div class="assistant-header-text">
            <h3 class="assistant-title">{{ t('assistant.title') }}</h3>
            <p class="assistant-sub">{{ t('assistant.subtitle') }}</p>
          </div>
          <div class="assistant-header-actions">
            <button
              type="button"
              class="assistant-icon-btn"
              :title="t('assistant.minimize')"
              @click="ui = 'minimized'"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path fill="currentColor" d="M19 13H5v-2h14v2z" />
              </svg>
            </button>
            <button
              type="button"
              class="assistant-icon-btn"
              :title="t('assistant.close')"
              @click="ui = 'closed'"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"
                />
              </svg>
            </button>
          </div>
        </header>

        <div ref="messagesRef" class="assistant-messages">
          <p v-if="!messages.length" class="assistant-empty">{{ t('assistant.empty') }}</p>
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            class="assistant-msg"
            :class="msg.role === 'user' ? 'is-user' : 'is-assistant'"
          >
            <div
              class="assistant-bubble"
              :class="{
                'is-thinking': msg.role === 'assistant' && !msg.content && streaming,
                'is-streaming': msg.role === 'assistant' && streaming && idx === messages.length - 1 && msg.content,
              }"
            >
              <template v-if="msg.role === 'assistant' && !msg.content && streaming">
                {{ t('assistant.thinking') }}
              </template>
              <div
                v-else-if="msg.role === 'assistant' && isStreamingMessage(idx)"
                class="assistant-stream-text"
              >{{ msg.content }}</div>
              <div
                v-else-if="msg.role === 'assistant'"
                class="assistant-md"
                v-html="renderMarkdown(msg.content)"
              />
              <template v-else>{{ msg.content }}</template>
            </div>
          </div>
        </div>

        <div v-if="lastRagSources.length" class="assistant-rag-wrap">
          <button type="button" class="assistant-rag-toggle" @click="ragExpanded = !ragExpanded">
            <span>{{ t('assistant.ragSources') }}（{{ lastRagSources.length }}）</span>
            <svg
              class="assistant-rag-chevron"
              :class="{ 'is-open': ragExpanded }"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path fill="currentColor" d="M7.41 8.59 12 13.17l4.59-4.58L18 10l-6 6-6-6z" />
            </svg>
          </button>
          <Transition name="assistant-rag-collapse">
            <div v-show="ragExpanded" class="assistant-rag">
              <span v-for="(src, i) in lastRagSources" :key="i" class="assistant-rag-chip">{{ src }}</span>
              <p v-if="lastRagMode" class="assistant-rag-mode">{{ ragModeLabel }}</p>
            </div>
          </Transition>
        </div>

        <div v-if="lastMode === 'rule'" class="assistant-hint">{{ t('assistant.noLlm') }}</div>

        <div v-if="!messages.length" class="assistant-suggestions">
          <button
            v-for="(s, i) in suggestions"
            :key="i"
            type="button"
            class="suggest-btn"
            :disabled="loading"
            @click="sendSuggestion(s)"
          >
            {{ s }}
          </button>
        </div>

        <form class="assistant-input" @submit.prevent="send">
          <el-input
            v-model="input"
            type="textarea"
            :rows="3"
            :placeholder="t('assistant.placeholder')"
            :disabled="loading"
            resize="none"
            @keydown.enter.exact.prevent="send"
          />
          <el-button type="primary" :loading="loading" :disabled="!input.trim()" @click="send">
            {{ t('assistant.send') }}
          </el-button>
        </form>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { streamAssistantChat, type AssistantChatResponse, type ChatMessage } from '@/api/assistant'
import { useLocale } from '@/composables/useLocale'
import { useRafBatch } from '@/composables/useRafBatch'
import { renderMarkdown } from '@/utils/markdown'

export type AssistantUiState = 'closed' | 'minimized' | 'open'

const ui = defineModel<AssistantUiState>({ default: 'closed' })

const { t, locale } = useLocale()
const input = ref('')
const loading = ref(false)
const streaming = ref(false)
const messages = ref<ChatMessage[]>([])
const lastMode = ref<'llm' | 'rule' | null>(null)
const lastRagSources = ref<string[]>([])
const lastRagMode = ref<AssistantChatResponse['rag_mode'] | null>(null)
const ragExpanded = ref(false)
const messagesRef = ref<HTMLElement | null>(null)
let streamAbort: AbortController | null = null
let pendingDelta = ''
let scrollRaf = 0

function isStreamingMessage(idx: number) {
  return streaming.value && idx === messages.value.length - 1
}

function scheduleScroll() {
  if (scrollRaf) return
  scrollRaf = requestAnimationFrame(() => {
    scrollRaf = 0
    void scrollToBottom()
  })
}

async function scrollToBottom() {
  await nextTick()
  const el = messagesRef.value
  if (el) el.scrollTop = el.scrollHeight
}

onBeforeUnmount(() => {
  if (scrollRaf) cancelAnimationFrame(scrollRaf)
})

const ragModeLabel = computed(() => {
  if (!lastRagMode.value) return ''
  if (lastRagMode.value === 'hybrid') return t('assistant.ragModeHybrid')
  if (lastRagMode.value === 'vector') return t('assistant.ragModeVector')
  return t('assistant.ragModeLexical')
})

const suggestions = computed(() => [
  t('assistant.suggest1'),
  t('assistant.suggest2'),
  t('assistant.suggest3'),
])

watch(ui, (state) => {
  if (state === 'open') void scrollToBottom()
})

async function sendMessage(text: string) {
  const trimmed = text.trim()
  if (!trimmed || loading.value) return

  streamAbort?.abort()
  streamAbort = new AbortController()
  pendingDelta = ''

  messages.value.push({ role: 'user', content: trimmed })
  messages.value.push({ role: 'assistant', content: '' })
  input.value = ''
  loading.value = true
  streaming.value = true
  await scrollToBottom()

  const assistantIdx = messages.value.length - 1

  const flushDelta = () => {
    if (!pendingDelta) return
    const msg = messages.value[assistantIdx]
    if (msg) msg.content += pendingDelta
    pendingDelta = ''
    scheduleScroll()
  }
  const { schedule: scheduleDelta, flushNow: flushDeltaNow, cancel: cancelDelta } = useRafBatch(flushDelta)

  try {
    const history = messages.value.slice(0, -2).slice(-8)
    await streamAssistantChat(
      {
        message: trimmed,
        locale: locale.value,
        history,
      },
      {
        onMeta: (meta) => {
          lastMode.value = meta.mode
          lastRagSources.value = meta.rag_sources ?? []
          lastRagMode.value = meta.rag_mode ?? null
          ragExpanded.value = false
        },
        onDelta: (chunk) => {
          pendingDelta += chunk
          scheduleDelta()
        },
        onDone: () => {
          flushDeltaNow()
          streaming.value = false
        },
        onError: (message) => {
          ElMessage.error(message || t('assistant.error'))
        },
      },
      streamAbort.signal,
    )
    flushDeltaNow()
    if (!messages.value[assistantIdx]?.content) {
      messages.value[assistantIdx]!.content = t('assistant.error')
    }
  } catch (err) {
    cancelDelta()
    if ((err as Error).name === 'AbortError') return
    ElMessage.error(t('assistant.error'))
    if (!messages.value[assistantIdx]?.content) {
      messages.value.pop()
    }
  } finally {
    flushDeltaNow()
    loading.value = false
    streaming.value = false
    streamAbort = null
    pendingDelta = ''
    await scrollToBottom()
  }
}

function send() {
  void sendMessage(input.value)
}

function sendSuggestion(text: string) {
  void sendMessage(text)
}
</script>

<style scoped>
.assistant-panel {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 3000;
  width: min(520px, calc(100vw - 32px));
  height: min(720px, calc(100vh - 32px));
  display: flex;
  flex-direction: column;
  border-radius: 14px;
  background: #fff;
  border: 1px solid #dce8f2;
  box-shadow: 0 12px 40px rgba(43, 88, 118, 0.18);
  overflow: hidden;
}
.assistant-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  padding: 14px 14px 10px;
  background: linear-gradient(135deg, #f8fbfe, #eef5fb);
  border-bottom: 1px solid #e8f0f6;
}
.assistant-header-text {
  min-width: 0;
}
.assistant-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2b5876;
}
.assistant-sub {
  margin: 4px 0 0;
  font-size: 12px;
  color: #8a9bab;
  line-height: 1.4;
}
.assistant-header-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}
.assistant-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #6b8aa3;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.assistant-icon-btn:hover {
  background: rgba(94, 159, 212, 0.15);
  color: #2b5876;
}
.assistant-icon-btn svg {
  width: 18px;
  height: 18px;
}
.assistant-messages {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.assistant-empty {
  margin: 20px 4px;
  font-size: 13px;
  color: #9aa8b5;
  line-height: 1.6;
}
.assistant-msg {
  display: flex;
}
.assistant-msg.is-user {
  justify-content: flex-end;
}
.assistant-bubble {
  max-width: 92%;
  padding: 11px 14px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.55;
  word-break: break-word;
}
.is-user .assistant-bubble {
  white-space: pre-wrap;
}
.assistant-stream-text {
  white-space: pre-wrap;
  word-break: break-word;
}
.is-assistant .assistant-bubble :deep(.assistant-md > :first-child) {
  margin-top: 0;
}
.is-assistant .assistant-bubble :deep(.assistant-md > :last-child) {
  margin-bottom: 0;
}
.is-assistant .assistant-bubble :deep(.assistant-md p) {
  margin: 0.55em 0;
}
.is-assistant .assistant-bubble :deep(.assistant-md h1),
.is-assistant .assistant-bubble :deep(.assistant-md h2),
.is-assistant .assistant-bubble :deep(.assistant-md h3),
.is-assistant .assistant-bubble :deep(.assistant-md h4) {
  margin: 0.75em 0 0.4em;
  font-weight: 600;
  line-height: 1.35;
  color: #2b5876;
}
.is-assistant .assistant-bubble :deep(.assistant-md h1) {
  font-size: 1.15em;
}
.is-assistant .assistant-bubble :deep(.assistant-md h2) {
  font-size: 1.08em;
}
.is-assistant .assistant-bubble :deep(.assistant-md h3),
.is-assistant .assistant-bubble :deep(.assistant-md h4) {
  font-size: 1em;
}
.is-assistant .assistant-bubble :deep(.assistant-md ul),
.is-assistant .assistant-bubble :deep(.assistant-md ol) {
  margin: 0.45em 0;
  padding-left: 1.35em;
}
.is-assistant .assistant-bubble :deep(.assistant-md li + li) {
  margin-top: 0.2em;
}
.is-assistant .assistant-bubble :deep(.assistant-md code) {
  padding: 0.1em 0.35em;
  border-radius: 4px;
  background: #e8eef4;
  font-family: Consolas, 'Courier New', monospace;
  font-size: 0.92em;
}
.is-assistant .assistant-bubble :deep(.assistant-md pre) {
  margin: 0.55em 0;
  padding: 10px 12px;
  border-radius: 8px;
  background: #1e293b;
  color: #e2e8f0;
  overflow-x: auto;
}
.is-assistant .assistant-bubble :deep(.assistant-md pre code) {
  padding: 0;
  background: transparent;
  color: inherit;
  font-size: 0.88em;
}
.is-assistant .assistant-bubble :deep(.assistant-md blockquote) {
  margin: 0.55em 0;
  padding: 0.2em 0 0.2em 0.75em;
  border-left: 3px solid #c5d9ea;
  color: #5a6f82;
}
.is-assistant .assistant-bubble :deep(.assistant-md a) {
  color: #3d7ab8;
  text-decoration: underline;
}
.is-assistant .assistant-bubble :deep(.assistant-md strong) {
  font-weight: 600;
  color: #2b5876;
}
.is-assistant .assistant-bubble :deep(.assistant-md table) {
  width: 100%;
  margin: 0.55em 0;
  border-collapse: collapse;
  font-size: 0.92em;
}
.is-assistant .assistant-bubble :deep(.assistant-md th),
.is-assistant .assistant-bubble :deep(.assistant-md td) {
  padding: 6px 8px;
  border: 1px solid #dce8f2;
}
.is-assistant .assistant-bubble :deep(.assistant-md th) {
  background: #eef5fb;
  font-weight: 600;
}
.is-user .assistant-bubble {
  background: #e8f2fa;
  color: #2b5876;
}
.is-assistant .assistant-bubble {
  background: #f4f7fa;
  color: #333;
  border: 1px solid #e8eef4;
}
.is-thinking {
  opacity: 0.75;
  font-style: italic;
}
.is-streaming::after {
  content: '▍';
  display: inline-block;
  margin-left: 2px;
  color: #4a8fc9;
  animation: assistant-cursor 0.9s step-end infinite;
}
@keyframes assistant-cursor {
  50% {
    opacity: 0;
  }
}
.assistant-hint {
  margin: 0 14px 8px;
  padding: 8px 10px;
  border-radius: 8px;
  background: #fffbeb;
  border: 1px solid #fde68a;
  font-size: 11px;
  color: #92400e;
  line-height: 1.45;
}
.assistant-rag-wrap {
  margin: 0 14px 8px;
  border: 1px solid #e8f0f6;
  border-radius: 8px;
  background: #f8fbfe;
  overflow: hidden;
}
.assistant-rag-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px 10px;
  border: none;
  background: transparent;
  color: #5a7a94;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}
.assistant-rag-toggle:hover {
  background: #eef5fb;
}
.assistant-rag-chevron {
  width: 16px;
  height: 16px;
  color: #8a9bab;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}
.assistant-rag-chevron.is-open {
  transform: rotate(180deg);
}
.assistant-rag {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 0 10px 10px;
  max-height: 120px;
  overflow-y: auto;
}
.assistant-rag-chip {
  font-size: 11px;
  padding: 4px 9px;
  border-radius: 999px;
  background: #eef5fb;
  color: #3d6f96;
  border: 1px solid #d5e6f4;
}
.assistant-rag-mode {
  margin: 2px 0 0;
  width: 100%;
  font-size: 10px;
  color: #8a9bab;
}
.assistant-rag-collapse-enter-active,
.assistant-rag-collapse-leave-active {
  transition: opacity 0.18s ease, max-height 0.22s ease;
  overflow: hidden;
}
.assistant-rag-collapse-enter-from,
.assistant-rag-collapse-leave-to {
  opacity: 0;
  max-height: 0;
}
.assistant-rag-collapse-enter-to,
.assistant-rag-collapse-leave-from {
  max-height: 120px;
}
.assistant-suggestions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 0 14px 10px;
}
.suggest-btn {
  text-align: left;
  border: 1px dashed #c5d9ea;
  border-radius: 8px;
  background: #f8fbfe;
  color: #3d6f96;
  font-size: 12px;
  padding: 8px 10px;
  cursor: pointer;
  transition: background 0.15s;
}
.suggest-btn:hover:not(:disabled) {
  background: #edf5fc;
}
.suggest-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.assistant-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px 14px 14px;
  border-top: 1px solid #eef3f8;
  background: #fafcfe;
}
.assistant-mini {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 3000;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  max-width: min(320px, calc(100vw - 32px));
  padding: 10px 14px;
  border: 1px solid #c5d9ea;
  border-radius: 999px;
  background: #fff;
  box-shadow: 0 8px 28px rgba(43, 88, 118, 0.16);
  cursor: pointer;
  color: #2b5876;
  transition: transform 0.2s, box-shadow 0.2s;
}
.assistant-mini:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(43, 88, 118, 0.2);
}
.assistant-mini-icon {
  font-size: 14px;
  color: #4a8fc9;
}
.assistant-mini-title {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.assistant-mini-badge {
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  background: #4a8fc9;
  color: #fff;
  font-size: 11px;
  line-height: 18px;
  text-align: center;
}
.assistant-mini-chevron {
  width: 18px;
  height: 18px;
  color: #8a9bab;
  flex-shrink: 0;
}
.assistant-panel-enter-active,
.assistant-panel-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}
.assistant-panel-enter-from,
.assistant-panel-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.97);
}
.assistant-fade-enter-active,
.assistant-fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.assistant-fade-enter-from,
.assistant-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
