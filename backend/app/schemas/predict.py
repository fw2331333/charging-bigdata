"""预测请求与响应模型（四项预测均已实现）。"""

from pydantic import BaseModel, Field


class SessionPredictBase(BaseModel):
    kwh_total: float = Field(..., ge=0, description="充电电量 kWh")
    start_time: int = Field(..., ge=0, le=23, description="开始小时")
    end_time: int = Field(..., ge=0, le=23, description="结束小时")
    weekday: str = Field(..., description="星期 Mon~Sun")
    platform: str = Field(..., description="android/ios")
    facility_type: int = Field(..., ge=0, description="设备类型")
    station_id: int = Field(0, ge=0, description="站点ID")


class PredictFeeRequest(SessionPredictBase):
    charge_time_hrs: float = Field(..., ge=0, description="充电时长(小时)")


class PredictDurationRequest(SessionPredictBase):
    charging_fees: float = Field(0, ge=0, description="已知费用(可选特征)")


class PredictPlatformRequest(BaseModel):
    kwh_total: float = Field(..., ge=0)
    charging_fees: float = Field(..., ge=0)
    charge_time_hrs: float = Field(..., ge=0)
    start_time: int = Field(..., ge=0, le=23)
    weekday: str = Field(...)
    facility_type: int = Field(..., ge=0)


class PredictSocRequest(BaseModel):
    pack_voltage: float = Field(..., description="组电压 V")
    charge_current: float = Field(..., description="充电电流 A")
    max_cell_voltage: float = Field(...)
    min_cell_voltage: float = Field(...)
    max_temperature: float = Field(...)
    min_temperature: float = Field(...)
    available_energy: float = Field(...)
    available_capacity: float = Field(...)


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
