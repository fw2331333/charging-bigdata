<template>
  <div class="navbar-tools">
    <button
      type="button"
      class="tool-btn"
      :class="{ 'tool-btn-active': assistantUi !== 'closed' }"
      :title="assistantUi === 'closed' ? t('assistant.open') : t('assistant.expand')"
      @click="toggleAssistant"
    >
      <svg class="tool-svg" viewBox="0 0 24 24" aria-hidden="true">
        <path
          fill="currentColor"
          d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12zM7 9h2v2H7V9zm4 0h2v2h-2V9zm4 0h2v2h-2V9z"
        />
      </svg>
    </button>

    <el-dropdown trigger="click" @command="onLocale">
      <button type="button" class="tool-btn" :title="t('common.language')">
        <svg class="tool-svg" viewBox="0 0 24 24">
          <path
            fill="currentColor"
            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"
          />
        </svg>
      </button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="zh" :disabled="locale === 'zh'">{{ t('common.zh') }}</el-dropdown-item>
          <el-dropdown-item command="en" :disabled="locale === 'en'">{{ t('common.en') }}</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <el-dropdown trigger="click" @command="onUser">
      <button
        type="button"
        class="tool-btn tool-btn-user"
        :title="auth.isLoggedIn ? auth.user?.display_name : t('common.login')"
      >
        <svg class="tool-svg" viewBox="0 0 24 24">
          <path
            fill="currentColor"
            d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"
          />
        </svg>
        <span v-if="auth.isLoggedIn" class="user-label">{{ auth.user?.username }}</span>
      </button>
      <template #dropdown>
        <el-dropdown-menu>
          <template v-if="auth.isLoggedIn">
            <el-dropdown-item disabled>
              {{ auth.user?.display_name }}（{{
                auth.user?.role === 'admin' ? t('common.adminRole') : t('common.user')
              }}）
            </el-dropdown-item>
            <el-dropdown-item command="profile">{{ t('common.profile') }}</el-dropdown-item>
            <el-dropdown-item v-if="auth.isAdmin" command="admin">{{ t('common.admin') }}</el-dropdown-item>
            <el-dropdown-item divided command="logout">{{ t('common.logout') }}</el-dropdown-item>
          </template>
          <el-dropdown-item v-else command="login">{{ t('common.login') }}</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <AssistantDrawer v-model="assistantUi" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AssistantDrawer, { type AssistantUiState } from '@/components/assistant/AssistantDrawer.vue'
import { useLocale } from '@/composables/useLocale'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { t, locale, setLocale } = useLocale()
const assistantUi = ref<AssistantUiState>('closed')

function toggleAssistant() {
  if (assistantUi.value === 'closed') {
    assistantUi.value = 'open'
  } else if (assistantUi.value === 'minimized') {
    assistantUi.value = 'open'
  } else {
    assistantUi.value = 'minimized'
  }
}

function onLocale(cmd: string) {
  const next = cmd as 'zh' | 'en'
  setLocale(next)
  ElMessage.info(next === 'zh' ? t('common.localeSwitchedZh') : t('common.localeSwitchedEn'))
}

function onUser(cmd: string) {
  if (cmd === 'login') void router.push({ name: 'login', query: { redirect: route.fullPath } })
  else if (cmd === 'logout') {
    void auth.logout().then(() => {
      ElMessage.success(t('common.loggedOut'))
      void router.push({ name: 'login' })
    })
  } else if (cmd === 'profile') {
    void router.push({ name: 'profile' })
  } else if (cmd === 'admin') {
    ElMessage.info(t('common.adminHint'))
  }
}
</script>

<style scoped>
.navbar-tools {
  display: flex;
  align-items: center;
  gap: 6px;
}
.tool-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 32px;
  min-width: 32px;
  padding: 0 8px;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}
.tool-btn:hover {
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.35);
}
.tool-btn-active {
  background: rgba(255, 255, 255, 0.28);
  border-color: rgba(255, 255, 255, 0.45);
}
.tool-svg {
  width: 16px;
  height: 16px;
  display: block;
}
.user-label {
  font-size: 11px;
  max-width: 64px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
