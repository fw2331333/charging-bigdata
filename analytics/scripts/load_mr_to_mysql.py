#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI：MapReduce HDFS 输出 → MySQL 服务层（企业级 ETL 入口）。

流水线调用：
  python3 analytics/scripts/load_mr_to_mysql.py --env-file config/pipeline.env

本地调试（无需 HDFS）：
  python3 analytics/scripts/load_mr_to_mysql.py --local-dir /path/to/mr/output
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# 将项目根目录加入 path，支持从任意 cwd 调用
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from analytics.etl import MrToMysqlLoader, load_pipeline_config  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("load_mr_to_mysql")


def main() -> None:
    default_env = _ROOT / "config" / "pipeline.env"
    parser = argparse.ArgumentParser(description="Load MapReduce outputs into MySQL (ETL layer)")
    parser.add_argument("--env-file", default=str(default_env), help="pipeline.env 路径")
    parser.add_argument("--hdfs-base", default="", help="覆盖 HDFS MR 输出根目录")
    parser.add_argument("--local-dir", default="", help="本地 v1..v7 目录（跳过 HDFS）")
    args = parser.parse_args()

    env_path = Path(args.env_file)
    if not env_path.is_file():
        log.error("配置文件不存在: %s", env_path)
        sys.exit(1)

    try:
        cfg = load_pipeline_config(env_path, args.hdfs_base)
    except ValueError as exc:
        log.error("%s", exc)
        sys.exit(1)

    log.info("ETL start -> %s (env=%s)", cfg.mysql_dsn_label, env_path)

    loader = MrToMysqlLoader(cfg)
    loader.test_connection()
    log.info("MySQL connection OK")

    local = Path(args.local_dir) if args.local_dir else None
    loader.run(local_dir=local)

    try:
        from analytics.scripts.invalidate_bi_cache import invalidate_backend_bi_cache

        invalidate_backend_bi_cache()
    except Exception as exc:
        log.warning("BI cache invalidate failed: %s", exc)


if __name__ == "__main__":
    main()
