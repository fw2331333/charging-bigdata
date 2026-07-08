<template>
  <div class="profile-page">
    <header class="profile-header">
      <h1 class="profile-title">{{ t('profile.title') }}</h1>
      <p class="profile-sub">{{ t('profile.subtitle') }}</p>
    </header>

    <el-alert
      v-if="isDemoUser"
      type="info"
      :closable="false"
      show-icon
      class="profile-alert"
      :title="t('profile.demoUserHint')"
    />

    <div class="profile-grid">
      <section class="profile-card">
        <h2 class="card-title">{{ t('profile.accountSection') }}</h2>
        <el-form label-position="top" @submit.prevent="saveUsername">
          <el-form-item :label="t('login.email')">
            <el-input :model-value="auth.user?.email ?? '—'" disabled />
          </el-form-item>
          <el-form-item :label="t('auth.username')">
            <el-input
              v-model="username"
              :placeholder="t('auth.usernamePlaceholder')"
              maxlength="50"
              :disabled="isAdmin || isDemoUser || usernameLoading"
            />
          </el-form-item>
          <p v-if="isAdmin" class="field-hint">{{ t('profile.adminNameLocked') }}</p>
          <el-button
            v-if="!isAdmin"
            type="primary"
            :loading="usernameLoading"
            :disabled="isDemoUser || !username.trim()"
            @click="saveUsername"
          >
            {{ t('profile.saveUsername') }}
          </el-button>
        </el-form>
      </section>

      <section class="profile-card">
        <h2 class="card-title">{{ t('profile.passwordSection') }}</h2>
        <p class="card-hint">{{ t('profile.passwordHint') }}</p>

        <p v-if="codeMessage" class="code-msg">{{ codeMessage }}</p>

        <el-form label-position="top" class="password-form" @submit.prevent="savePassword">
          <el-form-item v-if="codePending" :label="t('profile.verifyCode')">
            <el-input
              v-model="code"
              :placeholder="t('profile.verifyCodePlaceholder')"
              maxlength="6"
              :disabled="isDemoUser || passwordLoading"
            />
          </el-form-item>
          <el-form-item :label="t('auth.newPassword')">
            <el-input
              v-model="newPassword"
              type="password"
              show-password
              :placeholder="t('auth.passwordMin')"
              :disabled="isDemoUser || passwordLoading"
            />
          </el-form-item>
          <el-form-item :label="t('auth.confirmPassword')">
            <el-input
              v-model="confirmPassword"
              type="password"
              show-password
              :placeholder="t('auth.confirmPasswordPlaceholder')"
              :disabled="isDemoUser || passwordLoading"
            />
          </el-form-item>
          <el-button
            type="primary"
            :loading="passwordLoading"
            :disabled="isDemoUser || !canSubmitPassword"
            @click="savePassword"
          >
            {{ submitPasswordLabel }}
          </el-button>
        </el-form>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  changeProfilePasswordApi,
  sendProfileCodeApi,
  updateProfileUsernameApi,
} from '@/api/auth'
import { useLocale } from '@/composables/useLocale'
import { useAuthStore } from '@/stores/auth'

const { t } = useLocale()
const auth = useAuthStore()

const isDemoUser = computed(() => auth.user?.email === 'user@example.com')
const isAdmin = computed(() => auth.user?.role === 'admin')

const username = ref(auth.user?.username ?? '')
const code = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const codeMessage = ref('')
const codePending = ref(false)
const usernameLoading = ref(false)
const passwordLoading = ref(false)

watch(
  () => auth.user?.username,
  (v) => {
    if (v) username.value = v
  },
)

const passwordsValid = computed(
  () => newPassword.value.length >= 6 && confirmPassword.value.length >= 6,
)

const canSubmitPassword = computed(() => {
  if (!passwordsValid.value) return false
  if (codePending.value) return code.value.trim().length >= 4
  return true
})

const submitPasswordLabel = computed(() => {
  if (passwordLoading.value) return t('auth.submitting')
  if (codePending.value) return t('profile.savePassword')
  return t('profile.sendCodeAndContinue')
})

async function requestCode() {
  const res = await sendProfileCodeApi()
  codeMessage.value = res.message
  codePending.value = true
  ElMessage.success(t('profile.codeSent'))
}

async function saveUsername() {
  const trimmed = username.value.trim()
  if (!trimmed || trimmed === auth.user?.username) return
  usernameLoading.value = true
  try {
    const res = await updateProfileUsernameApi(trimmed)
    await auth.applyProfileUpdate(res)
    ElMessage.success(t('profile.usernameUpdated'))
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    ElMessage.error(detail ? String(detail) : t('profile.updateFailed'))
  } finally {
    usernameLoading.value = false
  }
}

async function savePassword() {
  if (newPassword.value !== confirmPassword.value) {
    ElMessage.warning(t('auth.passwordMismatch'))
    return
  }
  passwordLoading.value = true
  try {
    if (!codePending.value) {
      await requestCode()
      return
    }
    const res = await changeProfilePasswordApi(code.value.trim(), newPassword.value)
    await auth.applyProfileUpdate(res)
    code.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    codeMessage.value = ''
    codePending.value = false
    ElMessage.success(t('profile.passwordUpdated'))
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    ElMessage.error(detail ? String(detail) : t('profile.updateFailed'))
  } finally {
    passwordLoading.value = false
  }
}
</script>

<style scoped>
.profile-page {
  max-width: 920px;
  margin: 0 auto;
  padding: 8px 4px 24px;
}
.profile-header {
  margin-bottom: 20px;
}
.profile-title {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #2b5876;
}
.profile-sub {
  margin: 6px 0 0;
  font-size: 13px;
  color: #8a9bab;
}
.profile-alert {
  margin-bottom: 16px;
}
.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}
.profile-card {
  padding: 20px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #e8f0f6;
  box-shadow: 0 1px 12px rgba(43, 88, 118, 0.06);
}
.card-title {
  margin: 0 0 14px;
  font-size: 16px;
  font-weight: 600;
  color: #2b5876;
}
.card-hint,
.field-hint {
  margin: -6px 0 14px;
  font-size: 12px;
  color: #8a9bab;
  line-height: 1.5;
}
.code-msg {
  margin: 0 0 10px;
  font-size: 13px;
  color: #2b5876;
  line-height: 1.45;
}
.password-form {
  margin-top: 4px;
}
</style>
