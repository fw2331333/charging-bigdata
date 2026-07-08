<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" @submit.prevent="submit">
    <el-form-item label="电量(kWh)"><el-input-number v-model="form.kwh_total" :min="0" /></el-form-item>
    <el-form-item label="费用(元)"><el-input-number v-model="form.charging_fees" :min="0" :step="0.01" /></el-form-item>
    <el-form-item label="充电时长(h)"><el-input-number v-model="form.charge_time_hrs" :min="0" :step="0.1" /></el-form-item>
    <el-form-item label="开始时间" prop="start_at">
      <el-date-picker
        v-model="form.start_at"
        type="datetime"
        placeholder="选择开始日期时间"
        format="YYYY-MM-DD HH:mm"
        value-format="YYYY-MM-DDTHH:mm:ss"
        style="width: 100%"
        @change="onStartChange"
      />
    </el-form-item>
    <el-form-item label="星期">
      <el-select v-model="form.weekday"><el-option v-for="d in days" :key="d" :label="d" :value="d" /></el-select>
    </el-form-item>
    <el-form-item label="设备类型"><el-input-number v-model="form.facility_type" :min="0" /></el-form-item>
    <el-button type="primary" native-type="submit" :loading="loading">Predict</el-button>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { predictPlatform } from '@/api/predict'
import { formatDateTimeLocal, weekdayFromStart } from '@/utils/predictValidation'

const emit = defineEmits<{ done: [any] }>()
const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
const loading = ref(false)
const formRef = ref<FormInstance>()
const startDefault = (() => {
  const dt = new Date()
  dt.setHours(8, 0, 0, 0)
  return formatDateTimeLocal(dt)
})()
const form = reactive({
  kwh_total: 30,
  charging_fees: 1.5,
  charge_time_hrs: 2,
  start_at: startDefault,
  weekday: weekdayFromStart(startDefault),
  facility_type: 3,
})

const rules: FormRules = {
  start_at: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
}

function onStartChange() {
  form.weekday = weekdayFromStart(form.start_at)
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try { emit('done', await predictPlatform({ ...form })) } finally { loading.value = false }
}
</script>
