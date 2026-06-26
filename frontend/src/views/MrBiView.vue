<template>
  <el-card v-loading="loading">
    <template #header>
      <div class="header">
        <span>MapReduce 汇总 BI（MySQL 动态图表）</span>
        <el-tag type="success">MySQL → API → ECharts</el-tag>
      </div>
    </template>
    <p class="desc">
      数据来自 MapReduce 入库结果（charging_bigdata），由后端 API 实时查询，前端 ECharts 动态渲染。
      <strong>v1/v2/v4/v5 横轴为记录时间正序；v3/v6 为明细时序数据。</strong>
    </p>
    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <el-tab-pane v-for="tab in tabs" :key="tab.key" :label="tab.label" :name="tab.key">
        <el-empty v-if="!options[tab.key] && !loading" description="暂无数据，请先运行流水线入库" />
        <MrEchart v-if="options[tab.key]" :key="tab.key" :option="options[tab.key]!" />
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { nextTick, onMounted, reactive, ref } from 'vue'
import MrEchart from '@/components/bi/MrEchart.vue'
import {
  fetchCellVoltageRange,
  fetchChargeCurrentStats,
  fetchEnergyCapacity,
  fetchSocTemperature,
  fetchTemperature,
  fetchVoltageCurrent,
  fetchVoltageCurrentRelation,
} from '@/api/bi'
import {
  barOption,
  dualLineOption,
  formatMrTime,
  scatterOption,
  sortByTimeKey,
} from '@/utils/mrCharts'

type TabKey = 'v1' | 'v2' | 'v3' | 'v4' | 'v5' | 'v6' | 'v7'

const loading = ref(false)
const activeTab = ref<TabKey>('v1')
const options = reactive<Partial<Record<TabKey, EChartsOption>>>({})
const loaded = reactive<Partial<Record<TabKey, boolean>>>({})

const tabs: { key: TabKey; label: string }[] = [
  { key: 'v1', label: 'v1 电压电流' },
  { key: 'v2', label: 'v2 单体电压' },
  { key: 'v3', label: 'v3 温度' },
  { key: 'v4', label: 'v4 能量容量' },
  { key: 'v5', label: 'v5 充电电流' },
  { key: 'v6', label: 'v6 电压电流关系' },
  { key: 'v7', label: 'v7 SOC 温度' },
]

async function loadV1() {
  const rows = sortByTimeKey(await fetchVoltageCurrent(), 'record_hour')
  const x = rows.map((r) => formatMrTime(r.record_hour))
  options.v1 = dualLineOption(
    'v1 组电压与充电电流（时序）',
    x,
    [
      { name: '平均组电压(V)', data: rows.map((r) => r.avg_pack_voltage), yAxisIndex: 0 },
      { name: '平均充电电流(A)', data: rows.map((r) => r.avg_charge_current), yAxisIndex: 1 },
    ],
    ['电压(V)', '电流(A)'],
    { xAxisName: '时间', yDecimals: 2 },
  )
}

async function loadV2() {
  const rows = sortByTimeKey(await fetchCellVoltageRange(), 'record_hour')
  const x = rows.map((r) => formatMrTime(r.record_hour))
  options.v2 = dualLineOption(
    'v2 单体电压范围（时序）',
    x,
    [
      { name: '最高单体电压(V)', data: rows.map((r) => r.max_cell_voltage) },
      { name: '最低单体电压(V)', data: rows.map((r) => r.min_cell_voltage) },
    ],
    ['电压(V)'],
    { xAxisName: '时间', yDecimals: 3 },
  )
}

async function loadV3() {
  const rows = sortByTimeKey(await fetchTemperature(), 'record_time')
  const x = rows.map((r) => formatMrTime(r.record_time))
  options.v3 = dualLineOption(
    'v3 电池温度趋势',
    x,
    [
      { name: '最高温度(℃)', data: rows.map((r) => r.max_temperature) },
      { name: '最低温度(℃)', data: rows.map((r) => r.min_temperature) },
    ],
    ['温度(℃)'],
    { xAxisName: '时间', yDecimals: 1 },
  )
}

async function loadV4() {
  const rows = sortByTimeKey(await fetchEnergyCapacity(), 'record_hour')
  const x = rows.map((r) => formatMrTime(r.record_hour))
  options.v4 = dualLineOption(
    'v4 可用能量与容量（时序）',
    x,
    [
      { name: '平均可用能量(kW)', data: rows.map((r) => r.avg_available_energy), yAxisIndex: 0 },
      { name: '平均可用容量(Ah)', data: rows.map((r) => r.avg_available_capacity), yAxisIndex: 1 },
    ],
    ['能量(kW)', '容量(Ah)'],
    { xAxisName: '时间', yDecimals: 2 },
  )
}

async function loadV5() {
  const rows = sortByTimeKey(await fetchChargeCurrentStats(), 'record_hour')
  const x = rows.map((r) => formatMrTime(r.record_hour))
  options.v5 = dualLineOption(
    'v5 充电电流统计（时序）',
    x,
    [
      { name: '平均充电电流(A)', data: rows.map((r) => r.avg_charge_current) },
      { name: '最大充电电流(A)', data: rows.map((r) => r.max_charge_current) },
    ],
    ['电流(A)'],
    { xAxisName: '时间', yDecimals: 2 },
  )
}

async function loadV6() {
  const rows = sortByTimeKey(await fetchVoltageCurrentRelation(), 'record_time')
  const points = rows.map((r) => [r.pack_voltage, r.charge_current] as [number, number])
  options.v6 = scatterOption('v6 组电压与充电电流关系', points, '组电压(V)', '充电电流(A)')
}

async function loadV7() {
  const rows = await fetchSocTemperature()
  options.v7 = barOption(
    'v7 不同 SOC 区间平均温度',
    rows.map((r) => r.soc_bucket),
    [
      { name: '平均最高温度(℃)', data: rows.map((r) => r.avg_max_temperature) },
      { name: '平均最低温度(℃)', data: rows.map((r) => r.avg_min_temperature) },
    ],
    '温度(℃)',
  )
}

const loaders: Record<TabKey, () => Promise<void>> = {
  v1: loadV1,
  v2: loadV2,
  v3: loadV3,
  v4: loadV4,
  v5: loadV5,
  v6: loadV6,
  v7: loadV7,
}

async function onTabChange(name?: string | number) {
  await loadTab(name)
  await nextTick()
  window.dispatchEvent(new Event('resize'))
}

async function loadTab(name?: string | number) {
  const key = (name ?? activeTab.value) as TabKey
  if (loaded[key]) return
  loading.value = true
  try {
    await loaders[key]()
    loaded[key] = true
  } finally {
    loading.value = false
  }
}

onMounted(() => loadTab('v1'))
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.desc {
  margin: 0 0 12px;
  color: #606266;
  font-size: 13px;
}
</style>
