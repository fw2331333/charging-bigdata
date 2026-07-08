<template>
  <div
    ref="blockRef"
    class="gsap-chart-block expandable-chart-block"
    :class="{ 'is-expandable': expandable, 'is-source-hidden': expanded }"
    :role="expandable ? 'button' : undefined"
    :tabindex="expandable ? 0 : undefined"
    :aria-expanded="expandable ? expanded : undefined"
    @click="onBlockClick"
    @keydown.enter.prevent="onBlockClick"
    @keydown.space.prevent="onBlockClick"
  >
    <h6>{{ title }}</h6>
    <div class="expandable-chart-body">
      <slot />
    </div>
    <span v-if="expandable" class="expand-hint" :title="t('chart.clickToExpand')">⤢</span>
  </div>

  <Teleport to="body">
    <div
      v-if="layerVisible"
      class="chart-expand-layer"
      :class="{ 'is-interactive': expanded }"
      aria-modal="true"
      role="dialog"
      :aria-label="title"
    >
      <div ref="backdropRef" class="chart-expand-backdrop" @click="collapse" />
      <div ref="panelRef" class="chart-expand-panel" @click.stop>
        <button type="button" class="chart-expand-close" aria-label="Close" @click="collapse">×</button>
        <h6 class="chart-expand-title">{{ title }}</h6>
        <div class="chart-expand-chart">
          <MrEchart v-if="option" ref="expandedChartRef" :option="option" fill />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, onUnmounted, ref, watch } from 'vue'
import MrEchart from '@/components/bi/AsyncMrEchart'
import { useLocale } from '@/composables/useLocale'
import { animateChartCollapse, animateChartExpand } from '@/composables/useChartExpandAnimation'
import type { ChartOption } from '@/utils/mrCharts'

const props = defineProps<{
  title: string
  option?: ChartOption | null
}>()

const { t } = useLocale()

const blockRef = ref<HTMLElement | null>(null)
const backdropRef = ref<HTMLElement | null>(null)
const panelRef = ref<HTMLElement | null>(null)
const expandedChartRef = ref<InstanceType<typeof MrEchart> | null>(null)

const expanded = ref(false)
const layerVisible = ref(false)
const animating = ref(false)

const expandable = computed(() => Boolean(props.option))

function lockScroll(lock: boolean) {
  document.body.style.overflow = lock ? 'hidden' : ''
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && expanded.value) collapse()
}

function resizeCharts() {
  expandedChartRef.value?.resize?.()
  window.dispatchEvent(new Event('resize'))
}

async function expand() {
  if (!expandable.value || expanded.value || animating.value) return
  animating.value = true
  layerVisible.value = true
  expanded.value = true
  lockScroll(true)
  document.addEventListener('keydown', onKeydown)

  await nextTick()
  const source = blockRef.value
  const panel = panelRef.value
  const backdrop = backdropRef.value
  if (!source || !panel || !backdrop) {
    animating.value = false
    return
  }

  animateChartExpand(source, panel, backdrop, () => {
    animating.value = false
    resizeCharts()
  })
}

function collapse() {
  if (!expanded.value || animating.value) return
  animating.value = true

  const source = blockRef.value
  const panel = panelRef.value
  const backdrop = backdropRef.value
  if (!source || !panel || !backdrop) {
    finishCollapse()
    return
  }

  animateChartCollapse(source, panel, backdrop, finishCollapse)
}

function finishCollapse() {
  expanded.value = false
  layerVisible.value = false
  animating.value = false
  lockScroll(false)
  document.removeEventListener('keydown', onKeydown)
  resizeCharts()
}

function onBlockClick() {
  if (!expandable.value) return
  void expand()
}

watch(
  () => props.option,
  () => {
    if (expanded.value) nextTick(() => resizeCharts())
  },
)

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  lockScroll(false)
})
</script>

<style scoped>
.expandable-chart-block {
  position: relative;
  border-radius: 10px;
  transition: box-shadow 0.2s ease;
}
.expandable-chart-block.is-expandable {
  cursor: zoom-in;
}
.expandable-chart-block.is-expandable:hover {
  box-shadow: 0 8px 28px rgba(45, 106, 159, 0.12);
}
.expandable-chart-block.is-source-hidden {
  visibility: hidden;
}
.expandable-chart-body {
  min-height: 0;
}
.expand-hint {
  position: absolute;
  top: 8px;
  right: 10px;
  font-size: 14px;
  line-height: 1;
  color: #8a9bab;
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
}
.is-expandable:hover .expand-hint,
.is-expandable:focus-visible .expand-hint {
  opacity: 1;
}
</style>

<style>
.chart-expand-layer {
  position: fixed;
  inset: 0;
  z-index: 5000;
  pointer-events: none;
}
.chart-expand-layer.is-interactive {
  pointer-events: auto;
}
.chart-expand-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.28);
  backdrop-filter: blur(1.5px);
  opacity: 0;
}
.chart-expand-panel {
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 14px;
  border: 1px solid #e8f0f6;
  box-shadow: 0 24px 64px rgba(43, 88, 118, 0.22);
  overflow: hidden;
  will-change: transform, opacity;
}
.chart-expand-title {
  margin: 0;
  padding: 14px 48px 10px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #344675;
  text-align: center;
  flex-shrink: 0;
}
.chart-expand-chart {
  flex: 1;
  min-height: 0;
  padding: 0 12px 16px;
  display: flex;
}
.chart-expand-close {
  position: absolute;
  top: 10px;
  right: 12px;
  z-index: 2;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: #f0f4f8;
  color: #5a6f82;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
  transition: background 0.15s ease;
}
.chart-expand-close:hover {
  background: #e2eaf2;
  color: #2b5876;
}
</style>
