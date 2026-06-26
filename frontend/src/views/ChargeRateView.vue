<template>

  <el-card v-loading="loading">

    <template #header>充电速率（MySQL ADS）</template>

    <p class="hint">按一天内小时正序（00→23）；纵轴为 SOC 变化率</p>

    <el-empty v-if="!option && !loading" description="暂无数据" />

    <MrEchart v-if="option" :option="option" />

  </el-card>

</template>



<script setup lang="ts">

import type { EChartsOption } from 'echarts'

import { onMounted, ref } from 'vue'

import MrEchart from '@/components/bi/MrEchart.vue'

import { fetchChargeRateHourly } from '@/api/bi'

import { formatHourAxis, singleLineOption, sortByTimeKey } from '@/utils/mrCharts'



const loading = ref(false)

const option = ref<EChartsOption | null>(null)



onMounted(async () => {

  loading.value = true

  try {

    const rows = sortByTimeKey(await fetchChargeRateHourly(), 'hour_key')

    option.value = singleLineOption(

      '平均充电速率（按小时）',

      rows.map((r) => formatHourAxis(r.hour_key)),

      '速率(%SOC/分钟)',

      rows.map((r) => r.avg_rate),

      { xAxisName: '时', yDecimals: 4 },

    )

  } finally {

    loading.value = false

  }

})

</script>



<style scoped>

.hint { margin: 0 0 12px; color: #909399; font-size: 13px; }

</style>

