<template>
  <AuthShell :title="pageTitle" :subtitle="emailMasked ? t('auth.accountLabel', { email: emailMasked }) : ''">
    <div v-if="status === 'loading'" class="auth-form">
      <p class="auth-hint">{{ t('auth.checkingLink') }}</p>
    </div>

    <form v-else-if="status === 'ready' || status === 'submitting'" class="auth-form" @submit.prevent="submit">
      <div>
        <label class="auth-field-label">{{ t('auth.newPassword') }}</label>
        <input
          v-model="password"
          class="auth-input"
          type="password"
          :placeholder="t('auth.passwordMin')"
          minlength="6"
          required
          autocomplete="new-password"
          :disabled="status === 'submitting'"
        />
      </div>
      <div>
        <label class="auth-field-label">{{ t('auth.confirmPassword') }}</label>
        <input
          v-model="confirm"
          class="auth-input"
          type="password"
          :placeholder="t('auth.confirmPasswordPlaceholder')"
          minlength="6"
          required
          autocomplete="new-password"
          :disabled="status === 'submitting'"
        />
      </div>
      <p v-if="message" class="auth-error">{{ message }}</p>
      <button type="submit" class="auth-submit" :disabled="status === 'submitting'">
        {{ status === 'submitting' ? t('auth.submitting') : t('auth.confirmSetPassword') }}
      </button>
    </form>

    <div v-else-if="status === 'ok'" class="auth-form">
      <p class="auth-info">{{ message }}</p>
      <button type="button" class="auth-submit" @click="goLogin">{{ t('auth.goLogin') }}</button>
    </div>

    <div v-else class="auth-form">
      <p class="auth-error">{{ message }}</p>
      <RouterLink class="auth-link" to="/forgot-password">{{ t('auth.forgotPassword') }}</RouterLink>
      <span> · </span>
      <RouterLink class="auth-link" to="/register">{{ t('auth.register') }}</RouterLink>
      <span> · </span>
      <RouterLink class="auth-link" to="/login">{{ t('auth.backLogin') }}</RouterLink>
    </div>

    <template v-if="status !== 'ok'" #footer>
      <RouterLink class="auth-link" to="/login">{{ t('auth.backLogin') }}</RouterLink>
    </template>
  </AuthShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { clearTokens, completeEmailTokenApi, inspectEmailTokenApi } from '@/api/auth'
import AuthShell from '@/components/auth/AuthShell.vue'
import { useLocale } from '@/composables/useLocale'

const { t } = useLocale()
const route = useRoute()
const router = useRouter()

const token = computed(() => String(route.query.token ?? '').trim())
const purpose = ref('')
const emailMasked = ref('')
const password = ref('')
const confirm = ref('')
const status = ref<'loading' | 'ready' | 'submitting' | 'ok' | 'error'>('loading')
const message = ref('')
const successEmail = ref('')

const pageTitle = computed(() => {
  if (purpose.value === 'reset_password') return t('auth.resetTitle')
  if (purpose.value === 'verify_email') return t('auth.setPasswordTitle')
  return t('auth.setPasswordTitle')
})

onMounted(() => {
  clearTokens()
  if (!token.value) {
    status.value = 'error'
    message.value = t('auth.invalidLink')
    return
  }
  void inspectToken()
})

async function inspectToken() {
  try {
    const res = await inspectEmailTokenApi(token.value)
    purpose.value = res.purpose
    emailMasked.value = res.email_masked
    status.value = 'ready'
  } catch (e: unknown) {
    status.value = 'error'
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    message.value = detail ? String(detail) : t('auth.invalidLink')
  }
}

async function submit() {
  if (password.value !== confirm.value) {
    message.value = t('auth.passwordMismatch')
    return
  }
  status.value = 'submitting'
  message.value = ''
  try {
    const res = await completeEmailTokenApi(token.value, password.value)
    successEmail.value = res.email
    message.value = res.message
    status.value = 'ok'
  } catch (e: unknown) {
    status.value = 'ready'
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    message.value = detail ? String(detail) : t('auth.setPasswordFailed')
  }
}

function goLogin() {
  clearTokens()
  void router.replace({
    name: 'login',
    query: { email: successEmail.value, verified: '1' },
  })
}
</script>
