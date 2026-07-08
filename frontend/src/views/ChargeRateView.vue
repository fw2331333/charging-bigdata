<template>
  <NowUiPageCard
    v-loading="loading"
    page-title="平均充电速率图分析"
    page-subtitle="Average Charging Speed"
    :section-hint="t('nav.sectionHint')"
  >
    <ExpandableChartBlock title="Average Charging Speed by Hour of Day" :option="option">
      <MrEchart v-if="option" :option="option" />
      <el-empty v-else description="暂无数据" />
    </ExpandableChartBlock>
  </NowUiPageCard>
</template>

<script setup lang="ts">
defineOptions({ name: 'ChargeRateView' })

import type { ChartOption } from '@/utils/mrCharts'
import { onMounted, ref } from 'vue'
import MrEchart from '@/components/bi/AsyncMrEchart'
import ExpandableChartBlock from '@/components/bi/ExpandableChartBlock.vue'
import NowUiPageCard from '@/components/layout/NowUiPageCard.vue'
import { useLocale } from '@/composables/useLocale'
import { fetchChargeRateHourly } from '@/api/bi'

const { t } = useLocale()
import { formatHourAxis, singleLineOption, sortByTimeKey } from '@/utils/mrCharts'

const loading = ref(false)
const option = ref<ChartOption | null>(null)

onMounted(async () => {
  loading.value = true
  try {
    const rows = sortByTimeKey(await fetchChargeRateHourly(), 'hour_key')
    option.value = singleLineOption(
      'Average Charging Speed by Hour of Day',
      rows.map((r) => formatHourAxis(r.hour_key)),
      'Average Charging Speed (SOC/min)',
      rows.map((r) => r.avg_rate),
      { xAxisName: 'Hour of the Day', yDecimals: 4 },
    )
  } finally {
    loading.value = false
  }
})
</script>
