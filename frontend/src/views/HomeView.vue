<template>
  <el-card>
    <template #header>系统概览</template>
    <p>
      企业分层：<strong>HDFS 明细</strong> → MapReduce（课程）+ <strong>Spark SQL ADS</strong> → <strong>MySQL 汇总</strong> → 全部大屏 ECharts 只读 MySQL。
    </p>
    <el-row :gutter="12">
      <el-col :span="8" v-for="item in items" :key="item.path">
        <el-card shadow="hover" class="nav-card" @click="$router.push(item.path)">{{ item.label }}</el-card>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
const items = [
  { path: '/mr-bi', label: 'MR 汇总 BI（MySQL）' },
  { path: '/soc', label: 'SOC 折线图' },
  { path: '/soc-heatmap', label: 'SOC 热力图' },
  { path: '/charging', label: '充电次数' },
  { path: '/charge-rate', label: '充电速率' },
  { path: '/predict', label: '四项 ML 预测' },
]
</script>

<style scoped>
.nav-card { cursor: pointer; text-align: center; margin-bottom: 12px; }
</style>
