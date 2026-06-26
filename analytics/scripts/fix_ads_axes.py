#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修正 ADS 表：SOC 来自 dsv13r2；充电次数来自 nvv2t.created（与 Spark 一致）。"""
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DSV = Path(r"F:\项目2资料\数据集\dsv13r2.csv")
NVV = Path(r"F:\项目2资料\数据集\nvv2t.csv")
ENV = ROOT / "config" / "pipeline.env"


def load_env() -> dict:
    cfg = {}
    for line in ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip().replace("\r", "")
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip()
    return cfg


def fix_nvv_created(s: str) -> str:
    """nvv2t 0014-xx → 2014-xx，与 nvv2t_md 对齐。"""
    s = s.strip()
    if s.startswith("00") and len(s) >= 10:
        return "20" + s[2:]
    return s


def mysql_exec(cfg: dict, sql: str) -> None:
    cmd = [
        "mysql",
        "-h", "127.0.0.1",
        "-P", cfg.get("MYSQL_PORT", "3306"),
        "-u", cfg.get("MYSQL_USER", "root"),
        "-p{}".format(cfg.get("MYSQL_PASSWORD", "")),
        cfg.get("MYSQL_DATABASE", "charging_bigdata"),
        "-e", sql,
    ]
    subprocess.check_call(cmd)


def rebuild_soc_hourly() -> list[str]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for i, line in enumerate(DSV.read_text(encoding="utf-8-sig").splitlines()):
        if i == 0 and "record_time" in line:
            continue
        parts = line.split(",")
        if len(parts) < 3 or len(parts[1]) < 10:
            continue
        key = parts[1][:10]
        try:
            buckets[key].append(float(parts[2]))
        except ValueError:
            continue
    stmts = ["DELETE FROM t_soc_hourly;"]
    for k in sorted(buckets.keys()):
        avg = sum(buckets[k]) / len(buckets[k])
        stmts.append("INSERT INTO t_soc_hourly (time_key, avg_soc) VALUES ('{}', {});".format(k, avg))
    return stmts


def rebuild_charging() -> list[str]:
    daily: dict[str, int] = defaultdict(int)
    monthly: dict[str, int] = defaultdict(int)
    for i, line in enumerate(NVV.read_text(encoding="utf-8-sig").splitlines()):
        if i == 0:
            continue
        parts = line.split(",")
        if len(parts) < 4:
            continue
        created = fix_nvv_created(parts[3].strip())
        if len(created) < 10:
            continue
        day = created[:10].replace("-", "")
        month = created[:7].replace("-", "")
        daily[day] += 1
        monthly[month] += 1
    stmts = ["DELETE FROM t_charging_daily;", "DELETE FROM t_charging_monthly;"]
    for d in sorted(daily.keys()):
        stmts.append(
            "INSERT INTO t_charging_daily (record_date, charge_count) VALUES ('{}', {});".format(d, daily[d])
        )
    for m in sorted(monthly.keys()):
        stmts.append(
            "INSERT INTO t_charging_monthly (record_month, charge_count) VALUES ('{}', {});".format(m, monthly[m])
        )
    return stmts


def main() -> None:
    cfg = load_env()
    sql = "\n".join(rebuild_soc_hourly() + rebuild_charging())
    mysql_exec(cfg, sql)
    print("ADS fixed: SOC=dsv13r2, charging=nvv2t (created, 2014-2015)")


if __name__ == "__main__":
    main()
