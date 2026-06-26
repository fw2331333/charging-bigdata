<template>

  <el-card v-loading="loading">

    <template #header>SOC 分析（MySQL ADS）</template>

    <p class="hint">按记录时间正序（左→右）：Spark SQL 聚合 → MySQL <code>t_soc_hourly</code></p>

    <el-empty v-if="!option && !loading" description="暂无数据，请运行 ADS ETL" />

    <MrEchart v-if="option" :option="option" />

  </el-card>

</template>



<script setup lang="ts">

import type { EChartsOption } from 'echarts'

import { onMounted, ref } from 'vue'

import MrEchart from '@/components/bi/MrEchart.vue'

import { fetchSocHourly } from '@/api/bi'

import { formatMrTime, singleLineOption, sortByTimeKey } from '@/utils/mrCharts'



const loading = ref(false)

const option = ref<EChartsOption | null>(null)



onMounted(async () => {

  loading.value = true

  try {

    const rows = sortByTimeKey(await fetchSocHourly(), 'time_key')

    option.value = singleLineOption(

      '电池 SOC 随时间变化',

      rows.map((r) => formatMrTime(r.time_key)),

      'SOC(%)',

      rows.map((r) => r.avg_soc),

      { xAxisName: '时间', yDecimals: 2 },

    )

  } finally {

    loading.value = false

  }

})

</script>



<style scoped>

.hint { margin: 0 0 12px; color: #909399; font-size: 13px; }

</style>

