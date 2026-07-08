"""预测请求与响应模型（四项预测均已实现）。"""

from datetime import datetime, timedelta

from pydantic import BaseModel, Field, model_validator


class SessionPredictBase(BaseModel):
    kwh_total: float = Field(..., ge=0, description="充电电量 kWh")
    start_at: datetime = Field(..., description="充电开始日期时间")
    end_at: datetime = Field(..., description="充电结束日期时间（可跨日至次日）")
    weekday: str | None = Field(None, description="星期 Mon~Sun，默认从开始时间推导")
    platform: str = Field(..., description="android/ios")
    facility_type: int = Field(..., ge=0, description="设备类型")
    station_id: int = Field(0, ge=0, description="站点ID")

    @model_validator(mode="after")
    def check_datetime_order(self) -> "SessionPredictBase":
        if self.end_at <= self.start_at:
            raise ValueError("结束时间必须晚于开始时间（跨日充电请选择次日日期）")
        if self.end_at - self.start_at > timedelta(hours=48):
            raise ValueError("单次充电时长不应超过 48 小时")
        return self


class PredictFeeRequest(SessionPredictBase):
    charge_time_hrs: float | None = Field(
        None, ge=0, description="充电时长 h；留空则按起止时间自动计算"
    )


class PredictDurationRequest(SessionPredictBase):
    charging_fees: float = Field(0, ge=0, description="已知费用 元(可选特征)")


class PredictPlatformRequest(BaseModel):
    kwh_total: float = Field(..., ge=0, description="充电电量 kWh")
    charging_fees: float = Field(..., ge=0, description="充电费用 元")
    charge_time_hrs: float = Field(..., ge=0, description="充电时长 h")
    start_at: datetime = Field(..., description="充电开始日期时间")
    weekday: str | None = Field(None, description="星期 Mon~Sun，默认从开始时间推导")
    facility_type: int = Field(..., ge=0)


class PredictSocRequest(BaseModel):
    pack_voltage: float = Field(..., description="组电压 V")
    charge_current: float = Field(..., description="充电电流 A（充电常为负值）")
    max_cell_voltage: float = Field(..., description="最高单体电压 V")
    min_cell_voltage: float = Field(..., description="最低单体电压 V")
    max_temperature: float = Field(..., description="最高温度 ℃")
    min_temperature: float = Field(..., description="最低温度 ℃")
    available_energy: float = Field(..., ge=0, description="可用能量 kWh")
    available_capacity: float = Field(..., ge=0, description="可用容量 Ah")

    @model_validator(mode="after")
    def check_soc_bounds(self) -> "PredictSocRequest":
        if self.min_cell_voltage > self.max_cell_voltage:
            raise ValueError("最低单体电压不能高于最高单体电压")
        if self.min_temperature > self.max_temperature:
            raise ValueError("最低温度不能高于最高温度")
        return self


class PredictFeeResponse(BaseModel):
    predicted_fee: float
    algorithm: str = Field("", description="入选的费用预测算法：linear_regression 或 xgboost")
    message: str = "ok"


class PredictDurationResponse(BaseModel):
    predicted_hours: float
    message: str = "ok"


class PredictPlatformResponse(BaseModel):
    predicted_platform: str
    message: str = "ok"


class PredictSocResponse(BaseModel):
    predicted_soc: float
    message: str = "ok"


class ModelMetricsResponse(BaseModel):
    metrics: dict


class PerformanceReportResponse(BaseModel):
    """手册 §4.6 电池故障分类性能指标。"""
    report: dict
