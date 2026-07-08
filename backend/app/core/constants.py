"""服务层常量：表名与数据域划分（MR 离线统计 vs Spark ADS）。"""

# ---------------------------------------------------------------------------
# MapReduce 服务表（analytics/etl → load_mr_to_mysql.py）
# 与 mapreduce v1~v7 一一对应
# ---------------------------------------------------------------------------
MR_TABLES: tuple[str, ...] = (
    "t_voltage_current",
    "t_cell_voltage_range",
    "t_temperature",
    "t_energy_capacity",
    "t_charge_current_stats",
    "t_voltage_current_relation",
    "t_soc_temperature",
)

# ---------------------------------------------------------------------------
# Spark ADS 服务表（spark/scripts/load_ads_spark.py）
# ---------------------------------------------------------------------------
ADS_TABLES: tuple[str, ...] = (
    "t_soc_hourly",
    "t_charging_daily",
    "t_charging_monthly",
    "t_charge_rate_hourly",
    "t_soc_heatmap",
)

# API 默认分页上限（与各 endpoint Query 保持一致）
DEFAULT_BI_LIMIT = 500
MAX_BI_LIMIT = 10000
