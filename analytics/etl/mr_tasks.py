# -*- coding: utf-8 -*-
"""
MapReduce v1~v7 与 MySQL 服务层表的映射定义。

每条任务对应：
  HDFS  {hdfs_base}/{code}/part-r-00000
  MySQL {table}（列顺序与 MR 输出 Tab 分隔字段一致）
"""

from __future__ import annotations

from typing import NamedTuple


class MrEtlTask(NamedTuple):
    """单条 MR → MySQL 装载任务元数据。"""

    code: str
    table: str
    columns: list[str]


# (code, mysql_table, insert_columns)
MR_ETL_TASKS: tuple[MrEtlTask, ...] = (
    MrEtlTask("v1", "t_voltage_current", ["record_hour", "avg_pack_voltage", "avg_charge_current"]),
    MrEtlTask("v2", "t_cell_voltage_range", ["record_hour", "max_cell_voltage", "min_cell_voltage"]),
    MrEtlTask("v3", "t_temperature", ["record_time", "max_temperature", "min_temperature"]),
    MrEtlTask("v4", "t_energy_capacity", ["record_hour", "avg_available_energy", "avg_available_capacity"]),
    MrEtlTask("v5", "t_charge_current_stats", ["record_hour", "avg_charge_current", "max_charge_current"]),
    MrEtlTask("v6", "t_voltage_current_relation", ["record_hour", "voltage_change_rate", "current_change_rate"]),
    MrEtlTask("v7", "t_soc_temperature", ["battery_status", "avg_max_temperature", "avg_min_temperature", "var_max_temperature", "var_min_temperature"]),
)
