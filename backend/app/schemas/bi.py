"""BI 查询响应模型（MapReduce + ADS 汇总）。"""

from pydantic import BaseModel


class VoltageCurrentItem(BaseModel):
    record_hour: str
    avg_pack_voltage: float
    avg_charge_current: float


class CellVoltageRangeItem(BaseModel):
    record_hour: str
    max_cell_voltage: float
    min_cell_voltage: float


class TemperatureItem(BaseModel):
    record_time: str
    max_temperature: float
    min_temperature: float


class EnergyCapacityItem(BaseModel):
    record_hour: str
    avg_available_energy: float
    avg_available_capacity: float


class ChargeCurrentStatsItem(BaseModel):
    record_hour: str
    avg_charge_current: float
    max_charge_current: float


class VoltageCurrentRelationItem(BaseModel):
    record_hour: str
    voltage_change_rate: float
    current_change_rate: float


class SocTemperatureItem(BaseModel):
    battery_status: str
    avg_max_temperature: float
    avg_min_temperature: float
    var_max_temperature: float
    var_min_temperature: float


class SocHourlyItem(BaseModel):
    time_key: str
    avg_soc: float


class ChargingDailyItem(BaseModel):
    record_date: str
    charge_count: int


class ChargingMonthlyItem(BaseModel):
    record_month: str
    charge_count: int


class ChargeRateHourlyItem(BaseModel):
    hour_key: str
    avg_rate: float


class SocHeatmapItem(BaseModel):
    record_day: str
    hour_key: str
    avg_soc: float
