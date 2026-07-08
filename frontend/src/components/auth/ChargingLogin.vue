<template>
  <div ref="rootRef" class="login-page">
    <div class="login-bg" aria-hidden>
      <div class="login-grid" />
      <div class="login-glow login-glow--a" />
      <div class="login-glow login-glow--b" />
    </div>

    <div ref="panelRef" class="login-panel">
      <header class="login-header">
        <div class="login-logo">Neu</div>
        <div>
          <h1 class="login-title">{{ t('login.title') }}</h1>
          <p class="login-subtitle">{{ t('login.subtitle') }}</p>
        </div>
      </header>

      <form class="login-form" @submit.prevent="handleSubmit">
        <div class="login-field">
          <label class="login-label">{{ t('login.email') }}</label>
          <input
            v-model="emailModel"
            class="login-input"
            type="email"
            :placeholder="t('login.emailPlaceholder')"
            required
            autocomplete="email"
            :disabled="loading || exiting"
          />
        </div>
        <div class="login-field">
          <label class="login-label">{{ t('login.password') }}</label>
          <input
            v-model="passwordModel"
            class="login-input"
            type="password"
            :placeholder="t('login.passwordPlaceholder')"
            required
            autocomplete="current-password"
            :disabled="loading || exiting"
          />
        </div>
        <p v-if="infoMessage" class="login-info">{{ infoMessage }}</p>
        <p v-if="error" class="login-error">{{ error }}</p>
        <button
          v-if="needsVerify"
          type="button"
          class="login-resend"
          :disabled="resendLoading || loading || exiting"
          @click="emit('resend')"
        >
          {{ resendLoading ? t('auth.resending') : t('auth.resend') }}
        </button>
        <button type="submit" class="login-submit" :disabled="loading || exiting">
          {{ loading ? t('login.submitting') : exiting ? t('login.entering') : t('login.submit') }}
        </button>
        <div class="login-links">
          <RouterLink class="login-link" to="/forgot-password">{{ t('auth.forgotPassword') }}</RouterLink>
          <RouterLink class="login-link" to="/register">{{ t('auth.register') }}</RouterLink>
        </div>
      </form>
      <p class="login-foot">{{ t('login.demoAccount') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { gsap, prefersReducedMotion } from '@/lib/gsap'
import { useLocale } from '@/composables/useLocale'

const { t } = useLocale()

const props = defineProps<{
  email: string
  password: string
  infoMessage?: string
  error?: string
  loading?: boolean
  needsVerify?: boolean
  resendLoading?: boolean
}>()

const emit = defineEmits<{
  'update:email': [value: string]
  'update:password': [value: string]
  submit: []
  resend: []
  openComplete: []
}>()

const rootRef = ref<HTMLElement | null>(null)
const panelRef = ref<HTMLElement | null>(null)
const exiting = ref(false)

let ctx: gsap.Context | null = null

const emailModel = computed({
  get: () => props.email,
  set: (v) => emit('update:email', v),
})

const passwordModel = computed({
  get: () => props.password,
  set: (v) => emit('update:password', v),
})

function playExit() {
  if (prefersReducedMotion()) {
    emit('openComplete')
    return
  }

  exiting.value = true
  gsap.timeline({ onComplete: () => emit('openComplete') })
    .to(panelRef.value, { autoAlpha: 0, y: -12, scale: 0.98, duration: 0.35, ease: 'power2.in' })
    .to(rootRef.value, { autoAlpha: 0, duration: 0.25 }, 0.1)
}

function handleSubmit() {
  if (exiting.value) return
  emit('submit')
}

onMounted(() => {
  if (prefersReducedMotion() || !panelRef.value) return

  const fields = panelRef.value.querySelectorAll(
    '.login-field, .login-info, .login-error, .login-resend, .login-submit, .login-links, .login-foot',
  )

  ctx = gsap.context(() => {
    gsap.set(panelRef.value, { autoAlpha: 0, y: 24, scale: 0.97 })
    gsap.set(fields, { autoAlpha: 0, y: 12 })

    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
    tl.to(panelRef.value, { autoAlpha: 1, y: 0, scale: 1, duration: 0.55 })
      .to(fields, { autoAlpha: 1, y: 0, duration: 0.38, stagger: 0.06 }, 0.2)
  }, rootRef.value ?? undefined)
})

onUnmounted(() => {
  ctx?.revert()
})

defineExpose({ playExit })
</script>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  background: #eef3f8;
}

.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.login-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(94, 159, 212, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(94, 159, 212, 0.06) 1px, transparent 1px);
  background-size: 32px 32px;
}

.login-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: 0.4;
}

.login-glow--a {
  width: 320px;
  height: 320px;
  top: 12%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(94, 159, 212, 0.2);
}

.login-glow--b {
  width: 260px;
  height: 260px;
  bottom: 10%;
  right: 15%;
  background: rgba(61, 126, 184, 0.14);
}

.login-panel {
  position: relative;
  z-index: 1;
  width: min(400px, 100%);
  border-radius: 14px;
  background: #fff;
  border: 1px solid #e8f0f6;
  box-shadow: var(--neu-card-shadow, 0 1px 20px rgba(0, 0, 0, 0.08));
  padding: 28px 26px 24px;
}

.login-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 22px;
  padding-bottom: 18px;
  border-bottom: 1px solid #eef3f8;
}

.login-logo {
  width: 44px;
  height: 44px;
  border-radius: 11px;
  background: linear-gradient(135deg, #5e9fd4, #3d7eb8);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(61, 126, 184, 0.28);
}

.login-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2b5876;
}

.login-subtitle {
  margin: 3px 0 0;
  font-size: 12px;
  color: #9a9a9a;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.login-label {
  display: block;
  margin-bottom: 5px;
  font-size: 13px;
  color: #5a7a94;
}

.login-input {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #dce8f2;
  border-radius: 9px;
  background: #f6fafd;
  padding: 10px 14px;
  font-size: 14px;
  color: #2c2c2c;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.login-input:focus {
  outline: none;
  border-color: #4a8fc9;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(94, 159, 212, 0.22);
}

.login-input:disabled {
  opacity: 0.6;
}

.login-info {
  margin: 0;
  padding: 9px 12px;
  border-radius: 9px;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  color: #2b5876;
  font-size: 13px;
}

.login-error {
  margin: 0;
  padding: 9px 12px;
  border-radius: 9px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  font-size: 13px;
}

.login-submit {
  width: 100%;
  border: none;
  border-radius: 9px;
  padding: 11px 16px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  background: linear-gradient(135deg, #2d6a9f, #4a8fc8);
  box-shadow: 0 8px 22px rgba(45, 106, 159, 0.28);
  transition: transform 0.15s;
}

.login-submit:hover:not(:disabled) {
  transform: translateY(-1px);
}

.login-submit:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.login-resend {
  width: 100%;
  border: 1px solid #c5d9ea;
  border-radius: 9px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  color: #2d6a9f;
  background: #f8fbfe;
  cursor: pointer;
  transition: background 0.15s;
}
.login-resend:hover:not(:disabled) {
  background: #eef5fb;
}
.login-resend:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.login-links {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
}
.login-link {
  color: #3d7ab8;
  text-decoration: none;
  font-weight: 500;
}
.login-link:hover {
  text-decoration: underline;
}
.login-foot {
  margin: 16px 0 0;
  text-align: center;
  font-size: 12px;
  color: #9a9a9a;
}
</style>
