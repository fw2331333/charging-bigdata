"""
BI 业务服务层（Service）。

职责：接收 API 层传入的数据库连接，委托 BiRepository 查询，返回 Pydantic 模型列表。
热点查询带 60s TTL 进程内缓存。
"""

import pymysql

from app.core.cache import cached_call
from app.repositories.bi_repository import BiRepository
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

_BI_TTL = 60.0


class BiService:
    def __init__(self) -> None:
        self.repo = BiRepository()

    def invalidate_cache(self, prefix: str | None = None) -> int:
        from app.core.cache import cache_invalidate

        return cache_invalidate(f"bi:{prefix}" if prefix else "bi:")

    def list_voltage_current(self, conn: pymysql.connections.Connection, limit: int) -> list[VoltageCurrentItem]:
        return cached_call(
            f"bi:voltage_current:{limit}",
            _BI_TTL,
            lambda: self.repo.list_voltage_current(conn, limit),
        )

    def list_cell_voltage_range(self, conn: pymysql.connections.Connection, limit: int) -> list[CellVoltageRangeItem]:
        return cached_call(
            f"bi:cell_voltage_range:{limit}",
            _BI_TTL,
            lambda: self.repo.list_cell_voltage_range(conn, limit),
        )

    def list_temperature(self, conn: pymysql.connections.Connection, limit: int) -> list[TemperatureItem]:
        return cached_call(
            f"bi:temperature:{limit}",
            _BI_TTL,
            lambda: self.repo.list_temperature(conn, limit),
        )

    def list_energy_capacity(self, conn: pymysql.connections.Connection, limit: int) -> list[EnergyCapacityItem]:
        return cached_call(
            f"bi:energy_capacity:{limit}",
            _BI_TTL,
            lambda: self.repo.list_energy_capacity(conn, limit),
        )

    def list_charge_current_stats(self, conn: pymysql.connections.Connection, limit: int) -> list[ChargeCurrentStatsItem]:
        return cached_call(
            f"bi:charge_current_stats:{limit}",
            _BI_TTL,
            lambda: self.repo.list_charge_current_stats(conn, limit),
        )

    def list_voltage_current_relation(
        self, conn: pymysql.connections.Connection, limit: int
    ) -> list[VoltageCurrentRelationItem]:
        return cached_call(
            f"bi:voltage_current_relation:{limit}",
            _BI_TTL,
            lambda: self.repo.list_voltage_current_relation(conn, limit),
        )

    def list_soc_temperature(self, conn: pymysql.connections.Connection, limit: int) -> list[SocTemperatureItem]:
        return cached_call(
            f"bi:soc_temperature:{limit}",
            _BI_TTL,
            lambda: self.repo.list_soc_temperature(conn, limit),
        )

    def list_soc_hourly(self, conn: pymysql.connections.Connection, limit: int) -> list[SocHourlyItem]:
        return cached_call(
            f"bi:soc_hourly:{limit}",
            _BI_TTL,
            lambda: self.repo.list_soc_hourly(conn, limit),
        )

    def list_charging_daily(self, conn: pymysql.connections.Connection, limit: int) -> list[ChargingDailyItem]:
        return cached_call(
            f"bi:charging_daily:{limit}",
            _BI_TTL,
            lambda: self.repo.list_charging_daily(conn, limit),
        )

    def list_charging_monthly(self, conn: pymysql.connections.Connection, limit: int) -> list[ChargingMonthlyItem]:
        return cached_call(
            f"bi:charging_monthly:{limit}",
            _BI_TTL,
            lambda: self.repo.list_charging_monthly(conn, limit),
        )

    def list_charge_rate_hourly(self, conn: pymysql.connections.Connection, limit: int) -> list[ChargeRateHourlyItem]:
        return cached_call(
            f"bi:charge_rate_hourly:{limit}",
            _BI_TTL,
            lambda: self.repo.list_charge_rate_hourly(conn, limit),
        )

    def list_soc_heatmap(self, conn: pymysql.connections.Connection, limit: int) -> list[SocHeatmapItem]:
        return cached_call(
            f"bi:soc_heatmap:{limit}",
            _BI_TTL,
            lambda: self.repo.list_soc_heatmap(conn, limit),
        )
