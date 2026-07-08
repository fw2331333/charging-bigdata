<template>
  <div
    ref="el"
    class="mr-echart"
    :class="{ 'mr-echart-fill': fill, 'mr-echart-drill': drillable }"
    :style="fill ? undefined : { height: `${height}px` }"
  />
</template>

<script setup lang="ts">
import { echarts } from '@/lib/echarts'
import type { ChartOption } from '@/utils/mrCharts'
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { refreshScrollTriggers } from '@/composables/useScrollRefresh'

const props = withDefaults(
  defineProps<{
    option: ChartOption
    height?: number
    fill?: boolean
    drillable?: boolean
  }>(),
  { height: 420, fill: false, drillable: false },
)

const emit = defineEmits<{ chartClick: [] }>()

const el = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

function render() {
  if (!el.value) return
  chart ??= echarts.init(el.value)
  chart.setOption(props.option, { notMerge: true })
  chart.resize()
  chart.off('click', onChartClick)
  if (props.drillable) chart.on('click', onChartClick)
  refreshScrollTriggers()
}

function resize() {
  chart?.resize()
}

defineExpose({ resize })

function onResize() {
  resize()
}

function onChartClick() {
  if (props.drillable) emit('chartClick')
}

onMounted(() => {
  render()
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  chart?.off('click', onChartClick)
  chart?.dispose()
  chart = null
})

watch(() => props.option, render, { deep: true })
</script>

<style scoped>
.mr-echart {
  width: 100%;
  min-width: 0;
  overflow: visible;
}
.mr-echart-fill {
  flex: 1;
  min-height: 0;
  height: 100%;
}
.mr-echart-drill {
  cursor: pointer;
}
</style>
