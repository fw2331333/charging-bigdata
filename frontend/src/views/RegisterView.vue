<template>
  <AuthShell :title="t('auth.registerTitle')" :subtitle="t('auth.registerSubtitle')">
    <form class="auth-form" @submit.prevent="submit">
      <div>
        <label class="auth-field-label">{{ t('login.email') }}</label>
        <input
          v-model="email"
          class="auth-input"
          type="email"
          :placeholder="t('login.emailPlaceholder')"
          required
          autocomplete="email"
          :disabled="loading"
        />
      </div>
      <div>
        <label class="auth-field-label">{{ t('auth.username') }}</label>
        <input
          v-model="username"
          class="auth-input"
          type="text"
          :placeholder="t('auth.usernamePlaceholder')"
          required
          minlength="2"
          maxlength="50"
          autocomplete="username"
          :disabled="loading"
        />
      </div>
      <p class="auth-hint">{{ t('auth.registerHint') }}</p>
      <p v-if="error" class="auth-error">{{ error }}</p>
      <button type="submit" class="auth-submit" :disabled="loading">
        {{ loading ? t('auth.submitting') : t('auth.register') }}
      </button>
    </form>

    <template #footer>
      {{ t('auth.hasAccount') }}
      <RouterLink class="auth-link" to="/login">{{ t('login.submit') }}</RouterLink>
    </template>

    <EmailVerifyDialog
      :open="verifyOpen"
      :email="verifyEmail"
      :message="verifyMessage"
      :email-sent="verifyEmailSent"
      @close="verifyOpen = false"
    />
  </AuthShell>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { clearTokens, registerApi } from '@/api/auth'
import AuthShell from '@/components/auth/AuthShell.vue'
import EmailVerifyDialog from '@/components/auth/EmailVerifyDialog.vue'
import { useLocale } from '@/composables/useLocale'

const { t } = useLocale()

const email = ref('')
const username = ref('')
const error = ref('')
const loading = ref(false)

const verifyOpen = ref(false)
const verifyEmail = ref('')
const verifyMessage = ref('')
const verifyEmailSent = ref(true)

async function submit() {
  loading.value = true
  error.value = ''
  try {
    clearTokens()
    const res = await registerApi(email.value.trim(), username.value.trim())
    verifyEmail.value = res.email
    verifyMessage.value = res.message
    verifyEmailSent.value = res.email_sent !== false
    verifyOpen.value = true
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    error.value = detail ? String(detail) : t('auth.registerFailed')
  } finally {
    loading.value = false
  }
}
</script>
