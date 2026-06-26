/** MapReduce 汇总 BI（MySQL → API） */
import request from './request'

export interface VoltageCurrentItem {
  record_hour: string
  avg_pack_voltage: number
  avg_charge_current: number
}

export interface CellVoltageRangeItem {
  record_hour: string
  max_cell_voltage: number
  min_cell_voltage: number
}

export interface TemperatureItem {
  record_time: string
  max_temperature: number
  min_temperature: number
}

export interface EnergyCapacityItem {
  record_hour: string
  avg_available_energy: number
  avg_available_capacity: number
}

export interface ChargeCurrentStatsItem {
  record_hour: string
  avg_charge_current: number
  max_charge_current: number
}

export interface VoltageCurrentRelationItem {
  record_time: string
  pack_voltage: number
  charge_current: number
}

export interface SocTemperatureItem {
  soc_bucket: string
  avg_max_temperature: number
  avg_min_temperature: number
}

export const fetchVoltageCurrent = (limit = 500) =>
  request.get<unknown, VoltageCurrentItem[]>('/bi/voltage-current', { params: { limit } })

export const fetchCellVoltageRange = (limit = 500) =>
  request.get<unknown, CellVoltageRangeItem[]>('/bi/cell-voltage-range', { params: { limit } })

export const fetchTemperature = (limit = 2000) =>
  request.get<unknown, TemperatureItem[]>('/bi/temperature', { params: { limit } })

export const fetchEnergyCapacity = (limit = 500) =>
  request.get<unknown, EnergyCapacityItem[]>('/bi/energy-capacity', { params: { limit } })

export const fetchChargeCurrentStats = (limit = 500) =>
  request.get<unknown, ChargeCurrentStatsItem[]>('/bi/charge-current-stats', { params: { limit } })

export const fetchVoltageCurrentRelation = (limit = 2000) =>
  request.get<unknown, VoltageCurrentRelationItem[]>('/bi/voltage-current-relation', { params: { limit } })

export const fetchSocTemperature = (limit = 50) =>
  request.get<unknown, SocTemperatureItem[]>('/bi/soc-temperature', { params: { limit } })

export interface SocHourlyItem {
  time_key: string
  avg_soc: number
}

export interface ChargingDailyItem {
  record_date: string
  charge_count: number
}

export interface ChargingMonthlyItem {
  record_month: string
  charge_count: number
}

export interface ChargeRateHourlyItem {
  hour_key: string
  avg_rate: number
}

export interface SocHeatmapItem {
  record_day: string
  hour_key: string
  avg_soc: number
}

export const fetchSocHourly = (limit = 500) =>
  request.get<unknown, SocHourlyItem[]>('/bi/soc-hourly', { params: { limit } })

export const fetchChargingDaily = (limit = 500) =>
  request.get<unknown, ChargingDailyItem[]>('/bi/charging-daily', { params: { limit } })

export const fetchChargingMonthly = (limit = 120) =>
  request.get<unknown, ChargingMonthlyItem[]>('/bi/charging-monthly', { params: { limit } })

export const fetchChargeRateHourly = (limit = 48) =>
  request.get<unknown, ChargeRateHourlyItem[]>('/bi/charge-rate-hourly', { params: { limit } })

export const fetchSocHeatmap = (limit = 5000) =>
  request.get<unknown, SocHeatmapItem[]>('/bi/soc-heatmap', { params: { limit } })
