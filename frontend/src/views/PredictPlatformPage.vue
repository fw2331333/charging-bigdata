<template>
  <NowUiPageCard page-title="预测充电平台的选用" page-subtitle="Predict Charging Platform" :section-hint="t('nav.sectionHint')">
    <PredictPlatformForm @done="onResult" />
    <div v-if="result" class="now-predict-result">
      预测充电平台：<strong>{{ result.predicted_platform }}</strong>
    </div>
  </NowUiPageCard>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import NowUiPageCard from '@/components/layout/NowUiPageCard.vue'
import PredictPlatformForm from '@/components/predict/PredictPlatformForm.vue'
import { useLocale } from '@/composables/useLocale'

const { t } = useLocale()

const result = ref<any>(null)
function onResult(r: any) {
  result.value = r
}
</script>
