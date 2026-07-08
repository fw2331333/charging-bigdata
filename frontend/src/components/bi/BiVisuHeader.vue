<template>
  <header class="bi-visu-header">
    <a class="bi-visu-logo" href="https://www.neuedu.com" target="_blank" rel="noopener">
      <span class="logo-en">Neuedu</span>
      <span class="logo-cn">东软教育</span>
    </a>
    <h1 class="bi-visu-title">{{ BI_DASHBOARD_TITLE }}</h1>
    <div class="bi-visu-logo-spacer" aria-hidden="true" />
  </header>
</template>

<script setup lang="ts">
import { BI_DASHBOARD_TITLE } from '@/config/assets'
</script>

<style scoped>
.bi-visu-header {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.bi-visu-logo {
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-decoration: none;
  justify-self: start;
}
.logo-en {
  font-size: 22px;
  font-weight: 800;
  color: #2d6a9f;
  letter-spacing: 0.02em;
}
.logo-cn {
  font-size: 12px;
  font-weight: 600;
  color: #5a7a94;
}
.bi-visu-title {
  margin: 0;
  font-size: clamp(18px, 2.2vw, 26px);
  font-weight: 700;
  color: #1a2a3a;
  text-align: center;
  line-height: 1.3;
  white-space: nowrap;
}
.bi-visu-logo-spacer {
  width: 1px;
}
@media (max-width: 720px) {
  .bi-visu-header {
    grid-template-columns: 1fr;
    text-align: center;
  }
  .bi-visu-logo {
    justify-self: center;
  }
  .bi-visu-title {
    white-space: normal;
  }
  .bi-visu-logo-spacer {
    display: none;
  }
}
</style>
