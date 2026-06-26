"""BI 业务：编排 Repository 查询 MapReduce + ADS 汇总表。"""

import pymysql

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


class BiService:
    def __init__(self) -> None:
        self.repo = BiRepository()

    def list_voltage_current(self, conn: pymysql.connections.Connection, limit: int) -> list[VoltageCurrentItem]:
        return self.repo.list_voltage_current(conn, limit)

    def list_cell_voltage_range(self, conn: pymysql.connections.Connection, limit: int) -> list[CellVoltageRangeItem]:
        return self.repo.list_cell_voltage_range(conn, limit)

    def list_temperature(self, conn: pymysql.connections.Connection, limit: int) -> list[TemperatureItem]:
        return self.repo.list_temperature(conn, limit)

    def list_energy_capacity(self, conn: pymysql.connections.Connection, limit: int) -> list[EnergyCapacityItem]:
        return self.repo.list_energy_capacity(conn, limit)

    def list_charge_current_stats(self, conn: pymysql.connections.Connection, limit: int) -> list[ChargeCurrentStatsItem]:
        return self.repo.list_charge_current_stats(conn, limit)

    def list_voltage_current_relation(
        self, conn: pymysql.connections.Connection, limit: int
    ) -> list[VoltageCurrentRelationItem]:
        return self.repo.list_voltage_current_relation(conn, limit)

    def list_soc_temperature(self, conn: pymysql.connections.Connection, limit: int) -> list[SocTemperatureItem]:
        return self.repo.list_soc_temperature(conn, limit)

    def list_soc_hourly(self, conn: pymysql.connections.Connection, limit: int) -> list[SocHourlyItem]:
        return self.repo.list_soc_hourly(conn, limit)

    def list_charging_daily(self, conn: pymysql.connections.Connection, limit: int) -> list[ChargingDailyItem]:
        return self.repo.list_charging_daily(conn, limit)

    def list_charging_monthly(self, conn: pymysql.connections.Connection, limit: int) -> list[ChargingMonthlyItem]:
        return self.repo.list_charging_monthly(conn, limit)

    def list_charge_rate_hourly(self, conn: pymysql.connections.Connection, limit: int) -> list[ChargeRateHourlyItem]:
        return self.repo.list_charge_rate_hourly(conn, limit)

    def list_soc_heatmap(self, conn: pymysql.connections.Connection, limit: int) -> list[SocHeatmapItem]:
        return self.repo.list_soc_heatmap(conn, limit)
