<template>
  <el-form label-width="140px" @submit.prevent="submit">
    <el-form-item label="组电压(V)"><el-input-number v-model="form.pack_voltage" :step="0.1" /></el-form-item>
    <el-form-item label="充电电流(A)"><el-input-number v-model="form.charge_current" :step="0.1" /></el-form-item>
    <el-form-item label="最高/最低单体电压">
      <el-input-number v-model="form.max_cell_voltage" :step="0.01" /> /
      <el-input-number v-model="form.min_cell_voltage" :step="0.01" />
    </el-form-item>
    <el-form-item label="最高/最低温度">
      <el-input-number v-model="form.max_temperature" :step="0.1" /> /
      <el-input-number v-model="form.min_temperature" :step="0.1" />
    </el-form-item>
    <el-form-item label="可用能量/容量">
      <el-input-number v-model="form.available_energy" :step="0.1" /> /
      <el-input-number v-model="form.available_capacity" :step="0.1" />
    </el-form-item>
    <el-button type="primary" native-type="submit" :loading="loading">预测 SOC</el-button>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { predictSoc } from '@/api/predict'
const emit = defineEmits<{ done: [any] }>()
const loading = ref(false)
const form = reactive({
  pack_voltage: 320, charge_current: -20, max_cell_voltage: 3.6, min_cell_voltage: 3.5,
  max_temperature: 35, min_temperature: 30, available_energy: 50, available_capacity: 100,
})
async function submit() {
  loading.value = true
  try { emit('done', await predictSoc({ ...form })) } finally { loading.value = false }
}
</script>
