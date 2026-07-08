<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" @submit.prevent="submit">
    <el-form-item label="电量(kWh)" prop="kwh_total">
      <el-input-number v-model="form.kwh_total" :min="0" />
    </el-form-item>
    <SessionDateTimeFields
      v-model:start-at="form.start_at"
      v-model:end-at="form.end_at"
      v-model:weekday="form.weekday"
    />
    <el-form-item label="充电时长(h)" prop="charge_time_hrs">
      <el-input-number v-model="form.charge_time_hrs" :min="0" :step="0.1" clearable />
      <span class="field-hint">留空则按起止时间自动计算</span>
    </el-form-item>
    <el-form-item label="星期" prop="weekday">
      <el-select v-model="form.weekday"><el-option v-for="d in days" :key="d" :label="d" :value="d" /></el-select>
    </el-form-item>
    <el-form-item label="平台" prop="platform">
      <el-select v-model="form.platform"><el-option label="android" value="android" /><el-option label="ios" value="ios" /></el-select>
    </el-form-item>
    <el-form-item label="设备类型" prop="facility_type">
      <el-input-number v-model="form.facility_type" :min="0" />
    </el-form-item>
    <el-button type="primary" native-type="submit" :loading="loading">Predict</el-button>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { predictFee } from '@/api/predict'
import SessionDateTimeFields from '@/components/predict/SessionDateTimeFields.vue'
import {
  chargeHoursFromRange,
  defaultOvernightRange,
  validateSessionDateTime,
  weekdayFromStart,
} from '@/utils/predictValidation'

const emit = defineEmits<{ done: [any] }>()
const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
const loading = ref(false)
const formRef = ref<FormInstance>()
const defaults = defaultOvernightRange()
const form = reactive({
  kwh_total: 30,
  start_at: defaults.start_at,
  end_at: defaults.end_at,
  charge_time_hrs: null as number | null,
  weekday: weekdayFromStart(defaults.start_at),
  platform: 'android',
  facility_type: 3,
  station_id: 0,
})

const timeValidator = () => (_rule: unknown, _value: unknown, callback: (err?: Error) => void) => {
  const msg = validateSessionDateTime(form.start_at, form.end_at)
  if (msg) callback(new Error(msg))
  else callback()
}

const rules: FormRules = {
  start_at: [{ validator: timeValidator(), trigger: 'change' }],
  end_at: [{ validator: timeValidator(), trigger: 'change' }],
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const payload = {
      ...form,
      charge_time_hrs: form.charge_time_hrs ?? chargeHoursFromRange(form.start_at, form.end_at),
    }
    emit('done', await predictFee(payload))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.field-hint {
  margin-left: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
