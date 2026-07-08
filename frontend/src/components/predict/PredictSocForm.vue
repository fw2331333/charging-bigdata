<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="150px" @submit.prevent="submit">
    <el-form-item label="组电压(V)" prop="pack_voltage">
      <el-input-number v-model="form.pack_voltage" :step="0.1" />
    </el-form-item>
    <el-form-item label="充电电流(A)" prop="charge_current">
      <el-input-number v-model="form.charge_current" :step="0.1" />
      <span class="field-hint">充电时电流常为负值</span>
    </el-form-item>
    <el-form-item label="最高单体电压(V)" prop="max_cell_voltage">
      <el-input-number v-model="form.max_cell_voltage" :step="0.01" :min="form.min_cell_voltage" />
    </el-form-item>
    <el-form-item label="最低单体电压(V)" prop="min_cell_voltage">
      <el-input-number v-model="form.min_cell_voltage" :step="0.01" :max="form.max_cell_voltage" />
    </el-form-item>
    <el-form-item label="最高温度(℃)" prop="max_temperature">
      <el-input-number v-model="form.max_temperature" :step="0.1" :min="form.min_temperature" />
    </el-form-item>
    <el-form-item label="最低温度(℃)" prop="min_temperature">
      <el-input-number v-model="form.min_temperature" :step="0.1" :max="form.max_temperature" />
    </el-form-item>
    <el-form-item label="可用能量(kWh)" prop="available_energy">
      <el-input-number v-model="form.available_energy" :min="0" :step="0.1" />
    </el-form-item>
    <el-form-item label="可用容量(Ah)" prop="available_capacity">
      <el-input-number v-model="form.available_capacity" :min="0" :step="0.1" />
    </el-form-item>
    <el-button type="primary" native-type="submit" :loading="loading">Predict</el-button>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { predictSoc } from '@/api/predict'
import { validateSocBounds } from '@/utils/predictValidation'

const emit = defineEmits<{ done: [any] }>()
const loading = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({
  pack_voltage: 320,
  charge_current: -20,
  max_cell_voltage: 3.6,
  min_cell_voltage: 3.5,
  max_temperature: 35,
  min_temperature: 30,
  available_energy: 50,
  available_capacity: 100,
})

const boundValidator = () => (_rule: unknown, _value: unknown, callback: (err?: Error) => void) => {
  const msg = validateSocBounds(form)
  if (msg) callback(new Error(msg))
  else callback()
}

const rules: FormRules = {
  min_cell_voltage: [{ validator: boundValidator(), trigger: 'change' }],
  max_cell_voltage: [{ validator: boundValidator(), trigger: 'change' }],
  min_temperature: [{ validator: boundValidator(), trigger: 'change' }],
  max_temperature: [{ validator: boundValidator(), trigger: 'change' }],
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  const msg = validateSocBounds(form)
  if (msg) {
    ElMessage.warning(msg)
    return
  }
  loading.value = true
  try {
    emit('done', await predictSoc({ ...form }))
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
