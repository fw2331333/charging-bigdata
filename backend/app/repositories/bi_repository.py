"""
数据访问层（Repository）：只读 MySQL 服务层，不访问 HDFS。

表域划分：
  - MR 表（7 张）：MapReduce v1~v7 经 ETL 写入，见 app.core.constants.MR_TABLES
  - ADS 表（5 张）：Spark 汇总写入，见 app.core.constants.ADS_TABLES

本层仅负责 SQL 与行 → Pydantic 模型映射；业务编排在上层 BiService。
"""

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
    """MySQL 只读仓储；所有查询均带 LIMIT 防止全表扫描拖垮 API。"""

    def _fetch(self, conn: pymysql.connections.Connection, sql: str, limit: int) -> list[dict]:
        with conn.cursor() as cursor:
            cursor.execute(sql, (limit,))
            return list(cursor.fetchall())

    # --- MapReduce 服务表（v1~v7）---

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
            SELECT record_hour, voltage_change_rate, current_change_rate
            FROM t_voltage_current_relation
            ORDER BY CAST(record_hour AS UNSIGNED)
            LIMIT %s
            """,
            limit,
        )
        return [VoltageCurrentRelationItem(**row) for row in rows]

    def list_soc_temperature(self, conn: pymysql.connections.Connection, limit: int) -> list[SocTemperatureItem]:
        rows = self._fetch(
            conn,
            """
            SELECT battery_status, avg_max_temperature, avg_min_temperature, var_max_temperature, var_min_temperature
            FROM t_soc_temperature
            ORDER BY FIELD(battery_status, 'idle', 'charging', 'discharging')
            LIMIT %s
            """,
            limit,
        )
        return [SocTemperatureItem(**row) for row in rows]

    # --- Spark ADS 服务表 ---

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
