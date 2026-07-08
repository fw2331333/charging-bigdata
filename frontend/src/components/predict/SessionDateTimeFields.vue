<template>
  <el-form-item label="开始时间" :prop="startProp">
    <el-date-picker
      v-model="startAt"
      type="datetime"
      placeholder="选择开始日期时间"
      format="YYYY-MM-DD HH:mm"
      value-format="YYYY-MM-DDTHH:mm:ss"
      style="width: 100%"
      @change="onStartChange"
    />
  </el-form-item>
  <el-form-item label="结束时间" :prop="endProp">
    <el-date-picker
      v-model="endAt"
      type="datetime"
      placeholder="选择结束日期时间（可跨日）"
      format="YYYY-MM-DD HH:mm"
      value-format="YYYY-MM-DDTHH:mm:ss"
      style="width: 100%"
      @change="emitDuration"
    />
  </el-form-item>
  <p v-if="durationHint" class="session-duration-hint">{{ durationHint }}</p>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  formatDurationHint,
  validateSessionDateTime,
  weekdayFromStart,
} from '@/utils/predictValidation'

const props = withDefaults(
  defineProps<{
    startProp?: string
    endProp?: string
    syncWeekday?: boolean
  }>(),
  { startProp: 'start_at', endProp: 'end_at', syncWeekday: true },
)

const startAt = defineModel<string>('startAt', { required: true })
const endAt = defineModel<string>('endAt', { required: true })
const weekday = defineModel<string>('weekday', { required: false })

const durationHint = computed(() => {
  const msg = validateSessionDateTime(startAt.value, endAt.value)
  if (msg) return msg
  return formatDurationHint(startAt.value, endAt.value)
})

function onStartChange() {
  if (props.syncWeekday && weekday.value !== undefined) {
    weekday.value = weekdayFromStart(startAt.value)
  }
  emitDuration()
}

function emitDuration() {
  // durationHint 为 computed，随 v-model 自动更新
}
</script>

<style scoped>
.session-duration-hint {
  margin: -8px 0 12px 120px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
