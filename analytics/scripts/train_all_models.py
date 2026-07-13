#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""训练四项预测模型：费用、充电时间、平台、SOC，并输出评估指标。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics.config import MODELS_DIR
from analytics.fee_models import train_fee_with_comparison
from analytics.ml_data import (
    duration_feature_names,
    duration_features,
    parse_dsv13r2_rows,
    parse_nvv2t_rows,
    platform_feature_names,
    platform_features,
    soc_feature_names,
    soc_features,
)
from analytics.ml_train_utils import (
    SOC_REGRESSOR_PARAMS,
    train_rf_classifier,
    train_rf_regressor,
)
from sklearn.preprocessing import LabelEncoder

DEFAULT_LOCAL_NVV = Path(r"F:\项目2资料\数据集\nvv2t_md.csv")
DEFAULT_LOCAL_DSV = Path(r"F:\项目2资料\数据集\dsv13r2.csv")


def _save_bundle(path: Path, bundle: dict) -> None:
    import joblib

    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path)


def train_fee(rows: list[dict]) -> tuple[dict, dict]:
    return train_fee_with_comparison(rows)


def train_duration(rows: list[dict]) -> tuple[dict, dict]:
    x, y = [], []
    for row in rows:
        f = duration_features(row)
        if f is None:
            continue
        try:
            hrs = float(row["chargeTimeHrs"])
        except (KeyError, ValueError):
            continue
        x.append(f)
        y.append(hrs)
    if len(x) < 50:
        raise RuntimeError("充电时间预测样本不足")
    model, metrics = train_rf_regressor(np.array(x), np.array(y))
    metrics["task"] = "duration"
    bundle = {
        "model": model,
        "feature_names": duration_feature_names(),
        "task": "duration",
        "metrics": metrics,
    }
    return bundle, metrics


def train_platform(rows: list[dict]) -> tuple[dict, dict]:
    x, labels = [], []
    for row in rows:
        f = platform_features(row)
        if f is None:
            continue
        p = (row.get("platform") or "").strip().lower()
        if p not in ("android", "ios"):
            continue
        x.append(f)
        labels.append(p)
    if len(x) < 50:
        raise RuntimeError("平台预测样本不足")
    enc = LabelEncoder()
    y = enc.fit_transform(labels)
    model, metrics = train_rf_classifier(np.array(x), y)
    metrics["task"] = "platform"
    metrics["classes"] = list(enc.classes_)
    bundle = {
        "model": model,
        "label_encoder": enc,
        "feature_names": platform_feature_names(),
        "task": "platform",
        "metrics": metrics,
    }
    return bundle, metrics


def train_soc(
    hdfs_path: str | None, local_path: str | None, max_rows: int
) -> tuple[dict, dict]:
    rows = parse_dsv13r2_rows(hdfs_path, local_path, max_rows)
    x = [soc_features(r) for r in rows]
    y = [r["soc"] for r in rows]
    if len(x) < 50:
        raise RuntimeError("SOC预测样本不足")
    model, metrics = train_rf_regressor(
        np.array(x), np.array(y), params=SOC_REGRESSOR_PARAMS
    )
    metrics["task"] = "soc"
    bundle = {
        "model": model,
        "feature_names": soc_feature_names(),
        "task": "soc",
        "metrics": metrics,
    }
    return bundle, metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="训练四项ML模型")
    parser.add_argument("--hdfs-path", default="/Car/nvv2t_md.csv")
    parser.add_argument("--hdfs-dsv", default="/Car/dsv13r2.csv")
    parser.add_argument("--local-nvv", default=str(DEFAULT_LOCAL_NVV))
    parser.add_argument("--local-dsv", default=str(DEFAULT_LOCAL_DSV))
    parser.add_argument("--use-hdfs", action="store_true")
    parser.add_argument("--max-rows", type=int, default=80000)
    args = parser.parse_args()

    if args.use_hdfs:
        nvv_rows = parse_nvv2t_rows(hdfs_path=args.hdfs_path, max_rows=args.max_rows)
        dsv_h, dsv_l = args.hdfs_dsv, None
    else:
        nvv_rows = parse_nvv2t_rows(local_path=args.local_nvv, max_rows=args.max_rows)
        dsv_h, dsv_l = None, args.local_dsv

    all_metrics: dict = {}
    tasks = [
        ("fee_model.pkl", train_fee(nvv_rows)),
        ("duration_model.pkl", train_duration(nvv_rows)),
        ("platform_model.pkl", train_platform(nvv_rows)),
        ("soc_model.pkl", train_soc(dsv_h, dsv_l, args.max_rows)),
    ]
    for fname, (bundle, metrics) in tasks:
        _save_bundle(MODELS_DIR / fname, bundle)
        all_metrics[metrics["task"]] = metrics
        print(f"[OK] {fname}: {json.dumps(metrics, ensure_ascii=True)}")

    metrics_path = MODELS_DIR / "metrics.json"
    metrics_path.write_text(
        json.dumps(all_metrics, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"指标已保存: {metrics_path}")


if __name__ == "__main__":
    main()
