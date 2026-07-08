<template>
  <NowUiPageCard
    page-title="预测剩余电量"
    page-subtitle="SOC, State of Charge"
    :section-hint="t('nav.sectionHint')"
  >
    <PredictSocForm @done="onResult" />
    <div v-if="result" class="now-predict-result">
      预测剩余电量 (SOC, State of Charge)：
      <strong>{{ result.predicted_soc }}%</strong>
    </div>
  </NowUiPageCard>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import NowUiPageCard from '@/components/layout/NowUiPageCard.vue'
import PredictSocForm from '@/components/predict/PredictSocForm.vue'
import { useLocale } from '@/composables/useLocale'

const { t } = useLocale()

const result = ref<any>(null)
function onResult(r: any) {
  result.value = r
}
</script>
