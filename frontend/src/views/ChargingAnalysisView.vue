<template>

  <el-card v-loading="loading">

    <template #header>充电次数分析（MySQL ADS）</template>

    <p class="hint">数据来源 nvv2t 充电会话（created，2014–2015）；SOC 等电池分析来自 dsv13r2（2019-07）</p>

    <el-row :gutter="16">

      <el-col :span="12">

        <MrEchart v-if="dailyOption" :option="dailyOption" />

        <el-empty v-else description="暂无每日数据" />

      </el-col>

      <el-col :span="12">

        <MrEchart v-if="monthlyOption" :option="monthlyOption" />

        <el-empty v-else description="暂无每月数据" />

      </el-col>

    </el-row>

  </el-card>

</template>



<script setup lang="ts">

import type { EChartsOption } from 'echarts'

import { onMounted, ref } from 'vue'

import MrEchart from '@/components/bi/MrEchart.vue'

import { fetchChargingDaily, fetchChargingMonthly } from '@/api/bi'

import {

  formatChargingDate,

  formatChargingMonth,

  singleLineOption,

  sortByTimeKey,

} from '@/utils/mrCharts'



const loading = ref(false)

const dailyOption = ref<EChartsOption | null>(null)

const monthlyOption = ref<EChartsOption | null>(null)



onMounted(async () => {

  loading.value = true

  try {

    const daily = sortByTimeKey(await fetchChargingDaily(), 'record_date')

    const monthly = sortByTimeKey(await fetchChargingMonthly(), 'record_month')

    dailyOption.value = singleLineOption(

      '每日充电次数',

      daily.map((r) => formatChargingDate(r.record_date)),

      '充电次数(次)',

      daily.map((r) => r.charge_count),

      { xAxisName: '日期', yDecimals: 0 },

    )

    monthlyOption.value = singleLineOption(

      '每月充电次数',

      monthly.map((r) => formatChargingMonth(r.record_month)),

      '充电次数(次)',

      monthly.map((r) => r.charge_count),

      { xAxisName: '月份', yDecimals: 0 },

    )

  } finally {

    loading.value = false

  }

})

</script>



<style scoped>

.hint { margin: 0 0 12px; color: #909399; font-size: 13px; }

</style>

