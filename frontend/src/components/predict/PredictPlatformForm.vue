<template>
  <el-form label-width="120px" @submit.prevent="submit">
    <el-form-item label="电量(kWh)"><el-input-number v-model="form.kwh_total" :min="0" /></el-form-item>
    <el-form-item label="费用"><el-input-number v-model="form.charging_fees" :min="0" :step="0.01" /></el-form-item>
    <el-form-item label="充电时长(h)"><el-input-number v-model="form.charge_time_hrs" :min="0" :step="0.1" /></el-form-item>
    <el-form-item label="开始小时"><el-input-number v-model="form.start_time" :min="0" :max="23" /></el-form-item>
    <el-form-item label="星期"><el-select v-model="form.weekday"><el-option v-for="d in days" :key="d" :label="d" :value="d" /></el-select></el-form-item>
    <el-form-item label="设备类型"><el-input-number v-model="form.facility_type" :min="0" /></el-form-item>
    <el-button type="primary" native-type="submit" :loading="loading">预测平台</el-button>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { predictPlatform } from '@/api/predict'
const emit = defineEmits<{ done: [any] }>()
const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
const loading = ref(false)
const form = reactive({ kwh_total: 30, charging_fees: 1.5, charge_time_hrs: 2, start_time: 8, weekday: 'Mon', facility_type: 3 })
async function submit() {
  loading.value = true
  try { emit('done', await predictPlatform({ ...form })) } finally { loading.value = false }
}
</script>
