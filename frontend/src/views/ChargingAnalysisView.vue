<template>
  <NowUiPageCard
    v-loading="loading"
    page-title="设备的每日、每月充电频数"
    page-subtitle="Daily and Monthly Charging Frequency"
    :section-hint="t('nav.sectionHint')"
  >
    <div class="now-chart-grid">
      <ExpandableChartBlock title="设备的每日充电频数 (Histogram)" :option="dailyOption">
        <MrEchart v-if="dailyOption" :option="dailyOption" />
        <el-empty v-else description="暂无每日数据" />
      </ExpandableChartBlock>
      <ExpandableChartBlock title="设备每月充电频数 (Histogram)" :option="monthlyOption">
        <MrEchart v-if="monthlyOption" :option="monthlyOption" />
        <el-empty v-else description="暂无每月数据" />
      </ExpandableChartBlock>
    </div>
  </NowUiPageCard>
</template>

<script setup lang="ts">
defineOptions({ name: 'ChargingAnalysisView' })

import type { ChartOption } from '@/utils/mrCharts'
import { onMounted, ref } from 'vue'
import MrEchart from '@/components/bi/AsyncMrEchart'
import ExpandableChartBlock from '@/components/bi/ExpandableChartBlock.vue'
import NowUiPageCard from '@/components/layout/NowUiPageCard.vue'
import { useLocale } from '@/composables/useLocale'
import { fetchChargingDaily, fetchChargingMonthly } from '@/api/bi'
import {
  formatChargingDate,
  formatChargingMonth,
  singleLineOption,
  sortByTimeKey,
} from '@/utils/mrCharts'

const { t } = useLocale()

const loading = ref(false)
const dailyOption = ref<ChartOption | null>(null)
const monthlyOption = ref<ChartOption | null>(null)

onMounted(async () => {
  loading.value = true
  try {
    const daily = sortByTimeKey(await fetchChargingDaily(), 'record_date')
    const monthly = sortByTimeKey(await fetchChargingMonthly(), 'record_month')
    dailyOption.value = singleLineOption(
      '每日充电次数 Daily Charging Counts',
      daily.map((r) => formatChargingDate(r.record_date)),
      '充电频率 Charging Frequency',
      daily.map((r) => r.charge_count),
      { xAxisName: '日细分 Day', yDecimals: 0 },
    )
    monthlyOption.value = singleLineOption(
      '每月充电次数 Monthly Charging Counts',
      monthly.map((r) => formatChargingMonth(r.record_month)),
      '充电频率 Charging Frequency',
      monthly.map((r) => r.charge_count),
      { xAxisName: '月细分 Month', yDecimals: 0 },
    )
  } finally {
    loading.value = false
  }
})
</script>
