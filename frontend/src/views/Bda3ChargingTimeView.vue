<template>
  <NowUiPageCard
    v-loading="loading"
    page-title="充电时间分析"
    page-subtitle="Charging Time Analysis"
    :section-hint="t('nav.sectionHint')"
  >
    <div class="now-chart-grid cols-3">
      <ExpandableChartBlock title="Hourly Charging Time Analysis" :option="hourlyOption">
        <MrEchart v-if="hourlyOption" :option="hourlyOption" />
        <el-empty v-else description="暂无数据" />
      </ExpandableChartBlock>
      <ExpandableChartBlock title="Daily Charging Time Analysis" :option="dailyProxy">
        <MrEchart v-if="dailyProxy" :option="dailyProxy" />
        <el-empty v-else description="暂无每日数据" />
      </ExpandableChartBlock>
      <ExpandableChartBlock title="Monthly Charging Time Analysis" :option="monthlyProxy">
        <MrEchart v-if="monthlyProxy" :option="monthlyProxy" />
        <el-empty v-else description="暂无每月数据" />
      </ExpandableChartBlock>
    </div>
  </NowUiPageCard>
</template>

<script setup lang="ts">
defineOptions({ name: 'Bda3ChargingTimeView' })

import type { ChartOption } from '@/utils/mrCharts'
import { onMounted, ref } from 'vue'
import MrEchart from '@/components/bi/AsyncMrEchart'
import ExpandableChartBlock from '@/components/bi/ExpandableChartBlock.vue'
import NowUiPageCard from '@/components/layout/NowUiPageCard.vue'
import { useLocale } from '@/composables/useLocale'
import { fetchChargeRateHourly, fetchChargingDaily, fetchChargingMonthly } from '@/api/bi'

const { t } = useLocale()
import {
  formatChargingDate,
  formatChargingMonth,
  formatHourAxis,
  singleLineOption,
  sortByTimeKey,
} from '@/utils/mrCharts'

const loading = ref(false)
const hourlyOption = ref<ChartOption | null>(null)
const dailyProxy = ref<ChartOption | null>(null)
const monthlyProxy = ref<ChartOption | null>(null)

onMounted(async () => {
  loading.value = true
  try {
    const hourly = sortByTimeKey(await fetchChargeRateHourly(), 'hour_key')
    hourlyOption.value = singleLineOption(
      'Average Charge Rate by Hour',
      hourly.map((r) => formatHourAxis(r.hour_key)),
      'Average Charge Rate (SOC/min)',
      hourly.map((r) => r.avg_rate),
      { xAxisName: 'Hour of the Day', yDecimals: 4, scale: true },
    )

    const daily = sortByTimeKey(await fetchChargingDaily(), 'record_date')
    if (daily.length > 0) {
      dailyProxy.value = singleLineOption(
        'Daily Charging Pattern (session count)',
        daily.map((r) => formatChargingDate(r.record_date)),
        'Charge Sessions',
        daily.map((r) => r.charge_count),
        { xAxisName: 'Date', yDecimals: 0 },
      )
    }

    const monthly = sortByTimeKey(await fetchChargingMonthly(), 'record_month')
    if (monthly.length > 0) {
      monthlyProxy.value = singleLineOption(
        'Monthly Charging Pattern (proxy: session count)',
        monthly.map((r) => formatChargingMonth(r.record_month)),
        'Charge Sessions',
        monthly.map((r) => r.charge_count),
        { xAxisName: 'Month of the Year', yDecimals: 0 },
      )
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.cols-3 {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}
</style>
