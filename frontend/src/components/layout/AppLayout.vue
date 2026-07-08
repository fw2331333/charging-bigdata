<template>

  <div ref="rootRef" class="now-wrapper">

    <aside class="now-sidebar gsap-sidebar" data-color="blue">

      <div class="logo gsap-logo">

        <a href="https://www.neusoft.com" target="_blank" rel="noopener" class="logo-mini">Neu</a>

        <span class="logo-normal">{{ t('nav.logo') }}</span>

      </div>

      <nav class="now-nav-sections">

        <div v-for="section in navSections" :key="section.titleKey" class="nav-section">

          <p class="nav-section-title">{{ section.title }}</p>

          <ul class="now-nav">

            <li

              v-for="item in section.items"

              :key="item.path"

              class="gsap-nav-item"

              :class="{ active: isActive(item.path) }"

            >

              <RouterLink :to="item.path">

                <NavIcon :name="item.icon" />

                <span>{{ item.label }}</span>

              </RouterLink>

            </li>

          </ul>

        </div>

      </nav>

    </aside>



    <div class="now-main-panel">

      <nav class="now-navbar gsap-navbar">

        <a class="now-navbar-brand" href="https://www.neuedu.com" target="_blank" rel="noopener">

          NEUEDU.COM

        </a>

        <NavbarTools />

      </nav>



      <div v-if="!hidePanelHeader" class="now-panel-header gsap-panel-header">

        <div class="header text-center">

          <h2 class="title gsap-panel-title">{{ t('nav.panelTitle') }}</h2>

          <p class="category gsap-panel-sub">{{ t('nav.panelSubtitle') }}</p>

        </div>

      </div>



      <main ref="contentRef" class="now-content">
        <RouterView v-slot="{ Component, route: viewRoute }">
          <KeepAlive :max="8">
            <component
              :is="Component"
              v-if="viewRoute.meta.keepAlive && Component"
              :key="viewRoute.name"
            />
          </KeepAlive>
          <component
            :is="Component"
            v-if="!viewRoute.meta.keepAlive && Component"
            :key="viewRoute.fullPath"
          />
        </RouterView>
      </main>



      <footer class="now-footer gsap-footer">

        <nav>

          <ul>

            <li><a href="#">neu</a></li>

            <li><a href="#">About Us</a></li>

            <li><a href="#">Blog</a></li>

          </ul>

        </nav>

        <div class="copyright">

          {{ t('nav.footer', { year }) }}

        </div>

      </footer>

    </div>
  </div>
</template>



<script setup lang="ts">

import { computed, nextTick, ref, watch } from 'vue'

import { useRoute } from 'vue-router'

import { NAV_SECTION_DEFS } from '@/config/nav'

import NavIcon from '@/components/layout/NavIcon.vue'

import NavbarTools from '@/components/layout/NavbarTools.vue'

import { useLocale } from '@/composables/useLocale'

import { gsap, prefersReducedMotion, useGsap } from '@/composables/useGsap'



const route = useRoute()
const { t } = useLocale()

const navSections = computed(() =>
  NAV_SECTION_DEFS.map((section) => ({
    titleKey: section.titleKey,
    title: t(section.titleKey),
    items: section.items.map((item) => ({
      ...item,
      label: t(item.labelKey),
    })),
  })),
)

const hidePanelHeader = computed(() => Boolean(route.meta.hidePanelHeader))

const year = new Date().getFullYear()

const rootRef = ref<HTMLElement | null>(null)

const contentRef = ref<HTMLElement | null>(null)



function isActive(path: string): boolean {

  if (path === '/') return route.path === '/'

  return route.path === path || route.path.startsWith(path + '/')

}



useGsap(() => {

  const tl = gsap.timeline({ defaults: { ease: 'power2.out' } })

  tl.from('.gsap-sidebar', { x: -32, opacity: 0, duration: 0.55 })

    .from('.gsap-logo', { y: -12, opacity: 0, duration: 0.4 }, '-=0.35')

    .from('.gsap-nav-item', { x: -16, opacity: 0, duration: 0.38, stagger: 0.03 }, '-=0.2')

    .from('.gsap-navbar', { y: -10, opacity: 0, duration: 0.35 }, '-=0.45')

    .from('.gsap-panel-title', { y: 22, opacity: 0, duration: 0.5 }, '-=0.25')

    .from('.gsap-panel-sub', { y: 14, opacity: 0, duration: 0.45 }, '-=0.35')

    .from('.gsap-footer', { opacity: 0, duration: 0.35 }, '-=0.1')

}, rootRef)



function animatePageEnter() {

  if (prefersReducedMotion()) return

  const card = contentRef.value?.querySelector('.now-card')

  if (!card) return

  gsap.fromTo(card, { y: 28, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: 'power2.out' })

}



watch(() => route.path, async () => {

  await nextTick()

  animatePageEnter()

})



watch(

  contentRef,

  async (el) => {

    if (!el) return

    await nextTick()

    animatePageEnter()

  },

  { flush: 'post' },

)

</script>

