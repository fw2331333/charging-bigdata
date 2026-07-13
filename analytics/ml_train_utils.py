# -*- coding: utf-8 -*-
"""ML 训练辅助：正则化超参、训练/测试对比、过拟合/欠拟合提示。"""
from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split

# 随机森林：限制树深与叶子样本，减轻过拟合
RF_REGRESSOR_PARAMS: dict[str, Any] = {
    "n_estimators": 100,
    "max_depth": 8,
    "min_samples_leaf": 5,
    "min_samples_split": 10,
    "max_features": "sqrt",
    "random_state": 42,
    "n_jobs": -1,
}

RF_CLASSIFIER_PARAMS: dict[str, Any] = {
    **RF_REGRESSOR_PARAMS,
}

# SOC 特征多、样本相关性强，进一步收紧
SOC_REGRESSOR_PARAMS: dict[str, Any] = {
    "n_estimators": 80,
    "max_depth": 6,
    "min_samples_leaf": 8,
    "min_samples_split": 12,
    "max_features": "sqrt",
    "random_state": 42,
    "n_jobs": -1,
}

XGB_FEE_PARAMS: dict[str, Any] = {
    "n_estimators": 120,
    "max_depth": 4,
    "learning_rate": 0.06,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "random_state": 42,
    "n_jobs": -1,
}

OVERFIT_R2_GAP = 0.12
UNDERFIT_TEST_R2 = 0.25


def assess_fit_quality(train_r2: float, test_r2: float) -> str:
    """返回 ok / overfit_risk / underfit_risk。"""
    if test_r2 < UNDERFIT_TEST_R2:
        return "underfit_risk"
    if train_r2 - test_r2 > OVERFIT_R2_GAP:
        return "overfit_risk"
    return "ok"


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "r2": round(float(r2_score(y_true, y_pred)), 4),
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "mse": round(float(mean_squared_error(y_true, y_pred)), 4),
    }


def train_rf_regressor(
    x: np.ndarray,
    y: np.ndarray,
    *,
    params: dict[str, Any] | None = None,
    test_size: float = 0.2,
) -> tuple[RandomForestRegressor, dict[str, Any]]:
    """训练随机森林回归并返回模型与含 train/test 对比的指标。"""
    p = params or RF_REGRESSOR_PARAMS
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=42
    )
    model = RandomForestRegressor(**p)
    model.fit(x_train, y_train)
    train_m = regression_metrics(y_train, model.predict(x_train))
    test_m = regression_metrics(y_test, model.predict(x_test))
    fit_status = assess_fit_quality(train_m["r2"], test_m["r2"])
    metrics = {
        **test_m,
        "train_r2": train_m["r2"],
        "train_mae": train_m["mae"],
        "test_r2": test_m["r2"],
        "fit_status": fit_status,
        "fit_note": _fit_note(fit_status, train_m["r2"], test_m["r2"]),
        "hyperparams": p,
        "samples": int(len(x)),
    }
    return model, metrics


def train_rf_classifier(
    x: np.ndarray,
    y: np.ndarray,
    *,
    params: dict[str, Any] | None = None,
    test_size: float = 0.2,
) -> tuple[RandomForestClassifier, dict[str, Any]]:
    p = params or RF_CLASSIFIER_PARAMS
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=42, stratify=y
    )
    model = RandomForestClassifier(**p)
    model.fit(x_train, y_train)
    train_pred = model.predict(x_train)
    test_pred = model.predict(x_test)
    train_acc = float(accuracy_score(y_train, train_pred))
    test_acc = float(accuracy_score(y_test, test_pred))
    gap = train_acc - test_acc
    if test_acc < 0.55:
        fit_status = "underfit_risk"
    elif gap > 0.08:
        fit_status = "overfit_risk"
    else:
        fit_status = "ok"
    metrics = {
        "accuracy": round(test_acc, 4),
        "train_accuracy": round(train_acc, 4),
        "f1": round(float(f1_score(y_test, test_pred, average="weighted")), 4),
        "fit_status": fit_status,
        "fit_note": _fit_note(fit_status, train_acc, test_acc, is_classifier=True),
        "hyperparams": p,
        "samples": int(len(x)),
    }
    return model, metrics


def _fit_note(status: str, train_score: float, test_score: float, *, is_classifier: bool = False) -> str:
    label = "准确率" if is_classifier else "R²"
    if status == "overfit_risk":
        return f"训练{label}({train_score:.3f})明显高于测试{label}({test_score:.3f})，存在过拟合风险"
    if status == "underfit_risk":
        return f"测试{label}({test_score:.3f})偏低，模型可能欠拟合，可适当增加特征或样本"
    return f"训练/测试{label}差距在可接受范围"
