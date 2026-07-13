#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""手册 §4.6 ds_battery7_1：电池故障分类性能指标与 Classification Report。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics.battery_performance import DEFAULT_LOCAL_DSV, train_and_save


def main() -> None:
    parser = argparse.ArgumentParser(description="§4.6 电池性能分类指标（ds_battery7_1）")
    parser.add_argument("--local-dsv", default=str(DEFAULT_LOCAL_DSV))
    parser.add_argument("--hdfs-dsv", default="/Car/dsv13r2.csv")
    parser.add_argument("--use-hdfs", action="store_true")
    parser.add_argument("--max-rows", type=int, default=80_000)
    args = parser.parse_args()

    if args.use_hdfs:
        report = train_and_save(hdfs_path=args.hdfs_dsv, max_rows=args.max_rows)
    else:
        report = train_and_save(local_path=args.local_dsv, max_rows=args.max_rows)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n已保存: {report.get('saved_to')}")


if __name__ == "__main__":
    main()
