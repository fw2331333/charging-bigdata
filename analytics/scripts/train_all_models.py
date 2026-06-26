#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""训练四项预测模型：费用、充电时间、平台、SOC，并输出评估指标。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics.config import MODELS_DIR
from analytics.fee_models import train_fee_with_comparison
from analytics.ml_data import (
    parse_dsv13r2_rows,
    parse_nvv2t_rows,
    duration_feature_names,
    duration_features,
    platform_feature_names,
    platform_features,
    soc_feature_names,
    soc_features,
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

import numpy as np

DEFAULT_LOCAL_NVV = Path(r"F:\项目2资料\数据集\nvv2t_md.csv")
DEFAULT_LOCAL_DSV = Path(r"F:\项目2资料\数据集\dsv13r2.csv")


def _save_bundle(path: Path, bundle: dict) -> None:
    import joblib
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path)


def train_fee(rows: list[dict]) -> tuple[dict, dict]:
    """费用预测：线性回归 vs XGBoost 对比后选优（见 analytics/fee_models.py）。"""
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
    x_arr, y_arr = np.array(x), np.array(y)
    x_train, x_test, y_train, y_test = train_test_split(x_arr, y_arr, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=120, random_state=42, n_jobs=-1)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    metrics = {
        "task": "duration",
        "r2": round(float(r2_score(y_test, pred)), 4),
        "mae": round(float(mean_absolute_error(y_test, pred)), 4),
        "mse": round(float(mean_squared_error(y_test, pred)), 4),
        "samples": len(x),
    }
    bundle = {"model": model, "feature_names": duration_feature_names(), "task": "duration", "metrics": metrics}
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
    x_arr = np.array(x)
    x_train, x_test, y_train, y_test = train_test_split(
        x_arr, y, test_size=0.2, random_state=42, stratify=y
    )
    model = RandomForestClassifier(n_estimators=120, random_state=42, n_jobs=-1)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    metrics = {
        "task": "platform",
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "f1": round(float(f1_score(y_test, pred, average="weighted")), 4),
        "samples": len(x),
        "classes": list(enc.classes_),
    }
    bundle = {
        "model": model,
        "label_encoder": enc,
        "feature_names": platform_feature_names(),
        "task": "platform",
        "metrics": metrics,
    }
    return bundle, metrics


def train_soc(hdfs_path: str | None, local_path: str | None, max_rows: int) -> tuple[dict, dict]:
    rows = parse_dsv13r2_rows(hdfs_path, local_path, max_rows)
    x = [soc_features(r) for r in rows]
    y = [r["soc"] for r in rows]
    if len(x) < 50:
        raise RuntimeError("SOC预测样本不足")
    x_arr, y_arr = np.array(x), np.array(y)
    x_train, x_test, y_train, y_test = train_test_split(x_arr, y_arr, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=120, random_state=42, n_jobs=-1)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    metrics = {
        "task": "soc",
        "r2": round(float(r2_score(y_test, pred)), 4),
        "mae": round(float(mean_absolute_error(y_test, pred)), 4),
        "mse": round(float(mean_squared_error(y_test, pred)), 4),
        "samples": len(x),
    }
    bundle = {"model": model, "feature_names": soc_feature_names(), "task": "soc", "metrics": metrics}
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
