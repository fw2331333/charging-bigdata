<template>
  <el-card v-loading="loading">
    <template #header>SOC 热力图（MySQL ADS）</template>
    <p class="hint">Spark SQL 聚合 → MySQL <code>t_soc_heatmap</code></p>
    <el-alert
      v-if="pointCount > 0 && pointCount < 30"
      type="info"
      :closable="false"
      class="mb"
      :title="`当前仅 ${pointCount} 个聚合点（数据集时间跨度短），热力图只显示有数据的小时/日期，属正常现象`"
    />
    <el-empty v-if="!option && !loading" description="暂无数据" />
    <MrEchart v-if="option" :option="option" />
  </el-card>
</template>

<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { onMounted, ref } from 'vue'
import MrEchart from '@/components/bi/MrEchart.vue'
import { fetchSocHeatmap } from '@/api/bi'
import { formatMrTime, heatmapOption, sortByTimeKey, sortHours } from '@/utils/mrCharts'

const loading = ref(false)
const option = ref<EChartsOption | null>(null)
const pointCount = ref(0)

onMounted(async () => {
  loading.value = true
  try {
    const rows = sortByTimeKey(await fetchSocHeatmap(), 'record_day')
    pointCount.value = rows.length
    const days = [...new Set(rows.map((r) => r.record_day))].sort()
    const hours = sortHours([...new Set(rows.map((r) => r.hour_key))])
    const dayIndex = new Map(days.map((d, i) => [d, i]))
    const hourIndex = new Map(hours.map((h, i) => [h, i]))
    const data: [number, number, number][] = []
    let maxSoc = 0
    for (const r of rows) {
      const di = dayIndex.get(r.record_day)
      const hi = hourIndex.get(r.hour_key)
      if (di === undefined || hi === undefined) continue
      data.push([hi, di, r.avg_soc])
      maxSoc = Math.max(maxSoc, r.avg_soc)
    }
    const fmtDay = (d: string) => formatMrTime(d.length === 8 ? d : d)
    const opt = heatmapOption(
      'SOC 热力图（日期 × 小时）',
      days.map(fmtDay),
      hours,
      data,
    )
    const visualMap = opt.visualMap
    if (visualMap && !Array.isArray(visualMap)) {
      ;(visualMap as { max?: number }).max = Math.ceil(maxSoc) || 100
    }
    option.value = opt
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.hint { margin: 0 0 12px; color: #909399; font-size: 13px; }
.mb { margin-bottom: 12px; }
</style>
