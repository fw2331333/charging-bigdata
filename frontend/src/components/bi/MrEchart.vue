<template>
  <div ref="el" class="mr-echart" />
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import { onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps<{
  option: EChartsOption
}>()

const el = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

function render() {
  if (!el.value) return
  chart ??= echarts.init(el.value)
  chart.setOption(props.option, { notMerge: true })
  chart.resize()
}

function resize() {
  chart?.resize()
}

defineExpose({ resize })

function onResize() {
  resize()
}

onMounted(() => {
  render()
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  chart?.dispose()
  chart = null
})

watch(() => props.option, render, { deep: true })
</script>

<style scoped>
.mr-echart {
  width: 100%;
  height: 420px;
}
</style>
