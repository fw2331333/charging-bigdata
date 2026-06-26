"""数据访问层：查询 MySQL 中的 MapReduce 结果表。"""

import pymysql

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


class BiRepository:
    def _fetch(self, conn: pymysql.connections.Connection, sql: str, limit: int) -> list[dict]:
        with conn.cursor() as cursor:
            cursor.execute(sql, (limit,))
            return list(cursor.fetchall())

    def list_voltage_current(self, conn: pymysql.connections.Connection, limit: int) -> list[VoltageCurrentItem]:
        rows = self._fetch(
            conn,
            """
            SELECT record_hour, avg_pack_voltage, avg_charge_current
            FROM t_voltage_current
            ORDER BY record_hour
            LIMIT %s
            """,
            limit,
        )
        return [VoltageCurrentItem(**row) for row in rows]

    def list_cell_voltage_range(self, conn: pymysql.connections.Connection, limit: int) -> list[CellVoltageRangeItem]:
        rows = self._fetch(
            conn,
            """
            SELECT record_hour, max_cell_voltage, min_cell_voltage
            FROM t_cell_voltage_range
            ORDER BY record_hour
            LIMIT %s
            """,
            limit,
        )
        return [CellVoltageRangeItem(**row) for row in rows]

    def list_temperature(self, conn: pymysql.connections.Connection, limit: int) -> list[TemperatureItem]:
        rows = self._fetch(
            conn,
            """
            SELECT record_time, max_temperature, min_temperature
            FROM t_temperature
            ORDER BY record_time
            LIMIT %s
            """,
            limit,
        )
        return [TemperatureItem(**row) for row in rows]

    def list_energy_capacity(self, conn: pymysql.connections.Connection, limit: int) -> list[EnergyCapacityItem]:
        rows = self._fetch(
            conn,
            """
            SELECT record_hour, avg_available_energy, avg_available_capacity
            FROM t_energy_capacity
            ORDER BY record_hour
            LIMIT %s
            """,
            limit,
        )
        return [EnergyCapacityItem(**row) for row in rows]

    def list_charge_current_stats(self, conn: pymysql.connections.Connection, limit: int) -> list[ChargeCurrentStatsItem]:
        rows = self._fetch(
            conn,
            """
            SELECT record_hour, avg_charge_current, max_charge_current
            FROM t_charge_current_stats
            ORDER BY record_hour
            LIMIT %s
            """,
            limit,
        )
        return [ChargeCurrentStatsItem(**row) for row in rows]

    def list_voltage_current_relation(
        self, conn: pymysql.connections.Connection, limit: int
    ) -> list[VoltageCurrentRelationItem]:
        rows = self._fetch(
            conn,
            """
            SELECT record_time, pack_voltage, charge_current
            FROM t_voltage_current_relation
            ORDER BY record_time
            LIMIT %s
            """,
            limit,
        )
        return [VoltageCurrentRelationItem(**row) for row in rows]

    def list_soc_temperature(self, conn: pymysql.connections.Connection, limit: int) -> list[SocTemperatureItem]:
        rows = self._fetch(
            conn,
            """
            SELECT soc_bucket, avg_max_temperature, avg_min_temperature
            FROM t_soc_temperature
            ORDER BY soc_bucket
            LIMIT %s
            """,
            limit,
        )
        return [SocTemperatureItem(**row) for row in rows]

    def list_soc_hourly(self, conn: pymysql.connections.Connection, limit: int) -> list[SocHourlyItem]:
        rows = self._fetch(
            conn,
            "SELECT time_key, avg_soc FROM t_soc_hourly ORDER BY time_key LIMIT %s",
            limit,
        )
        return [SocHourlyItem(**row) for row in rows]

    def list_charging_daily(self, conn: pymysql.connections.Connection, limit: int) -> list[ChargingDailyItem]:
        rows = self._fetch(
            conn,
            "SELECT record_date, charge_count FROM t_charging_daily ORDER BY record_date LIMIT %s",
            limit,
        )
        return [ChargingDailyItem(**row) for row in rows]

    def list_charging_monthly(self, conn: pymysql.connections.Connection, limit: int) -> list[ChargingMonthlyItem]:
        rows = self._fetch(
            conn,
            "SELECT record_month, charge_count FROM t_charging_monthly ORDER BY record_month LIMIT %s",
            limit,
        )
        return [ChargingMonthlyItem(**row) for row in rows]

    def list_charge_rate_hourly(self, conn: pymysql.connections.Connection, limit: int) -> list[ChargeRateHourlyItem]:
        rows = self._fetch(
            conn,
            "SELECT hour_key, avg_rate FROM t_charge_rate_hourly ORDER BY CAST(hour_key AS UNSIGNED) LIMIT %s",
            limit,
        )
        return [ChargeRateHourlyItem(**row) for row in rows]

    def list_soc_heatmap(self, conn: pymysql.connections.Connection, limit: int) -> list[SocHeatmapItem]:
        rows = self._fetch(
            conn,
            """
            SELECT record_day, hour_key, avg_soc
            FROM t_soc_heatmap
            ORDER BY record_day, hour_key
            LIMIT %s
            """,
            limit,
        )
        return [SocHeatmapItem(**row) for row in rows]
