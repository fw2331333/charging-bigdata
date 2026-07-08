import { ensureValidAccessToken, getAuthToken } from './request'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface AssistantChatRequest {
  message: string
  locale: 'zh' | 'en'
  history: ChatMessage[]
}

export interface AssistantChatResponse {
  reply: string
  mode: 'llm' | 'rule'
  data_context_included: boolean
  rag_sources: string[]
  rag_mode: 'hybrid' | 'vector' | 'lexical'
}

export interface AssistantStreamMeta {
  mode: 'llm' | 'rule'
  rag_sources: string[]
  rag_mode: AssistantChatResponse['rag_mode']
}

export interface AssistantStreamHandlers {
  onMeta: (meta: AssistantStreamMeta) => void
  onDelta: (chunk: string) => void
  onDone: () => void
  onError?: (message: string) => void
}

function parseSseBlock(block: string): { event: string; data: string } | null {
  let event = 'message'
  let data = ''
  for (const line of block.split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim()
    else if (line.startsWith('data:')) data += line.slice(5).trim()
  }
  if (!data) return null
  return { event, data }
}

export async function streamAssistantChat(
  body: AssistantChatRequest,
  handlers: AssistantStreamHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const ok = await ensureValidAccessToken()
  if (!ok) throw new Error('unauthorized')

  const token = getAuthToken()
  const res = await fetch('/api/v1/assistant/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
    signal,
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `HTTP ${res.status}`)
  }

  const reader = res.body?.getReader()
  if (!reader) throw new Error('stream unavailable')

  const decoder = new TextDecoder()
  let buffer = ''
  let finished = false
  const finish = () => {
    if (finished) return
    finished = true
    handlers.onDone()
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''

    for (const part of parts) {
      const parsed = parseSseBlock(part.trim())
      if (!parsed) continue

      let payload: Record<string, unknown>
      try {
        payload = JSON.parse(parsed.data) as Record<string, unknown>
      } catch {
        continue
      }

      if (parsed.event === 'meta') {
        handlers.onMeta({
          mode: payload.mode as AssistantStreamMeta['mode'],
          rag_sources: (payload.rag_sources as string[]) ?? [],
          rag_mode: (payload.rag_mode as AssistantStreamMeta['rag_mode']) ?? 'lexical',
        })
      } else if (parsed.event === 'delta') {
        const chunk = String(payload.content ?? '')
        if (chunk) handlers.onDelta(chunk)
      } else if (parsed.event === 'error') {
        handlers.onError?.(String(payload.message ?? 'stream error'))
      } else if (parsed.event === 'done') {
        finish()
      }
    }
  }

  finish()
}
