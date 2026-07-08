<template>
  <div class="auth-page">
    <div class="auth-bg" aria-hidden>
      <div class="auth-grid" />
      <div class="auth-glow auth-glow--a" />
      <div class="auth-glow auth-glow--b" />
    </div>

    <div class="auth-panel">
      <header class="auth-header">
        <div class="auth-logo">Neu</div>
        <div>
          <h1 class="auth-title">{{ title }}</h1>
          <p v-if="subtitle" class="auth-subtitle">{{ subtitle }}</p>
        </div>
      </header>

      <slot />

      <footer v-if="$slots.footer" class="auth-footer">
        <slot name="footer" />
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<style scoped>
.auth-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  background: #eef3f8;
}
.auth-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.auth-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(94, 159, 212, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(94, 159, 212, 0.06) 1px, transparent 1px);
  background-size: 32px 32px;
}
.auth-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: 0.4;
}
.auth-glow--a {
  width: 320px;
  height: 320px;
  top: 12%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(94, 159, 212, 0.2);
}
.auth-glow--b {
  width: 260px;
  height: 260px;
  bottom: 10%;
  right: 15%;
  background: rgba(61, 126, 184, 0.14);
}
.auth-panel {
  position: relative;
  z-index: 1;
  width: min(400px, 100%);
  border-radius: 14px;
  background: #fff;
  border: 1px solid #e8f0f6;
  box-shadow: 0 1px 20px rgba(0, 0, 0, 0.08);
  padding: 28px 26px 24px;
}
.auth-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 22px;
  padding-bottom: 18px;
  border-bottom: 1px solid #eef3f8;
}
.auth-logo {
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
.auth-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2b5876;
}
.auth-subtitle {
  margin: 3px 0 0;
  font-size: 12px;
  color: #9a9a9a;
}
.auth-footer {
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid #eef3f8;
  text-align: center;
  font-size: 13px;
  color: #6b8aa3;
}
</style>

<style>
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.auth-field-label {
  display: block;
  margin-bottom: 5px;
  font-size: 13px;
  color: #5a7a94;
}
.auth-input {
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
.auth-input:focus {
  outline: none;
  border-color: #4a8fc9;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(94, 159, 212, 0.22);
}
.auth-input:disabled {
  opacity: 0.6;
}
.auth-hint {
  margin: -6px 0 0;
  font-size: 12px;
  color: #8a9bab;
  line-height: 1.45;
}
.auth-info {
  margin: 0;
  padding: 9px 12px;
  border-radius: 9px;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  color: #2b5876;
  font-size: 13px;
}
.auth-info.is-warn {
  background: #fffbeb;
  border-color: #fde68a;
  color: #92400e;
}
.auth-error {
  margin: 0;
  padding: 9px 12px;
  border-radius: 9px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  font-size: 13px;
}
.auth-submit {
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
  transition: transform 0.15s, opacity 0.15s;
}
.auth-submit:hover:not(:disabled) {
  transform: translateY(-1px);
}
.auth-submit:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.auth-btn-secondary {
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
.auth-btn-secondary:hover:not(:disabled) {
  background: #eef5fb;
}
.auth-btn-secondary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.auth-link {
  color: #3d7ab8;
  text-decoration: none;
  font-weight: 500;
}
.auth-link:hover {
  text-decoration: underline;
}
</style>
