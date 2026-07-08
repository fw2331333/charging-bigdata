<template>
  <div ref="bannerRef" class="four-s-banner">
    <div class="four-s-bg">
      <div class="four-s-grid" />
      <div class="cube cube-a gsap-cube" />
      <div class="cube cube-b gsap-cube" />
      <div class="cube cube-c gsap-cube" />
      <div class="wire-cube gsap-wire">
        <span class="wire-label wire-4s">4S</span>
      </div>
      <span class="float-label label-daas gsap-label">DaaS</span>
      <span class="float-label label-caas gsap-label">CaaS</span>
    </div>
    <div class="four-s-copy gsap-copy">
      <p class="four-s-title">4S产品服务体系赋能院校高质量发展</p>
      <p class="four-s-sub">
        The 4S product and service system empowers the high-quality development of universities
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { gsap, useGsap } from '@/composables/useGsap'

const bannerRef = ref<HTMLElement | null>(null)

useGsap(() => {
  const tl = gsap.timeline({ defaults: { ease: 'power2.out' } })
  tl.from('.gsap-copy', { x: -24, opacity: 0, duration: 0.55 })
    .from('.gsap-wire', { scale: 0.85, opacity: 0, duration: 0.5 }, '-=0.35')
    .from('.gsap-cube', { y: 20, opacity: 0, duration: 0.45, stagger: 0.1 }, '-=0.4')
    .from('.gsap-label', { y: -12, opacity: 0, duration: 0.4, stagger: 0.12 }, '-=0.35')

  gsap.to('.cube-a', { y: -6, duration: 2.4, repeat: -1, yoyo: true, ease: 'sine.inOut' })
  gsap.to('.cube-b', { y: 8, duration: 2.8, repeat: -1, yoyo: true, ease: 'sine.inOut', delay: 0.3 })
  gsap.to('.cube-c', { y: -4, duration: 2.2, repeat: -1, yoyo: true, ease: 'sine.inOut', delay: 0.6 })
  gsap.to('.wire-cube', { rotateY: 12, duration: 3, repeat: -1, yoyo: true, ease: 'sine.inOut' })
}, bannerRef)
</script>

<style scoped>
.four-s-banner {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  min-height: 200px;
  background: linear-gradient(135deg, #f0f7fd 0%, #e3f0fa 45%, #f8fbfe 100%);
  border: 1px solid #d4e6f4;
  box-shadow: 0 8px 28px rgba(61, 126, 184, 0.1);
}

.four-s-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.four-s-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(94, 159, 212, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(94, 159, 212, 0.08) 1px, transparent 1px);
  background-size: 28px 28px;
  mask-image: linear-gradient(90deg, transparent, #000 30%, #000 70%, transparent);
}

.four-s-copy {
  position: relative;
  z-index: 2;
  max-width: 58%;
  padding: 36px 32px;
}

.four-s-title {
  margin: 0 0 10px;
  font-size: 22px;
  font-weight: 700;
  color: #1a3a52;
  line-height: 1.35;
}

.four-s-sub {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #3d6a8a;
  line-height: 1.5;
}

.cube {
  position: absolute;
  border-radius: 4px;
  background: linear-gradient(145deg, #5e9fd4, #3d7eb8);
  box-shadow: 0 6px 16px rgba(61, 126, 184, 0.35);
}

.cube-a {
  width: 28px;
  height: 28px;
  right: 28%;
  top: 22%;
  transform: rotate(12deg);
}

.cube-b {
  width: 18px;
  height: 18px;
  right: 18%;
  top: 48%;
  opacity: 0.85;
}

.cube-c {
  width: 22px;
  height: 22px;
  right: 34%;
  bottom: 18%;
  opacity: 0.9;
}

.wire-cube {
  position: absolute;
  right: 10%;
  top: 50%;
  transform: translateY(-50%);
  width: 88px;
  height: 88px;
  border: 2px solid rgba(94, 159, 212, 0.55);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 24px rgba(94, 159, 212, 0.15);
}

.wire-label {
  font-size: 36px;
  font-weight: 800;
  color: rgba(61, 126, 184, 0.35);
  letter-spacing: 0.05em;
}

.float-label {
  position: absolute;
  font-size: 15px;
  font-weight: 700;
  color: #3d7eb8;
  text-shadow: 0 1px 0 #fff;
}

.label-daas {
  right: 22%;
  top: 16%;
}

.label-caas {
  right: 14%;
  bottom: 14%;
}

@media (max-width: 768px) {
  .four-s-copy {
    max-width: 100%;
    padding: 24px 20px;
  }
  .four-s-title {
    font-size: 18px;
  }
  .wire-cube,
  .cube,
  .float-label {
    opacity: 0.65;
    transform: scale(0.85);
  }
}
</style>
