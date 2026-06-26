"""BI 数据接口：查询 MapReduce 写入 MySQL 的统计结果。"""

import pymysql
from fastapi import APIRouter, Depends, Query

from app.api.deps import get_db
from app.schemas.bi import (
    CellVoltageRangeItem,
    ChargeCurrentStatsItem,
    ChargeRateHourlyItem,
    ChargingDailyItem,
    ChargingMonthlyItem,
    EnergyCapacityItem,
    SocHeatmapItem,
    SocHourlyItem,
    SocTemperatureItem,
    TemperatureItem,
    VoltageCurrentItem,
    VoltageCurrentRelationItem,
)
from app.services.bi_service import BiService

router = APIRouter(prefix="/bi", tags=["BI 统计"])
service = BiService()


@router.get("/voltage-current", response_model=list[VoltageCurrentItem], summary="v1 每小时电压电流")
def list_voltage_current(
    limit: int = Query(500, ge=1, le=5000),
    db: pymysql.connections.Connection = Depends(get_db),
) -> list[VoltageCurrentItem]:
    return service.list_voltage_current(db, limit)


@router.get("/cell-voltage-range", response_model=list[CellVoltageRangeItem], summary="v2 单体电压范围")
def list_cell_voltage_range(
    limit: int = Query(500, ge=1, le=5000),
    db: pymysql.connections.Connection = Depends(get_db),
) -> list[CellVoltageRangeItem]:
    return service.list_cell_voltage_range(db, limit)


@router.get("/temperature", response_model=list[TemperatureItem], summary="v3 温度趋势")
def list_temperature(
    limit: int = Query(2000, ge=1, le=10000),
    db: pymysql.connections.Connection = Depends(get_db),
) -> list[TemperatureItem]:
    return service.list_temperature(db, limit)


@router.get("/energy-capacity", response_model=list[EnergyCapacityItem], summary="v4 能量容量")
def list_energy_capacity(
    limit: int = Query(500, ge=1, le=5000),
    db: pymysql.connections.Connection = Depends(get_db),
) -> list[EnergyCapacityItem]:
    return service.list_energy_capacity(db, limit)


@router.get("/charge-current-stats", response_model=list[ChargeCurrentStatsItem], summary="v5 充电电流统计")
def list_charge_current_stats(
    limit: int = Query(500, ge=1, le=5000),
    db: pymysql.connections.Connection = Depends(get_db),
) -> list[ChargeCurrentStatsItem]:
    return service.list_charge_current_stats(db, limit)


@router.get(
    "/voltage-current-relation",
    response_model=list[VoltageCurrentRelationItem],
    summary="v6 电压电流关系",
)
def list_voltage_current_relation(
    limit: int = Query(2000, ge=1, le=10000),
    db: pymysql.connections.Connection = Depends(get_db),
) -> list[VoltageCurrentRelationItem]:
    return service.list_voltage_current_relation(db, limit)


@router.get("/soc-temperature", response_model=list[SocTemperatureItem], summary="v7 SOC 分段温度")
def list_soc_temperature(
    limit: int = Query(50, ge=1, le=500),
    db: pymysql.connections.Connection = Depends(get_db),
) -> list[SocTemperatureItem]:
    return service.list_soc_temperature(db, limit)


@router.get("/soc-hourly", response_model=list[SocHourlyItem], summary="ADS 每小时平均 SOC")
def list_soc_hourly(
    limit: int = Query(500, ge=1, le=5000),
    db: pymysql.connections.Connection = Depends(get_db),
) -> list[SocHourlyItem]:
    return service.list_soc_hourly(db, limit)


@router.get("/charging-daily", response_model=list[ChargingDailyItem], summary="ADS 每日充电次数")
def list_charging_daily(
    limit: int = Query(500, ge=1, le=5000),
    db: pymysql.connections.Connection = Depends(get_db),
) -> list[ChargingDailyItem]:
    return service.list_charging_daily(db, limit)


@router.get("/charging-monthly", response_model=list[ChargingMonthlyItem], summary="ADS 每月充电次数")
def list_charging_monthly(
    limit: int = Query(120, ge=1, le=500),
    db: pymysql.connections.Connection = Depends(get_db),
) -> list[ChargingMonthlyItem]:
    return service.list_charging_monthly(db, limit)


@router.get("/charge-rate-hourly", response_model=list[ChargeRateHourlyItem], summary="ADS 每小时充电速率")
def list_charge_rate_hourly(
    limit: int = Query(48, ge=1, le=200),
    db: pymysql.connections.Connection = Depends(get_db),
) -> list[ChargeRateHourlyItem]:
    return service.list_charge_rate_hourly(db, limit)


@router.get("/soc-heatmap", response_model=list[SocHeatmapItem], summary="ADS SOC 热力图")
def list_soc_heatmap(
    limit: int = Query(5000, ge=1, le=20000),
    db: pymysql.connections.Connection = Depends(get_db),
) -> list[SocHeatmapItem]:
    return service.list_soc_heatmap(db, limit)
