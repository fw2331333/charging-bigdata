# -*- coding: utf-8 -*-
"""
电池性能分类指标（手册 §4.6 ds_battery7_1.py）。

基于 dsv13r2：构造 voltage_diff / temperature_diff / abs_current 特征，
以 available_energy < 5 kWh 为故障标签，训练随机森林并输出
classification_report 与 confusion_matrix。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from analytics.config import MODELS_DIR
from analytics.ml_data import parse_dsv13r2_rows

DEFAULT_LOCAL_DSV = Path(r"F:\项目2资料\数据集\dsv13r2.csv")
ENERGY_FAILURE_THRESHOLD = 5.0
FALLBACK_FAILURE_THRESHOLD = 10.0
MIN_CLASS_SAMPLES = 20
CLASS_LABELS = ["正常", "能量不足"]
FEATURE_NAMES = ["soc", "voltage_diff", "temperature_diff", "abs_current"]


def _resolve_failure_threshold(rows: list[dict[str, float]]) -> tuple[float, str]:
    """手册默认 5kWh；若数据集中无足够正样本则回退到 10kWh。"""
    n = len(rows)
    below5 = sum(1 for r in rows if r["energy"] < ENERGY_FAILURE_THRESHOLD)
    if MIN_CLASS_SAMPLES <= below5 <= n - MIN_CLASS_SAMPLES:
        return ENERGY_FAILURE_THRESHOLD, f"available_energy < {ENERGY_FAILURE_THRESHOLD} kWh 视为能量不足"
    below10 = sum(1 for r in rows if r["energy"] < FALLBACK_FAILURE_THRESHOLD)
    if MIN_CLASS_SAMPLES <= below10 <= n - MIN_CLASS_SAMPLES:
        return (
            FALLBACK_FAILURE_THRESHOLD,
            f"available_energy < {FALLBACK_FAILURE_THRESHOLD} kWh 视为能量不足"
            f"（数据集无 <{ENERGY_FAILURE_THRESHOLD}kWh 样本，采用兼容阈值）",
        )
    energies = sorted(r["energy"] for r in rows)
    median = energies[len(energies) // 2]
    return median, f"available_energy < {median:.2f} kWh 视为能量不足（按数据中位数划分）"


def _rows_to_xy(
    rows: list[dict[str, float]], threshold: float
) -> tuple[np.ndarray, np.ndarray]:
    x, y = [], []
    for row in rows:
        if row["min_cell_v"] > row["max_cell_v"]:
            continue
        if row["min_temp"] > row["max_temp"]:
            continue
        x.append(
            [
                row["soc"],
                row["max_cell_v"] - row["min_cell_v"],
                row["max_temp"] - row["min_temp"],
                abs(row["charge_current"]),
            ]
        )
        y.append(1 if row["energy"] < threshold else 0)
    return np.array(x), np.array(y)


def build_performance_report(
    *,
    hdfs_path: str | None = None,
    local_path: str | Path | None = None,
    max_rows: int = 80_000,
    test_size: float = 0.2,
    n_estimators: int = 200,
    random_state: int = 42,
) -> dict[str, Any]:
    """训练故障分类模型并返回手册 §4.6 要求的性能指标。"""
    local = str(local_path) if local_path else None
    rows = parse_dsv13r2_rows(hdfs_path, local, max_rows)
    threshold, target_rule = _resolve_failure_threshold(rows)
    x_raw, y = _rows_to_xy(rows, threshold)
    if len(x_raw) < 50:
        raise RuntimeError("电池性能分类样本不足")
    if len(set(y.tolist())) < 2:
        raise RuntimeError("电池性能分类仅含单一类别，无法生成分类报告")

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x_raw)
    x_train, x_test, y_train, y_test = train_test_split(
        x_scaled, y, test_size=test_size, random_state=random_state, stratify=y
    )

    model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)

    report_dict = classification_report(
        y_test,
        y_pred,
        labels=[0, 1],
        target_names=CLASS_LABELS,
        output_dict=True,
        zero_division=0,
    )
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, labels=[0, 1], zero_division=0
    )
    cm = confusion_matrix(y_test, y_pred).tolist()

    per_class = []
    for i, label in enumerate(CLASS_LABELS):
        key = label
        block = report_dict.get(key, {})
        per_class.append(
            {
                "class": label,
                "class_index": i,
                "precision": round(float(block.get("precision", precision[i])), 4),
                "recall": round(float(block.get("recall", recall[i])), 4),
                "f1_score": round(float(block.get("f1-score", f1[i])), 4),
                "support": int(block.get("support", support[i])),
            }
        )

    result: dict[str, Any] = {
        "task": "battery_failure_classification",
        "source": "dsv13r2.csv",
        "algorithm": "RandomForestClassifier",
        "n_estimators": n_estimators,
        "target_rule": target_rule,
        "failure_threshold_kwh": threshold,
        "features": FEATURE_NAMES,
        "class_labels": CLASS_LABELS,
        "samples": int(len(x_raw)),
        "train_samples": int(len(x_train)),
        "test_samples": int(len(x_test)),
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "accuracy_percent": round(float(accuracy_score(y_test, y_pred)) * 100, 2),
        "macro_avg": {
            "precision": round(float(report_dict["macro avg"]["precision"]), 4),
            "recall": round(float(report_dict["macro avg"]["recall"]), 4),
            "f1_score": round(float(report_dict["macro avg"]["f1-score"]), 4),
        },
        "weighted_avg": {
            "precision": round(float(report_dict["weighted avg"]["precision"]), 4),
            "recall": round(float(report_dict["weighted avg"]["recall"]), 4),
            "f1_score": round(float(report_dict["weighted avg"]["f1-score"]), 4),
        },
        "per_class": per_class,
        "confusion_matrix": cm,
        "confusion_matrix_labels": {
            "y_true": CLASS_LABELS,
            "y_pred": CLASS_LABELS,
        },
        "classification_report_text": classification_report(
            y_test, y_pred, labels=[0, 1], target_names=CLASS_LABELS, zero_division=0
        ),
    }
    return result


def save_performance_report(report: dict[str, Any], out_dir: Path | None = None) -> Path:
    out = (out_dir or MODELS_DIR) / "performance_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def train_and_save(
    *,
    local_path: str | Path | None = None,
    hdfs_path: str | None = None,
    max_rows: int = 80_000,
) -> dict[str, Any]:
    report = build_performance_report(
        hdfs_path=hdfs_path,
        local_path=local_path or DEFAULT_LOCAL_DSV,
        max_rows=max_rows,
    )
    path = save_performance_report(report)
    report["saved_to"] = str(path)
    return report
