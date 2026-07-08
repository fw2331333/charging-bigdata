import type { ChartOption } from '@/utils/mrCharts'

export interface PerformanceClassMetric {
  class: string
  class_index: number
  precision: number
  recall: number
  f1_score: number
  support: number
}

export interface PerformanceReport {
  task?: string
  accuracy?: number
  accuracy_percent?: number
  samples?: number
  algorithm?: string
  n_estimators?: number
  target_rule?: string
  features?: string[]
  class_labels?: string[]
  per_class?: PerformanceClassMetric[]
  confusion_matrix?: number[][]
  macro_avg?: { precision: number; recall: number; f1_score: number }
  weighted_avg?: { precision: number; recall: number; f1_score: number }
  classification_report_text?: string
}

/** 手册 §4.6：Precision / Recall / F1-score 分组柱状图 */
export function classificationReportBarOption(report: PerformanceReport): ChartOption {
  const classes = report.per_class ?? []
  const labels = classes.map((c) => c.class)
  return {
    title: { text: 'Classification Report', left: 'center' },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Precision', 'Recall', 'F1-score'], bottom: 0 },
    grid: { left: 48, right: 24, top: 48, bottom: 56 },
    xAxis: {
      type: 'category',
      data: labels,
      name: 'Classes',
      axisTick: { alignWithLabel: true },
    },
    yAxis: { type: 'value', name: 'Scores', min: 0, max: 1 },
    series: [
      {
        name: 'Precision',
        type: 'bar',
        barGap: 0,
        data: classes.map((c) => c.precision),
        itemStyle: { color: '#344675' },
      },
      {
        name: 'Recall',
        type: 'bar',
        data: classes.map((c) => c.recall),
        itemStyle: { color: '#f96332' },
      },
      {
        name: 'F1-score',
        type: 'bar',
        data: classes.map((c) => c.f1_score),
        itemStyle: { color: '#18ce0f' },
      },
    ],
  }
}

/** 手册 §4.6：混淆矩阵热力图 */
export function confusionMatrixHeatmapOption(report: PerformanceReport): ChartOption | null {
  const cm = report.confusion_matrix
  const labels = report.class_labels ?? ['正常', '能量不足']
  if (!cm?.length) return null

  const data: [number, number, number][] = []
  cm.forEach((row, yi) => {
    row.forEach((val, xi) => data.push([xi, yi, val]))
  })
  const maxVal = Math.max(...data.map((d) => d[2]), 1)

  return {
    title: { text: 'Confusion Matrix', left: 'center' },
    tooltip: {
      position: 'top',
      formatter: (p: { data: [number, number, number] }) => {
        const [xi, yi, val] = p.data
        return `真实: ${labels[yi]}<br/>预测: ${labels[xi]}<br/>数量: ${val}`
      },
    },
    grid: { left: 80, right: 40, top: 48, bottom: 72 },
    xAxis: {
      type: 'category',
      data: labels,
      name: 'Predicted',
      splitArea: { show: true },
    },
    yAxis: {
      type: 'category',
      data: [...labels].reverse(),
      name: 'Truth',
      splitArea: { show: true },
    },
    visualMap: {
      min: 0,
      max: maxVal,
      calculable: false,
      orient: 'horizontal',
      left: 'center',
      bottom: 8,
      inRange: { color: ['#f5f7fa', '#344675'] },
      show: false,
    },
    series: [
      {
        type: 'heatmap',
        data: data.map(([x, y, v]) => [x, labels.length - 1 - y, v]),
        label: { show: true, color: '#111' },
        emphasis: {
          itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.25)' },
        },
      },
    ],
  }
}
