# MySQL 预置数据（Web 演示）

`charging_bigdata_data.sql` 为 **已跑完 MapReduce + Spark ADS 后的汇总数据**，他人无需 Hadoop 即可导入并驱动前端图表。

## 导入顺序

1. `sql/schema.sql` — MR 结果表 + 视图  
2. `sql/ads_schema.sql` — ADS 分析表  
3. `sql/seed/charging_bigdata_data.sql` — **本文件（INSERT 数据）**

## 一键导入

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File scripts/import_web_demo.ps1 -Password your_password
```

```bash
# Linux / macOS
MYSQL_PASSWORD=your_password bash scripts/import_web_demo.sh
```

## 数据说明

| 表 | 行数级 | 来源 |
|----|--------|------|
| t_voltage_current 等 MR 表 | ~3200 | dsv13r1 MapReduce |
| t_soc_hourly、t_charging_* 等 ADS 表 | ~300 | dsv13r2 + nvv2t Spark ADS |

维护者更新数据：在本机 MySQL 跑完流水线后执行 `scripts/export_mysql_seed.ps1`。
