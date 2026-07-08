<template>
  <NowUiPageCard page-title="预测充电时间" page-subtitle="Predict Charging Duration" :section-hint="t('nav.sectionHint')">
    <PredictDurationForm @done="onResult" />
    <div v-if="result" class="now-predict-result">
      预测充电时间：<strong>{{ result.predicted_hours }} 小时</strong>
    </div>
  </NowUiPageCard>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import NowUiPageCard from '@/components/layout/NowUiPageCard.vue'
import PredictDurationForm from '@/components/predict/PredictDurationForm.vue'
import { useLocale } from '@/composables/useLocale'

const { t } = useLocale()

const result = ref<any>(null)
function onResult(r: any) {
  result.value = r
}
</script>
