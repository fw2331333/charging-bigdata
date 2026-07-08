<template>
  <ChargingLogin
    ref="loginRef"
    v-model:email="email"
    v-model:password="password"
    :info-message="infoMessage"
    :error="error"
    :loading="loading"
    :needs-verify="needsVerify"
    :resend-loading="resendLoading"
    @submit="submit"
    @resend="resend"
    @open-complete="onOpenComplete"
  />
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ChargingLogin from '@/components/auth/ChargingLogin.vue'
import { resendVerificationApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { useLocale } from '@/composables/useLocale'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { t } = useLocale()

const loginRef = ref<InstanceType<typeof ChargingLogin> | null>(null)
const email = ref('')
const password = ref('')
const infoMessage = ref('')
const error = ref('')
const loading = ref(false)
const needsVerify = ref(false)
const resendLoading = ref(false)

onMounted(() => {
  if (auth.isLoggedIn) {
    void router.replace((route.query.redirect as string) || '/')
    return
  }
  const preset = route.query.email
  if (typeof preset === 'string' && preset) {
    email.value = preset
  }
  if (route.query.verified === '1') {
    infoMessage.value = t('login.verified')
    window.setTimeout(() => {
      infoMessage.value = ''
    }, 5000)
  }
})

async function submit() {
  loading.value = true
  error.value = ''
  needsVerify.value = false
  const result = await auth.login(email.value.trim(), password.value)
  loading.value = false
  if (result) {
    error.value = result.message
    needsVerify.value = result.status === 403
    return
  }
  loginRef.value?.playExit()
}

async function resend() {
  resendLoading.value = true
  error.value = ''
  try {
    const res = await resendVerificationApi(email.value.trim())
    infoMessage.value = res.message
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    error.value = detail ? String(detail) : t('auth.resendFailed')
  } finally {
    resendLoading.value = false
  }
}

function onOpenComplete() {
  const redirect = (route.query.redirect as string) || auth.pendingRoute || '/'
  auth.clearPendingRoute()
  void router.replace(redirect)
}
</script>
