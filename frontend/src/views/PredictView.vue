<template>
  <el-card>
    <template #header>机器学习四项预测</template>
    <el-alert v-if="metrics" type="info" :closable="false" class="mb">
      模型评估：费用 R²={{ metrics.fee?.r2 }}（{{ feeAlgoLabel }}）；
      时长 R²={{ metrics.duration?.r2 }}；
      平台 Acc={{ metrics.platform?.accuracy }}；SOC R²={{ metrics.soc?.r2 }}
    </el-alert>
    <el-alert
      v-if="feeComparison"
      type="warning"
      :closable="false"
      class="mb"
      :title="`费用模型对比：线性回归 R²=${feeComparison.linear_regression?.r2}，XGBoost R²=${feeComparison.xgboost?.r2}，入选 ${feeComparison.selected}`"
    />
    <el-tabs v-model="tab">
      <el-tab-pane label="充电费用" name="fee">
        <PredictFeeForm @done="onFee" />
        <el-alert v-if="fee" :title="`预测费用：¥ ${fee.predicted_fee}${fee.algorithm ? '（' + fee.algorithm + '）' : ''}`" type="success" />
      </el-tab-pane>
      <el-tab-pane label="充电时间" name="duration">
        <PredictDurationForm @done="onDuration" />
        <el-alert v-if="duration" :title="`预测时长：${duration.predicted_hours} 小时`" type="success" />
      </el-tab-pane>
      <el-tab-pane label="用户平台" name="platform">
        <PredictPlatformForm @done="onPlatform" />
        <el-alert v-if="platform" :title="`预测平台：${platform.predicted_platform}`" type="success" />
      </el-tab-pane>
      <el-tab-pane label="剩余电量SOC" name="soc">
        <PredictSocForm @done="onSoc" />
        <el-alert v-if="soc" :title="`预测 SOC：${soc.predicted_soc}%`" type="success" />
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchModelMetrics } from '@/api/predict'
import PredictFeeForm from '@/components/predict/PredictFeeForm.vue'
import PredictDurationForm from '@/components/predict/PredictDurationForm.vue'
import PredictPlatformForm from '@/components/predict/PredictPlatformForm.vue'
import PredictSocForm from '@/components/predict/PredictSocForm.vue'

const tab = ref('fee')
const feeComparison = computed(() => metrics.value?.fee?.model_comparison ?? null)
const feeAlgoLabel = computed(() => {
  const a = metrics.value?.fee?.algorithm
  if (a === 'linear_regression') return '线性回归'
  if (a === 'xgboost') return 'XGBoost'
  return a || '—'
})
const metrics = ref<Record<string, any> | null>(null)
const fee = ref<any>(null)
const duration = ref<any>(null)
const platform = ref<any>(null)
const soc = ref<any>(null)

onMounted(async () => {
  try {
    const res = await fetchModelMetrics()
    metrics.value = res.metrics
  } catch { /* ignore */ }
})

const onFee = (r: any) => { fee.value = r }
const onDuration = (r: any) => { duration.value = r }
const onPlatform = (r: any) => { platform.value = r }
const onSoc = (r: any) => { soc.value = r }
</script>

<style scoped>.mb { margin-bottom: 16px; }</style>
