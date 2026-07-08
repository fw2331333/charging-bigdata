<template>
  <svg class="nav-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
    <path v-if="name === 'app'" d="M4 4h7v7H4V4zm9 0h7v7h-7V4zM4 13h7v7H4v-7zm9 0h7v7h-7v-7z" />
    <path
      v-else-if="name === 'atom'"
      d="M12 2a2 2 0 012 2c0 .74-.4 1.39-1 1.73V7h2a2 2 0 110 4h-2v1.27c.6.34 1 .99 1 1.73a2 2 0 11-4 0c0-.74.4-1.39 1-1.73V11H9a2 2 0 110-4h2V5.73A2 2 0 0112 2zm0 14a1 1 0 100 2 1 1 0 000-2zm0-12a1 1 0 100 2 1 1 0 000-2z"
    />
    <path
      v-else-if="name === 'map'"
      d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5A2.5 2.5 0 1112 6a2.5 2.5 0 010 5.5z"
    />
    <path
      v-else-if="name === 'bell'"
      d="M12 22a2.5 2.5 0 002.45-2h-4.9A2.5 2.5 0 0012 22zm7-6V11a7 7 0 10-14 0v5l-2 2v1h18v-1l-2-2z"
    />
    <path
      v-else-if="name === 'user'"
      d="M12 12a5 5 0 100-10 5 5 0 000 10zm0 2c-5.33 0-8 2.67-8 4v2h16v-2c0-1.33-2.67-4-8-4z"
    />
    <path v-else-if="name === 'list'" d="M4 6h16v2H4V6zm0 5h16v2H4v-2zm0 5h16v2H4v-2z" />
    <path v-else-if="name === 'chart'" d="M3 13h4v8H3v-8zm7-6h4v14h-4V7zm7 3h4v11h-4V10z" />
    <path v-else d="M5 4h14v2H5V4zm0 7h14v2H5v-2zm0 7h10v2H5v-2z" />
  </svg>
</template>

<script setup lang="ts">
import type { NavItem } from '@/config/nav'

defineProps<{ name: NavItem['icon'] }>()
</script>
