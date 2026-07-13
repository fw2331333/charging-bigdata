# -*- coding: utf-8 -*-
"""
充电费用预测：线性回归与 XGBoost 对比训练。

课程指导文档 10.2 推荐费用预测使用「线性回归、XGBoost、LightGBM」。
本模块删除原 RandomForest 方案，在同一训练/测试集上对比线性回归与 XGBoost，
按测试集 R² 选优（同分时取 MAE 更低者），并将最优模型写入 fee_model.pkl。
"""
from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor  # 费用对比候选；未安装时 pip install -r analytics/requirements.txt

from analytics.ml_data import fee_feature_names, session_features
from analytics.ml_train_utils import XGB_FEE_PARAMS, assess_fit_quality


def _eval_regression(model, x_true: np.ndarray, y_true: np.ndarray) -> dict[str, float]:
    """在指定集上计算回归评估指标。"""
    pred = model.predict(x_true)
    return {
        "r2": round(float(r2_score(y_true, pred)), 4),
        "mae": round(float(mean_absolute_error(y_true, pred)), 4),
        "mse": round(float(mean_squared_error(y_true, pred)), 4),
    }


def _pick_best(
    candidates: dict[str, dict[str, Any]],
) -> tuple[str, Any, dict[str, float]]:
    """
    从候选模型中选出最优：
    1. 测试集 R² 更高者优先；
    2. R² 相同则 MAE 更低者优先。
    """
    ranked = sorted(
        candidates.items(),
        key=lambda item: (item[1]["metrics"]["r2"], -item[1]["metrics"]["mae"]),
        reverse=True,
    )
    name, payload = ranked[0]
    return name, payload["model"], payload["metrics"]


def train_fee_with_comparison(rows: list[dict]) -> tuple[dict, dict]:
    """
    训练费用预测模型并输出对比结果。

    Returns:
        bundle: 含最优 model、algorithm、model_comparison 等，供 joblib 持久化
        metrics: 写入 metrics.json 的 fee 节点（含对比表与入选算法）
    """
    x, y = [], []
    for row in rows:
        features = session_features(row)
        if features is None:
            continue
        try:
            fee = float(row["charging_fees"])
        except (KeyError, ValueError):
            continue
        x.append(features)
        y.append(fee)

    if len(x) < 50:
        raise RuntimeError("费用预测样本不足")

    x_arr, y_arr = np.array(x), np.array(y)
    x_train, x_test, y_train, y_test = train_test_split(
        x_arr, y_arr, test_size=0.2, random_state=42
    )

    # 候选 1：线性回归（可解释性强，作为基线）
    lr_model = LinearRegression()
    lr_model.fit(x_train, y_train)
    lr_test = _eval_regression(lr_model, x_test, y_test)
    lr_train = _eval_regression(lr_model, x_train, y_train)

    xgb_model = XGBRegressor(**XGB_FEE_PARAMS)
    xgb_model.fit(x_train, y_train)
    xgb_test = _eval_regression(xgb_model, x_test, y_test)
    xgb_train = _eval_regression(xgb_model, x_train, y_train)

    candidates = {
        "linear_regression": {"model": lr_model, "metrics": lr_test, "train_r2": lr_train["r2"]},
        "xgboost": {"model": xgb_model, "metrics": xgb_test, "train_r2": xgb_train["r2"]},
    }
    selected_name, selected_model, selected_metrics = _pick_best(candidates)
    selected_train_r2 = candidates[selected_name]["train_r2"]
    fit_status = assess_fit_quality(selected_train_r2, selected_metrics["r2"])

    model_comparison = {
        "linear_regression": {**lr_test, "train_r2": lr_train["r2"]},
        "xgboost": {**xgb_test, "train_r2": xgb_train["r2"]},
        "selected": selected_name,
        "selection_criterion": "测试集 R² 更高者优先；同分时 MAE 更低者优先",
    }

    metrics = {
        "task": "fee",
        "algorithm": selected_name,
        **selected_metrics,
        "train_r2": selected_train_r2,
        "test_r2": selected_metrics["r2"],
        "fit_status": fit_status,
        "hyperparams": XGB_FEE_PARAMS if selected_name == "xgboost" else {"model": "LinearRegression"},
        "samples": len(x),
        "model_comparison": model_comparison,
    }

    bundle = {
        "model": selected_model,
        "algorithm": selected_name,
        "feature_names": fee_feature_names(),
        "task": "fee",
        "metrics": metrics,
        "model_comparison": model_comparison,
    }
    return bundle, metrics
