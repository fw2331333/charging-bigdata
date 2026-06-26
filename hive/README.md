# 已弃用：请使用 Spark SQL

本目录为早期 Hive ODS 方案，**不再推荐**（Hive 3.x 维护模式，业界已普遍用 Spark SQL / Iceberg / Delta）。

## 当前主流路径

请使用 **[spark/README.md](../spark/README.md)**：

```text
HDFS /Car/*.csv
  → Spark SQL 聚合
  → JDBC 写入 MySQL ADS 表
  → FastAPI + ECharts 只读 MySQL
```

流水线已默认调用 `spark/scripts/run-spark-ads.sh`，无需安装 Hive。

## 本目录文件

| 文件 | 说明 |
|------|------|
| `ddl/` | 历史 Hive 外部表 DDL，仅供参考 |
| `scripts/install-hive.sh` | **勿再执行** |

答辩时可演示：

```bash
spark-submit --version
bash spark/scripts/run-spark-ads.sh
spark-sql -e "SELECT 1"
```
