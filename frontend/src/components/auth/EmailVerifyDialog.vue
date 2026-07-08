<template>
  <Teleport to="body">
    <div v-if="open" class="verify-overlay" role="dialog" aria-modal="true" @click.self="emit('close')">
      <div class="verify-dialog">
        <h2 class="verify-title">{{ t('auth.verifyTitle') }}</h2>
        <p class="auth-info" :class="{ 'is-warn': !emailSent }">{{ message }}</p>
        <p class="verify-desc">
          <template v-if="emailSent">
            {{ t('auth.verifySent', { email }) }}
          </template>
          <template v-else>
            {{ t('auth.verifyNotSent', { email }) }}
          </template>
        </p>

        <p v-if="resendMsg" class="auth-info">{{ resendMsg }}</p>
        <p v-if="resendError" class="auth-error">{{ resendError }}</p>

        <div class="verify-actions">
          <button type="button" class="auth-btn-secondary" :disabled="resendLoading" @click="resend">
            {{ resendLoading ? t('auth.resending') : t('auth.resend') }}
          </button>
          <button type="button" class="auth-submit" @click="emit('close')">{{ t('auth.gotIt') }}</button>
          <RouterLink class="verify-login-link auth-link" :to="{ name: 'login', query: { email } }" @click="emit('close')">
            {{ t('auth.goLogin') }}
          </RouterLink>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { resendVerificationApi } from '@/api/auth'
import { useLocale } from '@/composables/useLocale'

const props = defineProps<{
  open: boolean
  email: string
  message: string
  emailSent: boolean
}>()

const emit = defineEmits<{ close: [] }>()

const { t } = useLocale()
const resendMsg = ref('')
const resendError = ref('')
const resendLoading = ref(false)

async function resend() {
  resendLoading.value = true
  resendMsg.value = ''
  resendError.value = ''
  try {
    const res = await resendVerificationApi(props.email)
    resendMsg.value = res.message
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    resendError.value = detail ? String(detail) : t('auth.resendFailed')
  } finally {
    resendLoading.value = false
  }
}
</script>

<style scoped>
.verify-overlay {
  position: fixed;
  inset: 0;
  z-index: 4000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
}
.verify-dialog {
  width: min(400px, 100%);
  border-radius: 14px;
  background: #fff;
  border: 1px solid #e8f0f6;
  box-shadow: 0 16px 48px rgba(43, 88, 118, 0.2);
  padding: 24px;
}
.verify-title {
  margin: 0 0 12px;
  font-size: 17px;
  font-weight: 600;
  color: #2b5876;
}
.verify-desc {
  margin: 0 0 14px;
  font-size: 13px;
  line-height: 1.55;
  color: #5a6f82;
}
.verify-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 14px;
}
.verify-login-link {
  display: block;
  text-align: center;
  font-size: 13px;
  padding: 4px 0;
}
</style>
