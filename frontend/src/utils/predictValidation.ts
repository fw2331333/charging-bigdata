/** SOC / 会话预测表单边界校验 */

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as const
export type WeekdayLabel = (typeof WEEKDAYS)[number]

export function validateSocBounds(form: {
  min_cell_voltage: number
  max_cell_voltage: number
  min_temperature: number
  max_temperature: number
}): string | null {
  if (form.min_cell_voltage > form.max_cell_voltage) {
    return '最低单体电压不能高于最高单体电压'
  }
  if (form.min_temperature > form.max_temperature) {
    return '最低温度不能高于最高温度'
  }
  return null
}

export function parseDateTime(value: string | Date): Date | null {
  const dt = value instanceof Date ? value : new Date(value)
  return Number.isNaN(dt.getTime()) ? null : dt
}

export function validateSessionDateTime(startAt: string | Date, endAt: string | Date): string | null {
  const start = parseDateTime(startAt)
  const end = parseDateTime(endAt)
  if (!start || !end) return '请填写有效的开始/结束时间'
  if (end <= start) return '结束时间必须晚于开始时间（跨日充电请选择次日日期）'
  const hours = chargeHoursFromRange(start, end)
  if (hours > 48) return '单次充电时长不应超过 48 小时'
  return null
}

export function chargeHoursFromRange(startAt: string | Date, endAt: string | Date): number {
  const start = parseDateTime(startAt)
  const end = parseDateTime(endAt)
  if (!start || !end) return 0
  return (end.getTime() - start.getTime()) / 3_600_000
}

export function weekdayFromStart(startAt: string | Date): WeekdayLabel {
  const start = parseDateTime(startAt)
  if (!start) return 'Mon'
  return WEEKDAYS[(start.getDay() + 6) % 7]
}

export function formatDateTimeLocal(dt: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}T${pad(dt.getHours())}:${pad(dt.getMinutes())}:00`
}

export function defaultOvernightRange(): { start_at: string; end_at: string } {
  const start = new Date()
  start.setHours(22, 0, 0, 0)
  const end = new Date(start)
  end.setDate(end.getDate() + 1)
  end.setHours(6, 0, 0, 0)
  return { start_at: formatDateTimeLocal(start), end_at: formatDateTimeLocal(end) }
}

export function formatDurationHint(startAt: string | Date, endAt: string | Date): string {
  const hours = chargeHoursFromRange(startAt, endAt)
  if (hours <= 0) return ''
  const overnight = parseDateTime(startAt) && parseDateTime(endAt)
    ? parseDateTime(endAt)!.getDate() !== parseDateTime(startAt)!.getDate()
    : false
  const span = overnight ? '（跨日）' : ''
  return `时长约 ${hours.toFixed(1)} 小时${span}`
}
