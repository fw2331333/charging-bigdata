<template>
  <NowUiPageCard page-title="预测的充电费用" page-subtitle="Predict Charging Fee" :section-hint="t('nav.sectionHint')">
    <PredictFeeForm @done="onResult" />
    <div v-if="result" class="now-predict-result">
      预测充电费用：<strong>¥ {{ result.predicted_fee }}</strong>
      <span v-if="result.algorithm">（{{ result.algorithm }}）</span>
    </div>
  </NowUiPageCard>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import NowUiPageCard from '@/components/layout/NowUiPageCard.vue'
import PredictFeeForm from '@/components/predict/PredictFeeForm.vue'
import { useLocale } from '@/composables/useLocale'

const { t } = useLocale()

const result = ref<any>(null)
function onResult(r: any) {
  result.value = r
}
</script>
