<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">充电桩大数据</div>
      <el-menu :default-active="route.path" router>
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/mr-bi">MR 汇总 BI</el-menu-item>
        <el-menu-item index="/soc">SOC 分析</el-menu-item>
        <el-menu-item index="/soc-heatmap">SOC 热力图</el-menu-item>
        <el-menu-item index="/charging">充电次数</el-menu-item>
        <el-menu-item index="/charge-rate">充电速率</el-menu-item>
        <el-menu-item index="/predict">四项预测</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>新能源充电桩大数据分析系统</span>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<style scoped>
.layout { min-height: 100vh; }
.aside { background: #1f2d3d; color: #fff; }
.logo { padding: 20px 16px; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.1); }
.header { display: flex; align-items: center; background: #fff; border-bottom: 1px solid #ebeef5; }
</style>
