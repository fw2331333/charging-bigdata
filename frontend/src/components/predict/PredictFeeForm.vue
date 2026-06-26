<template>
  <el-form label-width="120px" @submit.prevent="submit">
    <el-form-item label="电量(kWh)"><el-input-number v-model="form.kwh_total" :min="0" /></el-form-item>
    <el-form-item label="开始/结束小时">
      <el-input-number v-model="form.start_time" :min="0" :max="23" /> -
      <el-input-number v-model="form.end_time" :min="0" :max="23" />
    </el-form-item>
    <el-form-item label="充电时长(h)"><el-input-number v-model="form.charge_time_hrs" :min="0" :step="0.1" /></el-form-item>
    <el-form-item label="星期"><el-select v-model="form.weekday"><el-option v-for="d in days" :key="d" :label="d" :value="d" /></el-select></el-form-item>
    <el-form-item label="平台"><el-select v-model="form.platform"><el-option label="android" value="android" /><el-option label="ios" value="ios" /></el-select></el-form-item>
    <el-form-item label="设备类型"><el-input-number v-model="form.facility_type" :min="0" /></el-form-item>
    <el-button type="primary" native-type="submit" :loading="loading">预测费用</el-button>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { predictFee } from '@/api/predict'
const emit = defineEmits<{ done: [any] }>()
const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
const loading = ref(false)
const form = reactive({ kwh_total: 30, start_time: 8, end_time: 10, charge_time_hrs: 2, weekday: 'Mon', platform: 'android', facility_type: 3, station_id: 0 })
async function submit() {
  loading.value = true
  try { emit('done', await predictFee({ ...form })) } finally { loading.value = false }
}
</script>
