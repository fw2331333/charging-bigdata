#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spark SQL：HDFS 明细 → MySQL ADS（对照指导书 §3.2 / §3.3 / §9）。

数据分工：
  - dsv13r2.csv：SOC 时序、热力图、充电速率（§3.2 电池分析）
  - nvv2t.csv：日/月充电会话次数，字段 created（§3.3 充电行为）
  - nvv2t_md.csv：仅 Windows ML 训练（§3.4，本脚本不读）
  - dsv13r1.csv：仅 MapReduce
"""
import argparse
import sys
from pathlib import Path

from pyspark.sql import SparkSession, Window, functions as F


def hdfs_uri(path: str) -> str:
    if path.startswith("hdfs://"):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return "hdfs://" + path


def load_env(env_file: Path) -> dict:
    cfg = {}
    if not env_file.is_file():
        return cfg
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip().replace("\r", "")
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def jdbc_props(cfg: dict) -> tuple:
    host = cfg.get("MYSQL_HOST", "10.0.2.2")
    port = cfg.get("MYSQL_PORT", "3306")
    db = cfg.get("MYSQL_DATABASE", "charging_bigdata")
    user = cfg.get("MYSQL_USER", "root")
    password = cfg.get("MYSQL_PASSWORD", "")
    url = "jdbc:mysql://{host}:{port}/{db}?useUnicode=true&characterEncoding=utf8&rewriteBatchedStatements=true".format(
        host=host, port=port, db=db
    )
    props = {"user": user, "password": password, "driver": "com.mysql.cj.jdbc.Driver"}
    return url, props


def write_table(df, table: str, url: str, props: dict) -> int:
    cnt = df.count()
    if cnt == 0:
        print("[WARN] skip empty table {}".format(table))
        return 0
    (
        df.write.mode("overwrite")
        .option("truncate", "true")
        .jdbc(url, table, properties=props)
    )
    print("[OK] {} -> {} rows".format(table, cnt))
    return cnt


def main() -> None:
    script_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Spark SQL ADS -> MySQL")
    parser.add_argument("--env-file", default=str(script_root / "config" / "pipeline.env"))
    parser.add_argument("--dsv13r2", default="/Car/dsv13r2.csv")
    parser.add_argument("--nvv2t", default="/Car/nvv2t.csv")
    parser.add_argument("--local", action="store_true", help="读本机 CSV（开发调试）")
    parser.add_argument("--local-dsv", default=r"F:\项目2资料\数据集\dsv13r2.csv")
    parser.add_argument("--local-nvv", default=r"F:\项目2资料\数据集\nvv2t.csv")
    args = parser.parse_args()

    cfg = load_env(Path(args.env_file))
    if not cfg.get("MYSQL_PASSWORD") and not args.local:
        print("ERROR: MYSQL_PASSWORD 为空", file=sys.stderr)
        sys.exit(1)
    if args.local:
        cfg["MYSQL_HOST"] = "127.0.0.1"

    dsv_path = args.local_dsv if args.local else hdfs_uri(args.dsv13r2)
    nvv_path = args.local_nvv if args.local else hdfs_uri(args.nvv2t)

    spark = (
        SparkSession.builder.appName("charging-bigdata-ads")
        .config("spark.sql.session.timeZone", "Asia/Shanghai")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    url, props = jdbc_props(cfg)
    total = 0

    # --- dsv13r2: SOC / 充电速率 / 热力图 ---
    dsv = spark.read.option("header", True).option("inferSchema", False).csv(dsv_path)
    dsv = dsv.withColumn("soc", F.col("soc").cast("double"))

    soc_hourly = (
        dsv.filter(F.length("record_time") >= 10)
        .withColumn("time_key", F.substring("record_time", 1, 10))
        .groupBy("time_key")
        .agg(F.avg("soc").alias("avg_soc"))
    )
    total += write_table(soc_hourly, "t_soc_hourly", url, props)

    heatmap = (
        dsv.filter(F.length("record_time") >= 10)
        .withColumn("record_day", F.substring("record_time", 1, 8))
        .withColumn("hour_key", F.substring("record_time", 9, 2))
        .groupBy("record_day", "hour_key")
        .agg(F.avg("soc").alias("avg_soc"))
    )
    total += write_table(heatmap, "t_soc_heatmap", url, props)

    # 充电速率：相邻记录 SOC 差 / 时间差（分钟），与 Python 版逻辑一致
    ts_df = (
        dsv.filter(F.col("record_time").rlike(r"^\d{14}$"))
        .withColumn("ts", F.col("record_time").cast("double"))
        .withColumn("hour_key", F.substring("record_time", 9, 2))
    )
    w = Window.orderBy("ts")
    rate_src = (
        ts_df.withColumn("prev_ts", F.lag("ts").over(w))
        .withColumn("prev_soc", F.lag("soc").over(w))
        .withColumn("dt", F.col("ts") - F.col("prev_ts"))
        .filter((F.col("dt") > 0) & (F.col("dt") <= 3600))
        .withColumn("rate", (F.col("soc") - F.col("prev_soc")) / (F.col("dt") / 60.0))
        .filter(F.abs(F.col("rate")) <= 50)
    )
    rate = rate_src.groupBy("hour_key").agg(F.avg("rate").alias("avg_rate"))
    total += write_table(rate, "t_charge_rate_hourly", url, props)

    # --- nvv2t: 日/月充电会话次数（§3.3 created；0014→2014 与 nvv2t_md 一致）---
    nvv = spark.read.option("header", True).option("inferSchema", False).csv(nvv_path)
    nvv = nvv.withColumn("created_fixed", F.regexp_replace("created", r"^00", "20"))
    daily = (
        nvv.filter(F.length("created_fixed") >= 10)
        .withColumn("record_date", F.regexp_replace(F.substring("created_fixed", 1, 10), "-", ""))
        .groupBy("record_date")
        .agg(F.count("*").alias("charge_count"))
    )
    total += write_table(daily, "t_charging_daily", url, props)

    monthly = (
        nvv.filter(F.length("created_fixed") >= 7)
        .withColumn("record_month", F.regexp_replace(F.substring("created_fixed", 1, 7), "-", ""))
        .groupBy("record_month")
        .agg(F.count("*").alias("charge_count"))
    )
    total += write_table(monthly, "t_charging_monthly", url, props)

    print("Done. Total ADS rows written: {}".format(total))
    spark.stop()


if __name__ == "__main__":
    main()
