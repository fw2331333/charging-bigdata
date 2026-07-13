<template>
  <NowUiPageCard
    :page-title="t('nav.sectionTitle')"
    :page-subtitle="t('nav.sectionHint')"
  >
    <div ref="homeRef" class="home-root">
      <FourSBanner />

      <p class="now-intro-text gsap-intro">
        {{ t('home.intro') }}
      </p>

      <div class="home-actions gsap-actions">
        <button type="button" class="bi-entry-btn" @click="goBiEntry">
          <span class="btn-icon">◫</span>
          <span class="btn-text">
            <strong>{{ t('nav.biEntry') }}</strong>
          </span>
        </button>
        <a
          class="bi-entry-btn bi-entry-secondary"
          :href="datartUrl"
          target="_blank"
          rel="noopener noreferrer"
          @click="onDatartClick"
        >
          <span class="btn-icon">↗</span>
          <span class="btn-text">
            <strong>{{ t('home.datartTitle') }}</strong>
          </span>
        </a>
      </div>
    </div>
  </NowUiPageCard>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import FourSBanner from '@/components/home/FourSBanner.vue'
import NowUiPageCard from '@/components/layout/NowUiPageCard.vue'
import { getDatartOpenUrl, isDatartReachable } from '@/config/datart'
import { BI_ENTRY } from '@/config/nav'
import { useLocale } from '@/composables/useLocale'
import { useAuthStore } from '@/stores/auth'
import { gsap, useGsap } from '@/composables/useGsap'

const homeRef = ref<HTMLElement | null>(null)
const router = useRouter()
const auth = useAuthStore()
const { t } = useLocale()
const datartUrl = computed(() => getDatartOpenUrl())
const datartReachable = ref<boolean | null>(null)

onMounted(() => {
  void isDatartReachable().then((ok) => {
    datartReachable.value = ok
  })
})

function goBiEntry() {
  if (!auth.isLoggedIn) {
    void router.push({ name: 'login', query: { redirect: BI_ENTRY.path } })
    return
  }
  void router.push(BI_ENTRY.path)
}

function onDatartClick(e: MouseEvent) {
  if (datartReachable.value === false) {
    e.preventDefault()
    ElMessage.warning({
      message:
        `Datart 未启动（${datartUrl.value} 无响应）。服务器请执行：docker compose -f docker-compose.yml -f docker-compose.datart.yml up -d datart，再运行 bash scripts/fix-datart-all.sh`,
      duration: 10000,
      showClose: true,
    })
  }
}

useGsap(() => {
  const tl = gsap.timeline({ defaults: { ease: 'power2.out' }, delay: 0.1 })
  tl.from('.gsap-intro', { y: 18, opacity: 0, duration: 0.5 })
    .from('.gsap-actions', { y: 16, opacity: 0, duration: 0.45 }, '-=0.25')
}, homeRef)
</script>

<style scoped>
.now-intro-text {
  max-width: 900px;
  margin: 20px auto 0;
}
.home-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-top: 28px;
}
.bi-entry-btn {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 28px;
  width: min(520px, 100%);
  border: 1px solid #dce8f2;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8fbfe, #eef5fb);
  cursor: pointer;
  text-align: left;
  text-decoration: none;
  color: inherit;
  transition: transform 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
}
.bi-entry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(45, 106, 159, 0.12);
}
.bi-entry-secondary {
  background: #fff;
}
.btn-icon {
  font-size: 22px;
  color: #4a8fc9;
}
.btn-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.btn-text strong {
  font-size: 15px;
  color: #2b5876;
}
.btn-text small {
  font-size: 12px;
  color: #8a9bab;
}
</style>
