import type { EChartsOption } from 'echarts'

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

export function sortHours(hours: string[]): string[] {
  return [...hours].sort((a, b) => Number(a) - Number(b))
}

function axisLabelInterval(count: number): number | 'auto' {
  if (count <= 12) return 0
  if (count <= 31) return 0
  if (count <= 90) return Math.floor(count / 15)
  return 'auto'
}

export function dualLineOption(
  title: string,
  xData: string[],
  series: { name: string; data: number[]; yAxisIndex?: number }[],
  yAxisNames: string[],
  opts?: { xAxisName?: string; yDecimals?: number },
): EChartsOption {
  const fewPoints = xData.length <= 24
  const dualAxis = yAxisNames.length > 1
  const dec = opts?.yDecimals ?? 2
  return {
    title: { text: title, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      trigger: 'axis',
      valueFormatter: (v) => (typeof v === 'number' ? v.toFixed(dec) : String(v)),
    },
    legend: { top: 28 },
    grid: { left: 64, right: dualAxis ? 64 : 28, top: 72, bottom: xData.length > 12 ? 72 : 56 },
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
    yAxis: yAxisNames.map((name, idx) => ({
      type: 'value',
      name,
      nameGap: 12,
      scale: !fewPoints,
      position: idx === 0 ? 'left' : 'right',
    })),
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
): EChartsOption {
  return {
    title: { text: title, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      trigger: 'item',
      formatter: (p: { value: [number, number] }) =>
        `${xName}: ${p.value[0].toFixed(2)}<br/>${yName}: ${p.value[1].toFixed(2)}`,
    },
    grid: { left: 64, right: 28, top: 56, bottom: 48 },
    xAxis: { type: 'value', name: xName, nameGap: 12, scale: true },
    yAxis: { type: 'value', name: yName, nameGap: 12, scale: true },
    series: [{ type: 'scatter', symbolSize: 6, data: points }],
  }
}

export function barOption(
  title: string,
  categories: string[],
  series: { name: string; data: number[] }[],
  yName = '℃',
): EChartsOption {
  return {
    title: { text: title, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'axis', valueFormatter: (v) => Number(v).toFixed(2) },
    legend: { top: 28 },
    grid: { left: 56, right: 24, top: 72, bottom: 48 },
    xAxis: { type: 'category', name: 'SOC区间(%)', data: categories },
    yAxis: { type: 'value', name: yName, nameGap: 12 },
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
  opts?: { xAxisName?: string; yDecimals?: number },
): EChartsOption {
  const fewPoints = xData.length <= 24
  const dec = opts?.yDecimals ?? 0
  return {
    title: { text: title, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      trigger: 'axis',
      valueFormatter: (v) => Number(v).toFixed(dec),
    },
    grid: { left: 64, right: 28, top: 56, bottom: xData.length > 12 ? 72 : 56 },
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
    yAxis: { type: 'value', name: yName, nameGap: 12, min: 0, scale: !fewPoints && data.length > 24 },
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

export function heatmapOption(
  title: string,
  days: string[],
  hours: string[],
  data: [number, number, number][],
): EChartsOption {
  return {
    title: { text: title, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      position: 'top',
      formatter: (p: { value: [number, number, number] }) => {
        const [hi, di, soc] = p.value
        return `${days[di]} ${hours[hi]}时<br/>SOC: ${soc.toFixed(2)}%`
      },
    },
    grid: { left: 96, right: 48, top: 60, bottom: 56 },
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
      formatter: (v: number) => `${v.toFixed(0)}%`,
    },
    series: [{
      name: '平均 SOC(%)',
      type: 'heatmap',
      data,
      label: {
        show: data.length <= 30,
        formatter: (p: { value: [number, number, number] }) => p.value[2].toFixed(1),
        fontSize: 10,
      },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.4)' } },
    }],
  }
}
