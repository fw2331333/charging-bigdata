import type { EChartsOption } from 'echarts'

/** 工厂函数返回值类型（放宽以通过 vue-tsc） */
export type ChartOption = EChartsOption | Record<string, unknown>

/** 紧凑时间键；nvv2t 年份 0014→2014（与 nvv2t_md 一致） */
export function normalizeCompactDate(s: string): string {
  const digits = (s || '').replace(/\D/g, '')
  if (digits.length >= 6 && digits.startsWith('00')) {
    return '20' + digits.slice(2)
  }
  return digits
}

/** MR / ADS 时间键 → 显示：yyyy-MM-dd HH:mm */
export function formatMrTime(value: string): string {
  if (!value) return value
  const v = normalizeCompactDate(value)
  if (v.length >= 12) {
    return `${v.slice(0, 4)}-${v.slice(4, 6)}-${v.slice(6, 8)} ${v.slice(8, 10)}:${v.slice(10, 12)}`
  }
  if (v.length >= 10) {
    return `${v.slice(0, 4)}-${v.slice(4, 6)}-${v.slice(6, 8)} ${v.slice(8, 10)}:00`
  }
  if (v.length === 8) {
    return `${v.slice(0, 4)}-${v.slice(4, 6)}-${v.slice(6, 8)}`
  }
  return value
}

/** 同一年份时省略重复年份，仅保留 MM-dd HH:mm */
export function formatMrTimeSeries(values: string[]): string[] {
  const full = values.map(formatMrTime)
  const years = new Set(
    full
      .map((s) => (s.length >= 4 && /^\d{4}/.test(s) ? s.slice(0, 4) : ''))
      .filter(Boolean),
  )
  if (years.size === 1) {
    const y = [...years][0]
    const prefix = `${y}-`
    return full.map((s) => (s.startsWith(prefix) ? s.slice(prefix.length) : s))
  }
  return full
}

/** 充电日统计 yyyyMMdd */
export function formatChargingDate(value: string): string {
  const v = normalizeCompactDate(value)
  if (v.length === 8) {
    return `${v.slice(0, 4)}-${v.slice(4, 6)}-${v.slice(6, 8)}`
  }
  return value
}

/** 充电月统计 yyyyMM */
export function formatChargingMonth(value: string): string {
  const v = normalizeCompactDate(value)
  if (v.length >= 6) {
    return `${v.slice(0, 4)}-${v.slice(4, 6)}`
  }
  return value
}

/** 仅小时 HH（充电速率等按小时聚合图） */
export function formatHourAxis(value: string): string {
  if (!value) return value
  if (/^\d{10,}$/.test(value)) {
    return value.slice(8, 10)
  }
  return value.padStart(2, '0')
}

/** 按时间键升序（时间发展从左到右） */
export function compareTimeKeys(a: string, b: string): number {
  const na = normalizeCompactDate(a)
  const nb = normalizeCompactDate(b)
  if (na.length !== nb.length) return na.length - nb.length
  return na.localeCompare(nb)
}

export function sortByTimeKey<T>(rows: T[], key: keyof T): T[] {
  return [...rows].sort((a, b) => compareTimeKeys(String(a[key]), String(b[key])))
}

/** 温度明细按 yyyyMMddHH 聚合，避免 v3 图 X 轴重复拥挤 */
export function aggregateTemperatureByHour(
  rows: { record_time: string; max_temperature: number; min_temperature: number }[],
): { label: string; max_temperature: number; min_temperature: number }[] {
  const map = new Map<string, { max: number; min: number }>()
  for (const r of rows) {
    const v = normalizeCompactDate(r.record_time)
    const key = v.length >= 10 ? v.slice(0, 10) : v.length >= 8 ? `${v.slice(0, 8)}00` : v
    const cur = map.get(key)
    if (!cur) {
      map.set(key, { max: r.max_temperature, min: r.min_temperature })
    } else {
      cur.max = Math.max(cur.max, r.max_temperature)
      cur.min = Math.min(cur.min, r.min_temperature)
    }
  }
  return [...map.entries()]
    .sort((a, b) => compareTimeKeys(a[0], b[0]))
    .map(([key, { max, min }]) => ({
      label: key.length >= 10
        ? `${key.slice(4, 6)}-${key.slice(6, 8)} ${key.slice(8, 10)}:00`
        : formatMrTime(key),
      max_temperature: max,
      min_temperature: min,
    }))
}

export function sortHours(hours: string[]): string[] {
  return [...hours].sort((a, b) => Number(a) - Number(b))
}

function axisLabelInterval(count: number): number | 'auto' {
  if (count <= 12) return 0
  if (count <= 31) return 0
  if (count <= 90) return Math.floor(count / 15)
  return 'auto'
}

/** 根据 Y 轴标题长度预留左侧空间，避免轴名称被裁切 */
function gridLeftForYName(name?: string, extra = 0): number {
  const len = (name ?? '').length
  if (len <= 8) return 48 + extra
  if (len <= 16) return 56 + extra
  return Math.min(108, 52 + len * 4) + extra
}

function gridRightForYName(name?: string): number {
  const len = (name ?? '').length
  return len > 0 ? Math.min(96, 36 + len * 4) : 24
}

/** 长 Y 轴标题用顶部横排，避免多图并排时左侧竖排文字伸入邻列被裁切 */
function usesHorizontalYName(name?: string): boolean {
  return (name?.length ?? 0) > 4
}

function chartGrid(opts: {
  leftYName?: string
  rightYName?: string
  top?: number
  bottom?: number
}): Record<string, number | boolean> {
  const topName = usesHorizontalYName(opts.leftYName)
  const baseTop = opts.top ?? 60
  return {
    containLabel: true,
    left: topName ? 40 : gridLeftForYName(opts.leftYName),
    right: gridRightForYName(opts.rightYName),
    top: topName ? baseTop + 14 : baseTop,
    bottom: opts.bottom ?? 48,
  }
}

function valueYAxis(name: string, extra?: Record<string, unknown>) {
  if (usesHorizontalYName(name)) {
    return {
      type: 'value' as const,
      name,
      nameLocation: 'end' as const,
      nameRotate: 0,
      nameGap: 10,
      nameTextStyle: { fontSize: 11, align: 'left', color: '#666' },
      ...extra,
    }
  }
  return {
    type: 'value' as const,
    name,
    nameLocation: 'middle' as const,
    nameRotate: 90,
    nameGap: 36,
    nameTextStyle: { fontSize: 11, padding: [0, 0, 0, 4] },
    ...extra,
  }
}

export function dualLineOption(
  title: string,
  xData: string[],
  series: { name: string; data: number[]; yAxisIndex?: number }[],
  yAxisNames: string[],
  opts?: { xAxisName?: string; yDecimals?: number },
): ChartOption {
  const fewPoints = xData.length <= 24
  const dec = opts?.yDecimals ?? 2
  return {
    title: { text: title, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      trigger: 'axis',
      valueFormatter: (v) => (typeof v === 'number' ? v.toFixed(dec) : String(v)),
    },
    legend: { top: 28 },
    grid: chartGrid({
      leftYName: yAxisNames[0],
      rightYName: yAxisNames[1],
      top: 72,
      bottom: xData.length > 12 ? 72 : 56,
    }),
    xAxis: {
      type: 'category',
      name: opts?.xAxisName ?? '时间',
      nameGap: 28,
      data: xData,
      boundaryGap: false,
      axisLabel: {
        rotate: xData.length > 8 ? 35 : 0,
        fontSize: 10,
        interval: axisLabelInterval(xData.length),
      },
    },
    yAxis: yAxisNames.map((name, idx) =>
      valueYAxis(name, {
        scale: !fewPoints,
        position: idx === 0 ? 'left' : 'right',
      }),
    ),
    dataZoom: xData.length > 48 ? [{ type: 'inside' }, { type: 'slider', height: 18, bottom: 4 }] : undefined,
    series: series.map((s) => ({
      name: s.name,
      type: 'line',
      smooth: !fewPoints,
      showSymbol: fewPoints || xData.length <= 48,
      symbolSize: fewPoints ? 8 : 4,
      yAxisIndex: s.yAxisIndex ?? 0,
      data: s.data.map((v) => Number(v.toFixed(dec))),
    })),
  }
}

export function scatterOption(
  title: string,
  points: [number, number][],
  xName: string,
  yName: string,
): ChartOption {
  return {
    title: { text: title, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      trigger: 'item',
      formatter: (params: unknown) => {
        const val = (params as { value: [number, number] }).value
        return `${xName}: ${val[0].toFixed(2)}<br/>${yName}: ${val[1].toFixed(2)}`
      },
    },
    grid: chartGrid({ leftYName: yName, rightYName: xName, top: 56, bottom: 48 }),
    xAxis: { type: 'value', name: xName, nameGap: 16, nameLocation: 'middle', scale: true },
    yAxis: valueYAxis(yName, { scale: true }),
    series: [{ type: 'scatter', symbolSize: 6, data: points }],
  }
}

const BATTERY_STATUS_LABELS: Record<string, string> = {
  idle: 'idle · SOC<20%',
  charging: 'charging · 20–50%',
  discharging: 'discharging · ≥50%',
}

export interface BatteryStatusTemperatureRow {
  status: string
  avgMaxTemperature: number
  avgMinTemperature: number
  varMaxTemperature: number
  varMinTemperature: number
}

/** v7：电池状态温度均值（柱）+ 方差（折线，右轴） */
export function batteryStatusTemperatureOption(
  title: string,
  rows: BatteryStatusTemperatureRow[],
): ChartOption {
  const labels = rows.map((r) => BATTERY_STATUS_LABELS[r.status] ?? r.status)
  const avgMax = rows.map((r) => Number(r.avgMaxTemperature.toFixed(2)))
  const avgMin = rows.map((r) => Number(r.avgMinTemperature.toFixed(2)))
  const varMax = rows.map((r) => Number(r.varMaxTemperature.toFixed(4)))
  const varMin = rows.map((r) => Number(r.varMinTemperature.toFixed(4)))

  return {
    title: { text: title, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: unknown) => {
        const items = (Array.isArray(params) ? params : [params]) as {
          seriesName: string
          value: number
          dataIndex: number
        }[]
        if (!items.length) return ''
        const idx = items[0].dataIndex
        const row = rows[idx]
        const stdMax = Math.sqrt(Math.max(row.varMaxTemperature, 0))
        const stdMin = Math.sqrt(Math.max(row.varMinTemperature, 0))
        const statusLabel = BATTERY_STATUS_LABELS[row.status] ?? row.status
        return [
          `<strong>${statusLabel}</strong>`,
          `平均最高温: ${row.avgMaxTemperature.toFixed(2)} ℃`,
          `平均最低温: ${row.avgMinTemperature.toFixed(2)} ℃`,
          `最高温方差: ${row.varMaxTemperature.toFixed(4)}`,
          `最低温方差: ${row.varMinTemperature.toFixed(4)}`,
          `最高温标准差: ${stdMax.toFixed(3)} ℃`,
          `最低温标准差: ${stdMin.toFixed(3)} ℃`,
        ].join('<br/>')
      },
    },
    legend: { top: 28, textStyle: { fontSize: 10 } },
    grid: chartGrid({
      leftYName: '温度 (℃)',
      rightYName: '方差',
      top: 88,
      bottom: 56,
    }),
    xAxis: {
      type: 'category',
      name: '电池状态',
      nameGap: 28,
      data: labels,
      axisLabel: { fontSize: 10, interval: 0 },
    },
    yAxis: [
      valueYAxis('温度 (℃)', {
        scale: true,
        splitLine: { lineStyle: { color: '#eee' } },
      }),
      valueYAxis('方差', {
        scale: true,
        position: 'right',
        splitLine: { show: false },
      }),
    ],
    series: [
      {
        name: 'avg_max_temperature',
        type: 'bar',
        yAxisIndex: 0,
        data: avgMax,
        itemStyle: { color: '#e85d6a' },
        barGap: '12%',
        barCategoryGap: '36%',
      },
      {
        name: 'avg_min_temperature',
        type: 'bar',
        yAxisIndex: 0,
        data: avgMin,
        itemStyle: { color: '#3d7eb8' },
      },
      {
        name: 'var_max_temperature',
        type: 'line',
        yAxisIndex: 1,
        data: varMax,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 2, type: 'dashed' },
        itemStyle: { color: '#c0392b' },
      },
      {
        name: 'var_min_temperature',
        type: 'line',
        yAxisIndex: 1,
        data: varMin,
        symbol: 'diamond',
        symbolSize: 8,
        lineStyle: { width: 2, type: 'dashed' },
        itemStyle: { color: '#2980b9' },
      },
    ],
  }
}

export function barOption(
  title: string,
  categories: string[],
  series: { name: string; data: number[] }[],
  yName = '℃',
): ChartOption {
  return {
    title: { text: title, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'axis', valueFormatter: (v) => Number(v).toFixed(2) },
    legend: { top: 28 },
    grid: chartGrid({ leftYName: yName, top: 72, bottom: 48 }),
    xAxis: { type: 'category', name: 'SOC区间(%)', data: categories },
    yAxis: valueYAxis(yName),
    series: series.map((s) => ({
      name: s.name,
      type: 'bar',
      data: s.data.map((v) => Number(v.toFixed(2))),
    })),
  }
}

export function singleLineOption(
  title: string,
  xData: string[],
  yName: string,
  data: number[],
  opts?: { xAxisName?: string; yDecimals?: number; scale?: boolean },
): ChartOption {
  const fewPoints = xData.length <= 24
  const dec = opts?.yDecimals ?? 0
  const nums = data.map((v) => Number(v))
  const hasNegative = nums.some((v) => v < 0)
  const useScale = opts?.scale ?? (hasNegative || (!fewPoints && data.length > 24))
  const yAxisExtra: Record<string, unknown> = { scale: useScale }
  if (!useScale && !hasNegative) {
    yAxisExtra.min = 0
  }
  return {
    title: { text: title, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      trigger: 'axis',
      valueFormatter: (v) => Number(v).toFixed(dec),
    },
    grid: chartGrid({
      leftYName: yName,
      top: title ? 72 : 56,
      bottom: xData.length > 12 ? 72 : 56,
    }),
    xAxis: {
      type: 'category',
      name: opts?.xAxisName ?? '时间',
      nameGap: 28,
      data: xData,
      boundaryGap: false,
      axisLabel: {
        rotate: xData.length > 8 ? 35 : 0,
        fontSize: 10,
        interval: axisLabelInterval(xData.length),
      },
    },
    yAxis: valueYAxis(yName, yAxisExtra),
    dataZoom: xData.length > 60 ? [{ type: 'inside' }, { type: 'slider', height: 18, bottom: 4 }] : undefined,
    series: [{
      type: 'line',
      data: data.map((v) => Number(v.toFixed(dec))),
      smooth: data.length > 12,
      showSymbol: data.length <= 48,
      symbolSize: 8,
    }],
  }
}

/** record_hour / record_time → 小时轴标签（visu1 为 00、11、12…） */
export function hourAxisLabel(value: string): string {
  const v = normalizeCompactDate(value)
  if (v.length >= 10) return v.slice(8, 10)
  if (v.length >= 8) return v.slice(6, 8)
  return value
}

const VISU_COLORS = ['#3d7eb8', '#e8a04c', '#e85d6a', '#f0a0b8', '#9b7fd4', '#5e9fd4', '#7eb8e8']

function visuGrid(): EChartsOption['grid'] {
  return { containLabel: true, left: 16, right: 16, top: 28, bottom: 36 }
}

export function donutOption(
  title: string,
  data: { name: string; value: number }[],
): ChartOption {
  const normalized = data.map((d) => ({
    name: d.name,
    value: Math.max(Math.abs(Number(d.value)) || 0, 0.001),
  }))
  return {
    title: { text: title, left: 'center', top: 0, textStyle: { fontSize: 11, fontWeight: 600 } },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { fontSize: 10 } },
    color: ['#3d7eb8', '#5e9fd4'],
    series: [{
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['50%', '48%'],
      avoidLabelOverlap: true,
      label: { fontSize: 10, formatter: '{b}: {d}%', color: '#3c4858' },
      labelLine: { length: 6, length2: 8 },
      data: normalized,
    }],
  }
}

export function pieOption(
  title: string,
  data: { name: string; value: number }[],
): ChartOption {
  const normalized = data.map((d) => ({
    name: d.name,
    value: Math.max(Math.abs(Number(d.value)) || 0, 0.001),
  }))
  return {
    title: { text: title, show: false },
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { show: false },
    color: VISU_COLORS,
    series: [{
      type: 'pie',
      radius: '62%',
      center: ['50%', '52%'],
      label: { fontSize: 10, formatter: '{b}: {d}%' },
      labelLine: { length: 8, length2: 10 },
      data: normalized,
    }],
  }
}

/** visu1 左上：组电压柱 + 充电电流负向柱 */
export function dualBarVisuOption(
  xData: string[],
  voltage: number[],
  current: number[],
): ChartOption {
  return {
    tooltip: { trigger: 'axis' },
    legend: { top: 0, textStyle: { fontSize: 10 } },
    grid: visuGrid(),
    xAxis: { type: 'category', data: xData, axisLabel: { fontSize: 10 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#eee' } } },
    series: [
      {
        name: 'avg_pack_voltage',
        type: 'bar',
        data: voltage.map((v) => Number(v.toFixed(4))),
        itemStyle: { color: '#3d7eb8' },
        label: { show: true, position: 'top', fontSize: 9, formatter: (params: unknown) => String((params as { value: number }).value) },
      },
      {
        name: 'avg_charge_current',
        type: 'bar',
        data: current.map((v) => Number(v.toFixed(4))),
        itemStyle: { color: '#e8a04c' },
        label: { show: true, position: 'bottom', fontSize: 9 },
      },
    ],
  }
}

/** visu1 右二：双系列堆叠面积 */
export function stackedAreaOption(
  xData: string[],
  series: { name: string; data: number[] }[],
): ChartOption {
  return {
    tooltip: { trigger: 'axis' },
    legend: { top: 0, textStyle: { fontSize: 10 } },
    grid: visuGrid(),
    xAxis: { type: 'category', boundaryGap: false, data: xData, axisLabel: { fontSize: 10 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#eee' } } },
    color: ['#5e9fd4', '#3d7eb8'],
    series: series.map((s) => ({
      name: s.name,
      type: 'line',
      stack: 'total',
      areaStyle: { opacity: 0.55 },
      showSymbol: true,
      symbolSize: 6,
      data: s.data.map((v) => Number(v.toFixed(2))),
      label: { show: true, fontSize: 9, position: 'top' },
    })),
  }
}

/** visu1 左三：带「累计」柱 */
export function barWithTotalOption(
  xData: string[],
  values: number[],
  totalLabel = '累计',
): ChartOption {
  const total = values.reduce((a, b) => a + Math.abs(b), 0)
  const cats = [...xData, totalLabel]
  const data = [...values.map((v) => Number(v.toFixed(2))), Number(total.toFixed(2))]
  return {
    tooltip: { trigger: 'axis' },
    grid: visuGrid(),
    xAxis: { type: 'category', data: cats, axisLabel: { fontSize: 10 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#eee' } } },
    series: [{
      type: 'bar',
      data: data.map((v, i) => ({
        value: v,
        itemStyle: { color: i === data.length - 1 ? '#9aa5b1' : '#6ab04c' },
      })),
      label: { show: true, position: 'top', fontSize: 9 },
    }],
  }
}

/** visu1 右三：柱 + 折线双轴 */
export function dualAxisLineBarOption(
  xData: string[],
  barData: number[],
  lineData: number[],
  barName: string,
  lineName: string,
): ChartOption {
  return {
    tooltip: { trigger: 'axis' },
    legend: { top: 0, textStyle: { fontSize: 10 } },
    grid: chartGrid({ leftYName: barName, rightYName: lineName, top: 40, bottom: 36 }),
    xAxis: { type: 'category', data: xData, axisLabel: { fontSize: 10 } },
    yAxis: [
      valueYAxis(barName, { nameTextStyle: { fontSize: 9 }, splitLine: { lineStyle: { color: '#eee' } } }),
      valueYAxis(lineName, {
        nameTextStyle: { fontSize: 9 },
        splitLine: { show: false },
        position: 'right',
      }),
    ],
    series: [
      {
        name: barName,
        type: 'bar',
        yAxisIndex: 0,
        data: barData.map((v) => Number(v.toFixed(2))),
        itemStyle: { color: '#3d7eb8' },
        barWidth: '36%',
      },
      {
        name: lineName,
        type: 'line',
        yAxisIndex: 1,
        data: lineData.map((v) => Number(v.toFixed(4))),
        itemStyle: { color: '#e85d6a' },
        lineStyle: { width: 2 },
        symbol: 'circle',
        symbolSize: 7,
      },
    ],
  }
}

/** visu1 底栏：正向面积 + 负向面积 */
export function mirroredAreaOption(
  xData: string[],
  positive: number[],
  negative: number[],
): ChartOption {
  return {
    tooltip: { trigger: 'axis' },
    legend: { top: 0, textStyle: { fontSize: 10 } },
    grid: { containLabel: true, left: 16, right: 16, top: 32, bottom: 40 },
    xAxis: { type: 'category', boundaryGap: false, data: xData, axisLabel: { fontSize: 10 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#eee' } } },
    series: [
      {
        name: 'avg_pack_voltage',
        type: 'line',
        areaStyle: { color: 'rgba(232, 160, 76, 0.45)' },
        lineStyle: { color: '#e8a04c' },
        showSymbol: true,
        data: positive.map((v) => Number(v.toFixed(2))),
        label: { show: true, fontSize: 9, position: 'top' },
      },
      {
        name: 'avg_charge_current',
        type: 'line',
        areaStyle: { color: 'rgba(61, 126, 184, 0.45)' },
        lineStyle: { color: '#3d7eb8' },
        showSymbol: true,
        data: negative.map((v) => Number(v.toFixed(4))),
        label: { show: true, fontSize: 9, position: 'bottom' },
      },
    ],
  }
}

export function compactGrid(opt: ChartOption): ChartOption {
  if (opt.title) opt.title = { show: false }
  if (opt.grid && !Array.isArray(opt.grid)) {
    opt.grid = { containLabel: true, ...opt.grid, top: 32, bottom: 32, left: 16, right: 16 }
  }
  if (opt.legend) {
    opt.legend = { ...(opt.legend as object), top: 0, textStyle: { fontSize: 10 }, itemWidth: 12, itemHeight: 8 }
  }
  return opt
}

export function heatmapOption(
  title: string,
  days: string[],
  hours: string[],
  data: [number, number, number][],
): ChartOption {
  return {
    title: { text: title, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      position: 'top',
      formatter: (params: unknown) => {
        const val = (params as { value: [number, number, number] }).value
        const [hi, di, soc] = val
        return `${days[di]} ${hours[hi]}时<br/>SOC: ${soc.toFixed(2)}%`
      },
    },
    grid: { containLabel: true, left: 16, right: 48, top: 60, bottom: 72 },
    xAxis: {
      type: 'category',
      name: '时',
      nameGap: 24,
      data: hours,
      splitArea: { show: true },
    },
    yAxis: {
      type: 'category',
      name: '日期',
      nameGap: 8,
      data: days,
      splitArea: { show: true },
    },
    visualMap: {
      min: 0,
      max: 100,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      text: ['高', '低'],
      formatter: (v: unknown) => `${Number(v).toFixed(0)}%`,
    },
    series: [{
      name: '平均 SOC(%)',
      type: 'heatmap',
      data,
      label: {
        show: data.length <= 30,
        formatter: (params: unknown) => (params as { value: [number, number, number] }).value[2].toFixed(1),
        fontSize: 10,
      },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.4)' } },
    }],
  }
}
