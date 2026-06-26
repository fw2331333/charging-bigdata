#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 MapReduce 的 part-r-00000 导入 MySQL（支持 HDFS 拉取或本地目录）。"""
import argparse
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("load_mr_to_mysql")

TASKS = [
    ("v1", "t_voltage_current", ["record_hour", "avg_pack_voltage", "avg_charge_current"]),
    ("v2", "t_cell_voltage_range", ["record_hour", "max_cell_voltage", "min_cell_voltage"]),
    ("v3", "t_temperature", ["record_time", "max_temperature", "min_temperature"]),
    ("v4", "t_energy_capacity", ["record_hour", "avg_available_energy", "avg_available_capacity"]),
    ("v5", "t_charge_current_stats", ["record_hour", "avg_charge_current", "max_charge_current"]),
    ("v6", "t_voltage_current_relation", ["record_time", "pack_voltage", "charge_current"]),
    ("v7", "t_soc_temperature", ["soc_bucket", "avg_max_temperature", "avg_min_temperature"]),
]


def hdfs_get(hdfs_path: str, local_file: Path) -> None:
    local_file.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(["hdfs", "dfs", "-get", "-f", hdfs_path, str(local_file)])


def parse_line(line: str) -> Optional[Tuple[str, List[float]]]:
    line = line.strip()
    if not line:
        return None
    parts = line.split("\t")
    if len(parts) < 3:
        return None
    key = parts[0]
    try:
        metrics = [float(x) for x in parts[1:]]
    except ValueError:
        return None
    return key, metrics


def sql_quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def load_pipeline_env(env_file: Path) -> dict:
    cfg = {}
    if not env_file.is_file():
        return cfg
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip().replace("\r", "")
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        cfg[key.strip()] = value.strip().strip('"').strip("'")
    return cfg


def resolve_mysql_config(env_file: Path, hdfs_base_cli: str) -> dict:
    cfg = load_pipeline_env(env_file)
    if not cfg.get("MYSQL_PASSWORD"):
        log.error("MySQL 密码为空，请检查 %s 中 MYSQL_PASSWORD", env_file)
        sys.exit(1)
    return {
        "host": cfg.get("MYSQL_HOST", "10.0.2.2"),
        "port": int(cfg.get("MYSQL_PORT", "3306")),
        "user": cfg.get("MYSQL_USER", "root"),
        "password": cfg.get("MYSQL_PASSWORD", ""),
        "database": cfg.get("MYSQL_DATABASE", "charging_bigdata"),
        "hdfs_base": hdfs_base_cli or cfg.get("HDFS_OUTPUT_BASE", "/Car/output"),
    }


def mysql_base_cmd(cfg: dict) -> List[str]:
    return [
        "mysql",
        "-h", cfg["host"],
        "-P", str(cfg["port"]),
        "-u", cfg["user"],
        "-p{}".format(cfg["password"]),
        cfg["database"],
    ]


def test_mysql(cfg: dict) -> None:
    subprocess.check_call(
        mysql_base_cmd(cfg) + ["-e", "SELECT 1;"],
        stdout=subprocess.DEVNULL,
    )


def load_file_cli(cfg: dict, table: str, columns: List[str], file_path: Path) -> int:
    updates = ", ".join("{0}=VALUES({0})".format(col) for col in columns[1:])
    col_list = ", ".join(columns)
    rows = 0
    fd, sql_path = tempfile.mkstemp(prefix="cbp_etl_", suffix=".sql")
    os.close(fd)

    try:
        with open(sql_path, "w", encoding="utf-8") as out, file_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                parsed = parse_line(line)
                if parsed is None:
                    continue
                key, metrics = parsed
                if len(metrics) < len(columns) - 1:
                    continue
                vals = [sql_quote(key)]
                vals.extend(str(m) for m in metrics[: len(columns) - 1])
                out.write(
                    "INSERT INTO {table} ({cols}) VALUES ({vals}) "
                    "ON DUPLICATE KEY UPDATE {upd};\n".format(
                        table=table,
                        cols=col_list,
                        vals=", ".join(vals),
                        upd=updates,
                    )
                )
                rows += 1

        if rows == 0:
            return 0

        with open(sql_path, "r", encoding="utf-8") as sql_in:
            subprocess.check_call(mysql_base_cmd(cfg), stdin=sql_in)
        return rows
    finally:
        try:
            os.unlink(sql_path)
        except OSError:
            pass


def main() -> None:
    script_root = Path(__file__).resolve().parents[2]
    default_env = script_root / "config" / "pipeline.env"

    parser = argparse.ArgumentParser(description="Load MapReduce outputs into MySQL")
    parser.add_argument("--env-file", default=str(default_env), help="pipeline.env 路径")
    parser.add_argument("--hdfs-base", default="", help="HDFS MR 输出根目录，默认读 env 文件")
    parser.add_argument("--local-dir", default="", help="local directory with v1..v7 folders")
    args = parser.parse_args()

    env_path = Path(args.env_file)
    if not env_path.is_file():
        log.error("配置文件不存在: %s", env_path)
        sys.exit(1)

    mysql_cfg = resolve_mysql_config(env_path, args.hdfs_base)
    log.info(
        "ETL start -> %s:%s/%s (mysql CLI, env=%s)",
        mysql_cfg["host"],
        mysql_cfg["port"],
        mysql_cfg["database"],
        env_path,
    )
    test_mysql(mysql_cfg)
    log.info("MySQL connection OK")

    tmp_dir = None
    hdfs_base = mysql_cfg["hdfs_base"]
    try:
        if args.local_dir:
            base = Path(args.local_dir)
        else:
            tmp_dir = tempfile.mkdtemp(prefix="cbp_mr_")
            base = Path(tmp_dir)

        total = 0
        for code, table, columns in TASKS:
            part = base / code / "part-r-00000"
            if not part.exists():
                if args.local_dir:
                    log.warning("[SKIP] %s: missing %s", code, part)
                    continue
                log.info("hdfs get %s", "{}/{}/part-r-00000".format(hdfs_base.rstrip("/"), code))
                hdfs_get("{}/{}/part-r-00000".format(hdfs_base.rstrip("/"), code), part)

            count = load_file_cli(mysql_cfg, table, columns, part)
            log.info("[OK] %s -> %s: %d rows", code, table, count)
            total += count

        log.info("Done. Total rows loaded/updated: %d", total)
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
