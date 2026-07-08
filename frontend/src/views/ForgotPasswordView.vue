<template>
  <AuthShell :title="t('auth.forgotTitle')" :subtitle="t('auth.forgotSubtitle')">
    <div v-if="sent" class="auth-form">
      <p class="auth-info" :class="{ 'is-warn': !emailSent }">{{ message }}</p>
      <p class="auth-hint">{{ emailSent ? t('auth.forgotSentHint') : t('auth.forgotFailHint') }}</p>
      <button type="button" class="auth-btn-secondary" @click="resetForm">{{ t('auth.tryAnotherEmail') }}</button>
    </div>

    <form v-else class="auth-form" @submit.prevent="submit">
      <div>
        <label class="auth-field-label">{{ t('auth.registeredEmail') }}</label>
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
      <p v-if="error" class="auth-error">{{ error }}</p>
      <button type="submit" class="auth-submit" :disabled="loading">
        {{ loading ? t('auth.sending') : t('auth.sendEmail') }}
      </button>
    </form>

    <template #footer>
      {{ t('auth.rememberPassword') }}
      <RouterLink class="auth-link" to="/login">{{ t('auth.backLogin') }}</RouterLink>
    </template>
  </AuthShell>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { forgotPasswordApi } from '@/api/auth'
import AuthShell from '@/components/auth/AuthShell.vue'
import { useLocale } from '@/composables/useLocale'

const { t } = useLocale()

const email = ref('')
const error = ref('')
const loading = ref(false)
const sent = ref(false)
const message = ref('')
const emailSent = ref(false)

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const res = await forgotPasswordApi(email.value.trim())
    sent.value = true
    message.value = res.message
    emailSent.value = res.email_sent === true
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    error.value = detail ? String(detail) : t('auth.sendFailed')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  sent.value = false
  message.value = ''
  emailSent.value = false
}
</script>
