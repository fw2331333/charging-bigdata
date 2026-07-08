<template>
  <NowUiPageCard
    v-loading="loading"
    page-title="电池使用轨迹图"
    page-subtitle="Battery Usage Trajectory"
    :section-hint="t('nav.sectionHint')"
  >
    <div class="now-chart-grid cols-3">
      <ExpandableChartBlock title="电池使用轨迹图 (Battery Usage Trajectory)" :option="lineOption">
        <MrEchart v-if="lineOption" :option="lineOption" />
        <el-empty v-else description="暂无 SOC 时序数据" />
      </ExpandableChartBlock>
      <ExpandableChartBlock title="电池使用轨迹热力图 (Trajectory Heatmap)" :option="heatOption">
        <MrEchart v-if="heatOption" :option="heatOption" />
        <el-empty v-else description="暂无热力图数据" />
      </ExpandableChartBlock>
      <ExpandableChartBlock title="每小时平均 SOC" :option="hourlyOption">
        <MrEchart v-if="hourlyOption" :option="hourlyOption" />
        <el-empty v-else description="暂无数据" />
      </ExpandableChartBlock>
    </div>
  </NowUiPageCard>
</template>

<script setup lang="ts">
defineOptions({ name: 'SocAnalysisView' })

import type { ChartOption } from '@/utils/mrCharts'
import { onMounted, ref } from 'vue'
import MrEchart from '@/components/bi/AsyncMrEchart'
import ExpandableChartBlock from '@/components/bi/ExpandableChartBlock.vue'
import NowUiPageCard from '@/components/layout/NowUiPageCard.vue'
import { useLocale } from '@/composables/useLocale'
import { fetchSocHeatmap, fetchSocHourly } from '@/api/bi'
import {
  formatHourAxis,
  formatMrTime,
  heatmapOption,
  singleLineOption,
  sortByTimeKey,
  sortHours,
} from '@/utils/mrCharts'

const { t } = useLocale()

const loading = ref(false)
const lineOption = ref<ChartOption | null>(null)
const hourlyOption = ref<ChartOption | null>(null)
const heatOption = ref<ChartOption | null>(null)

onMounted(async () => {
  loading.value = true
  try {
    const hourly = sortByTimeKey(await fetchSocHourly(), 'time_key')
    lineOption.value = singleLineOption(
      'Battery Usage Trajectory',
      hourly.map((r) => formatMrTime(r.time_key)),
      'Average State of Charge (SOC)',
      hourly.map((r) => r.avg_soc),
      { xAxisName: 'Hour of Day', yDecimals: 2 },
    )
    hourlyOption.value = singleLineOption(
      'Average SOC by Hour',
      hourly.map((r) => formatHourAxis(r.time_key.slice(-2) || r.time_key)),
      'SOC(%)',
      hourly.map((r) => r.avg_soc),
      { xAxisName: 'Hour', yDecimals: 2 },
    )

    const heatRows = sortByTimeKey(await fetchSocHeatmap(), 'record_day')
    const days = [...new Set(heatRows.map((r) => r.record_day))].sort()
    const hours = sortHours([...new Set(heatRows.map((r) => r.hour_key))])
    const dayIndex = new Map(days.map((d, i) => [d, i]))
    const hourIndex = new Map(hours.map((h, i) => [h, i]))
    const data: [number, number, number][] = []
    let maxSoc = 0
    for (const r of heatRows) {
      const di = dayIndex.get(r.record_day)
      const hi = hourIndex.get(r.hour_key)
      if (di === undefined || hi === undefined) continue
      data.push([hi, di, r.avg_soc])
      maxSoc = Math.max(maxSoc, r.avg_soc)
    }
    if (data.length > 0) {
      const opt = heatmapOption('Battery Usage Trajectory Heatmap', days.map((d) => formatMrTime(d)), hours, data)
      const visualMap = opt.visualMap
      if (visualMap && !Array.isArray(visualMap)) {
        ;(visualMap as { max?: number }).max = Math.ceil(maxSoc) || 100
      }
      heatOption.value = opt
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.cols-3 {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}
</style>
