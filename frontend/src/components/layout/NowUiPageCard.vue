<template>

  <div ref="cardRef" class="now-card">

    <div class="now-card-body">

      <h4 v-if="pageTitle" class="now-card-title gsap-card-title">

        {{ pageTitle }}

        <span v-if="pageSubtitle" class="category">{{ pageSubtitle }}</span>

      </h4>

      <p v-if="sectionHint" class="now-section-subtitle gsap-card-sub">{{ sectionHint }}</p>

      <div class="gsap-card-slot">

        <slot />

      </div>

    </div>

  </div>

</template>



<script setup lang="ts">

import { ref } from 'vue'

import { gsap, useGsap } from '@/composables/useGsap'



defineProps<{

  pageTitle?: string

  pageSubtitle?: string

  sectionHint?: string

}>()



const cardRef = ref<HTMLElement | null>(null)



/** 图表页：标题 + 内容区 scroll 进入 */

useGsap(() => {

  gsap.from('.gsap-card-title', { y: 16, opacity: 0, duration: 0.45, ease: 'power2.out' })

  gsap.from('.gsap-card-sub', { y: 12, opacity: 0, duration: 0.4, delay: 0.06, ease: 'power2.out' })



  gsap.utils.toArray<HTMLElement>('.gsap-chart-block').forEach((el) => {

    gsap.from(el, {

      scrollTrigger: {

        trigger: el,

        start: 'top 88%',

        toggleActions: 'play none none reverse',

      },

      y: 36,

      opacity: 0,

      duration: 0.55,

      ease: 'power2.out',

    })

  })

}, cardRef)

</script>


