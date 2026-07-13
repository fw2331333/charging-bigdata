<template>
  <div v-loading="loading" class="mr-bi-page">
    <BiVisuHeader />
    <FourSBanner />

    <div class="mr-bi-grid">
      <div v-for="panel in panels" :key="panel.key" class="mr-bi-cell" :class="panel.span">
        <MrEchart
          v-if="panel.option"
          :option="panel.option"
          :height="panel.height"
          :drillable="!!panel.drill"
          @chart-click="goDrill(panel.drill)"
        />
        <el-empty v-else description="暂无数据" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'MrBiView' })

import type { ChartOption } from '@/utils/mrCharts'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import BiVisuHeader from '@/components/bi/BiVisuHeader.vue'
import MrEchart from '@/components/bi/AsyncMrEchart'
import FourSBanner from '@/components/home/FourSBanner.vue'
import { fetchViewConfigs, type ChartViewConfig } from '@/api/auth'
import {
  fetchCellVoltageRange,
  fetchChargeCurrentStats,
  fetchEnergyCapacity,
  fetchSocTemperature,
  fetchTemperature,
  fetchVoltageCurrent,
  fetchVoltageCurrentRelation,
  type CellVoltageRangeItem,
  type ChargeCurrentStatsItem,
  type EnergyCapacityItem,
  type SocTemperatureItem,
  type TemperatureItem,
  type VoltageCurrentItem,
  type VoltageCurrentRelationItem,
} from '@/api/bi'
import {
  aggregateTemperatureByHour,
  barWithTotalOption,
  batteryStatusTemperatureOption,
  dualBarVisuOption,
  dualLineOption,
  hourAxisLabel,
  sortByTimeKey,
  stackedAreaOption,
} from '@/utils/mrCharts'

interface Panel {
  key: string
  option: ChartOption | null
  span?: string
  height?: number
  drill?: string
}

const router = useRouter()
const loading = ref(false)
const panels = ref<Panel[]>([])

const DATA_FETCHERS: Record<string, () => Promise<unknown>> = {
  '/bi/voltage-current': () => fetchVoltageCurrent(),
  '/bi/cell-voltage-range': () => fetchCellVoltageRange(),
  '/bi/temperature': () => fetchTemperature(),
  '/bi/energy-capacity': () => fetchEnergyCapacity(),
  '/bi/charge-current-stats': () => fetchChargeCurrentStats(),
  '/bi/voltage-current-relation': () => fetchVoltageCurrentRelation(),
  '/bi/soc-temperature': () => fetchSocTemperature(),
}

function goDrill(path?: string) {
  if (path) router.push(path)
}

function setOption(key: string, option: ChartOption | null) {
  const p = panels.value.find((x) => x.key === key)
  if (p) p.option = option
}

function buildOption(cfg: ChartViewConfig, raw: unknown): ChartOption | null {
  const title = cfg.title
  const key = cfg.chart_key

  if (key === 'v1') {
    const rows = sortByTimeKey(raw as VoltageCurrentItem[], 'record_hour')
    const x = rows.map((r) => hourAxisLabel(r.record_hour))
    return dualBarVisuOption(
      x,
      rows.map((r) => r.avg_pack_voltage),
      rows.map((r) => r.avg_charge_current),
    )
  }

  if (key === 'v2') {
    const rows = sortByTimeKey(raw as CellVoltageRangeItem[], 'record_hour')
    const x = rows.map((r) => hourAxisLabel(r.record_hour))
    return dualLineOption(
      title,
      x,
      [
        { name: 'max_cell_voltage', data: rows.map((r) => r.max_cell_voltage) },
        { name: 'min_cell_voltage', data: rows.map((r) => r.min_cell_voltage) },
      ],
      ['V', 'V'],
      { xAxisName: '小时', yDecimals: 4 },
    )
  }

  if (key === 'v3') {
    const rows = aggregateTemperatureByHour(raw as TemperatureItem[])
    const x = rows.map((r) => r.label)
    return dualLineOption(
      title,
      x,
      [
        { name: 'max_temperature', data: rows.map((r) => r.max_temperature) },
        { name: 'min_temperature', data: rows.map((r) => r.min_temperature) },
      ],
      ['℃', '℃'],
      { xAxisName: '时间', yDecimals: 2 },
    )
  }

  if (key === 'v4') {
    const rows = sortByTimeKey(raw as EnergyCapacityItem[], 'record_hour')
    const x = rows.map((r) => hourAxisLabel(r.record_hour))
    return stackedAreaOption(x, [
      { name: 'avg_available_energy', data: rows.map((r) => r.avg_available_energy) },
      { name: 'avg_available_capacity', data: rows.map((r) => r.avg_available_capacity) },
    ])
  }

  if (key === 'v5') {
    const rows = sortByTimeKey(raw as ChargeCurrentStatsItem[], 'record_hour')
    const x = rows.map((r) => hourAxisLabel(r.record_hour))
    return barWithTotalOption(x, rows.map((r) => r.max_charge_current))
  }

  if (key === 'v6') {
    const rows = sortByTimeKey(raw as VoltageCurrentRelationItem[], 'record_hour')
    const x = rows.map((r) => r.record_hour)
    return dualLineOption(
      title,
      x,
      [
        { name: 'voltage_change_rate', data: rows.map((r) => r.voltage_change_rate) },
        { name: 'current_change_rate', data: rows.map((r) => r.current_change_rate), yAxisIndex: 1 },
      ],
      ['Voltage Avg Chg (%)', 'Current |I| Avg Chg (%)'],
      { xAxisName: 'Hour of Day', yDecimals: 4 },
    )
  }

  if (key === 'v7') {
    const rows = raw as SocTemperatureItem[]
    return batteryStatusTemperatureOption(
      title,
      rows.map((r) => ({
        status: r.battery_status,
        avgMaxTemperature: r.avg_max_temperature,
        avgMinTemperature: r.avg_min_temperature,
        varMaxTemperature: r.var_max_temperature,
        varMinTemperature: r.var_min_temperature,
      })),
    )
  }

  return null
}

onMounted(async () => {
  loading.value = true
  try {
    const configs = (await fetchViewConfigs())
      .filter((c) => c.enabled && /^v[1-7]$/.test(c.chart_key))
      .sort((a, b) => a.sort_order - b.sort_order)

    panels.value = configs.map((c) => ({
      key: c.chart_key,
      option: null,
      span: c.chart_key === 'v7' ? 'span-full' : undefined,
      height: c.chart_key === 'v7' ? 360 : undefined,
      drill: c.drill_route ?? undefined,
    }))

    const sources = [...new Set(configs.map((c) => c.data_source))]
    const dataMap = new Map<string, unknown>()
    await Promise.all(
      sources.map(async (src) => {
        const fetcher = DATA_FETCHERS[src]
        if (fetcher) dataMap.set(src, await fetcher())
      }),
    )

    for (const cfg of configs) {
      const raw = dataMap.get(cfg.data_source)
      if (raw) setOption(cfg.chart_key, buildOption(cfg, raw))
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.mr-bi-page {
  padding: 8px 4px 24px;
}
.mr-bi-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}
.mr-bi-cell {
  min-height: 320px;
  padding: 8px 10px 4px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e8eef3;
  box-shadow: 0 1px 8px rgba(61, 126, 184, 0.06);
}
.mr-bi-cell.span-full {
  grid-column: 1 / -1;
  min-height: 280px;
}
@media (max-width: 900px) {
  .mr-bi-grid {
    grid-template-columns: 1fr;
  }
}
</style>
