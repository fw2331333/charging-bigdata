import request from './request'

export interface SessionBase {
  kwh_total: number
  start_at: string
  end_at: string
  weekday?: string
  platform: string
  facility_type: number
  station_id?: number
}

export interface PredictFeeRequest extends SessionBase {
  charge_time_hrs?: number
}

export interface PredictDurationRequest extends SessionBase {
  charging_fees?: number
}

export interface PredictPlatformRequest {
  kwh_total: number
  charging_fees: number
  charge_time_hrs: number
  start_at: string
  weekday?: string
  facility_type: number
}

export interface PredictSocRequest {
  pack_voltage: number
  charge_current: number
  max_cell_voltage: number
  min_cell_voltage: number
  max_temperature: number
  min_temperature: number
  available_energy: number
  available_capacity: number
}

export interface ModelMetrics {
  metrics: Record<string, Record<string, number | string>>
}

export interface PerformanceReportResponse {
  report: Record<string, any>
}

export const fetchModelMetrics = () => request.get<unknown, ModelMetrics>('/predict/metrics')
export const fetchPerformanceReport = () =>
  request.get<unknown, PerformanceReportResponse>('/predict/performance-report')
export const predictFee = (data: PredictFeeRequest) => request.post('/predict/fee', data)
export const predictDuration = (data: PredictDurationRequest) => request.post('/predict/duration', data)
export const predictPlatform = (data: PredictPlatformRequest) => request.post('/predict/platform', data)
export const predictSoc = (data: PredictSocRequest) => request.post('/predict/soc', data)
