<template>
  <NowUiPageCard
    v-loading="loading"
    page-title="性能指标分类分析报告"
    page-subtitle="Classification Report"
    :section-hint="t('nav.sectionHint')"
  >
    <el-alert
      v-if="!hasPerformance && !loading"
      type="warning"
      :closable="false"
      title="未加载电池性能分类报告，请运行 analytics/scripts/ds_battery7_1.py 生成 performance_report.json"
      class="mb"
    />

    <template v-if="performance">
      <el-descriptions :column="3" border class="mb">
        <el-descriptions-item label="准确率">
          {{ performance.accuracy_percent != null ? `${performance.accuracy_percent}%` : '—' }}
        </el-descriptions-item>
        <el-descriptions-item label="样本数">{{ performance.samples ?? '—' }}</el-descriptions-item>
        <el-descriptions-item label="特征">
          {{ (performance.features ?? []).join(', ') || '—' }}
        </el-descriptions-item>
        <el-descriptions-item label="Macro F1">{{ performance.macro_avg?.f1_score ?? '—' }}</el-descriptions-item>
        <el-descriptions-item label="Weighted F1">{{ performance.weighted_avg?.f1_score ?? '—' }}</el-descriptions-item>
        <el-descriptions-item label="算法">
          {{ performance.algorithm }} (n={{ performance.n_estimators }})
        </el-descriptions-item>
      </el-descriptions>

      <div class="now-chart-grid cols-2">
        <div class="gsap-chart-block">
          <h6>性能指标分类分析报告 (Classification Report)</h6>
          <MrEchart v-if="reportChart" :option="reportChart" />
        </div>
        <div class="gsap-chart-block">
          <h6>混淆矩阵 (Confusion Matrix)</h6>
          <MrEchart v-if="matrixChart" :option="matrixChart" />
          <el-empty v-else description="暂无混淆矩阵数据" />
        </div>
      </div>

      <el-table v-if="performance.per_class?.length" :data="performance.per_class" border class="mb" size="small">
        <el-table-column prop="class" label="类别" width="120" />
        <el-table-column prop="precision" label="Precision" />
        <el-table-column prop="recall" label="Recall" />
        <el-table-column prop="f1_score" label="F1-score" />
        <el-table-column prop="support" label="Support" />
      </el-table>

      <el-collapse v-if="performance.classification_report_text">
        <el-collapse-item title="完整 Classification Report 文本" name="text">
          <pre class="report-text">{{ performance.classification_report_text }}</pre>
        </el-collapse-item>
      </el-collapse>
    </template>

    <el-divider v-if="performance && metrics">预测模型评估指标</el-divider>

    <el-alert
      v-if="!metrics && !loading && !performance"
      type="info"
      :closable="false"
      title="未加载预测模型指标，请先训练模型"
    />
    <el-descriptions v-if="metrics" :column="2" border>
      <el-descriptions-item label="费用模型 R²（测试）">
        {{ metrics.fee?.test_r2 ?? metrics.fee?.r2 ?? '—' }}
      </el-descriptions-item>
      <el-descriptions-item label="费用拟合状态">{{ fitLabel(metrics.fee?.fit_status) }}</el-descriptions-item>
      <el-descriptions-item label="时长模型 R²（测试）">
        {{ metrics.duration?.test_r2 ?? metrics.duration?.r2 ?? '—' }}
      </el-descriptions-item>
      <el-descriptions-item label="时长拟合状态">{{ fitLabel(metrics.duration?.fit_status) }}</el-descriptions-item>
      <el-descriptions-item label="平台准确率（测试）">{{ metrics.platform?.accuracy ?? '—' }}</el-descriptions-item>
      <el-descriptions-item label="平台拟合状态">{{ fitLabel(metrics.platform?.fit_status) }}</el-descriptions-item>
      <el-descriptions-item label="SOC 模型 R²（测试）">
        {{ metrics.soc?.test_r2 ?? metrics.soc?.r2 ?? '—' }}
      </el-descriptions-item>
      <el-descriptions-item label="SOC 拟合状态">{{ fitLabel(metrics.soc?.fit_status) }}</el-descriptions-item>
    </el-descriptions>
  </NowUiPageCard>
</template>

<script setup lang="ts">
defineOptions({ name: 'MetricsReportView' })

import type { ChartOption } from '@/utils/mrCharts'
import { computed, onMounted, ref } from 'vue'
import MrEchart from '@/components/bi/AsyncMrEchart'
import NowUiPageCard from '@/components/layout/NowUiPageCard.vue'
import { useLocale } from '@/composables/useLocale'
import { fetchModelMetrics, fetchPerformanceReport } from '@/api/predict'
import {
  classificationReportBarOption,
  confusionMatrixHeatmapOption,
  type PerformanceReport,
} from '@/utils/performanceCharts'

const { t } = useLocale()

const loading = ref(false)
const metrics = ref<Record<string, any> | null>(null)
const performance = ref<PerformanceReport | null>(null)
const reportChart = ref<ChartOption | null>(null)
const matrixChart = ref<ChartOption | null>(null)

const hasPerformance = computed(() => Boolean(performance.value?.per_class?.length))

function fitLabel(status?: string) {
  if (status === 'overfit_risk') return '过拟合风险'
  if (status === 'underfit_risk') return '欠拟合风险'
  if (status === 'ok') return '正常'
  return '—'
}

onMounted(async () => {
  loading.value = true
  try {
    const [metricsRes, perfRes] = await Promise.allSettled([
      fetchModelMetrics(),
      fetchPerformanceReport(),
    ])
    if (metricsRes.status === 'fulfilled') {
      metrics.value = metricsRes.value.metrics
    }
    if (perfRes.status === 'fulfilled' && perfRes.value.report?.per_class) {
      performance.value = perfRes.value.report as PerformanceReport
      reportChart.value = classificationReportBarOption(performance.value)
      matrixChart.value = confusionMatrixHeatmapOption(performance.value)
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.mb {
  margin-bottom: 20px;
}
.report-text {
  margin: 0;
  white-space: pre-wrap;
  font-size: 12px;
  line-height: 1.5;
  color: var(--el-text-color-regular);
}
</style>
