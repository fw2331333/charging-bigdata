"""预测业务：加载四项训练模型进行推理。"""

import json
import sys
from pathlib import Path

# 允许 backend 引用 analytics.ml_data（本地 backend/ 与 Docker /app 均适用）
def _analytics_root() -> Path:
    here = Path(__file__).resolve()
    for depth in (3, 2, 4):
        root = here.parents[depth]
        if (root / "analytics" / "ml_data.py").exists():
            return root
    return here.parents[3]


_ROOT = _analytics_root()
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from analytics.ml_data import (
    charge_hours_between,
    duration_features,
    platform_features,
    session_features,
    session_row_from_datetimes,
    soc_features,
    weekday_label,
)

from app.core.config import settings
from app.schemas.predict import (
    ModelMetricsResponse,
    PerformanceReportResponse,
    PredictDurationRequest,
    PredictDurationResponse,
    PredictFeeRequest,
    PredictFeeResponse,
    PredictPlatformRequest,
    PredictPlatformResponse,
    PredictSocRequest,
    PredictSocResponse,
)


class PredictService:
    MODEL_FILES = ("fee_model.pkl", "duration_model.pkl", "platform_model.pkl", "soc_model.pkl")

    def __init__(self) -> None:
        self.models_dir = Path(settings.ANALYTICS_OUTPUT_DIR) / "models"
        self._model_cache: dict[str, dict] = {}

    def models_status(self) -> dict[str, bool]:
        return {name: (self.models_dir / name).is_file() for name in self.MODEL_FILES}

    def warmup_models(self) -> dict[str, bool]:
        loaded: dict[str, bool] = {}
        for name in self.MODEL_FILES:
            loaded[name] = self._load(name) is not None
        return loaded

    def reload_models(self) -> list[str]:
        """清空内存模型缓存，下次预测时从磁盘重新加载。"""
        self._model_cache.clear()
        return [p.name for p in sorted(self.models_dir.glob("*.pkl"))]

    def _load(self, name: str) -> dict | None:
        if name in self._model_cache:
            return self._model_cache[name]
        path = self.models_dir / name
        if not path.exists():
            return None
        try:
            import joblib
            bundle = joblib.load(path)
            parsed = bundle if isinstance(bundle, dict) else {"model": bundle}
            self._model_cache[name] = parsed
            return parsed
        except Exception:
            return None

    def get_metrics(self) -> ModelMetricsResponse:
        p = self.models_dir / "metrics.json"
        if p.exists():
            return ModelMetricsResponse(metrics=json.loads(p.read_text(encoding="utf-8")))
        return ModelMetricsResponse(metrics={})

    def get_performance_report(self) -> PerformanceReportResponse:
        p = self.models_dir / "performance_report.json"
        if p.exists():
            return PerformanceReportResponse(report=json.loads(p.read_text(encoding="utf-8")))
        return PerformanceReportResponse(report={})

    def predict_fee(self, req: PredictFeeRequest) -> PredictFeeResponse:
        bundle = self._load("fee_model.pkl")
        charge_hrs = (
            req.charge_time_hrs
            if req.charge_time_hrs is not None
            else charge_hours_between(req.start_at, req.end_at)
        )
        if bundle and "model" in bundle:
            row = session_row_from_datetimes(
                req.start_at,
                req.end_at,
                kwh_total=req.kwh_total,
                weekday=req.weekday,
                platform=req.platform,
                facility_type=req.facility_type,
                station_id=req.station_id,
                charge_time_hrs=charge_hrs,
            )
            f = session_features(row)
            if f:
                fee = float(bundle["model"].predict([f])[0])
                algo = str(bundle.get("algorithm", ""))
                return PredictFeeResponse(
                    predicted_fee=round(fee, 2),
                    algorithm=algo,
                )
        est = max(0.0, req.kwh_total * 1.2 + charge_hrs * 0.5)
        return PredictFeeResponse(predicted_fee=round(est, 2), message="模型未加载，使用估算")

    def predict_duration(self, req: PredictDurationRequest) -> PredictDurationResponse:
        bundle = self._load("duration_model.pkl")
        if bundle and "model" in bundle:
            row = session_row_from_datetimes(
                req.start_at,
                req.end_at,
                kwh_total=req.kwh_total,
                weekday=req.weekday,
                platform=req.platform,
                facility_type=req.facility_type,
                station_id=req.station_id,
            )
            f = duration_features(row)
            if f:
                hrs = float(bundle["model"].predict([f])[0])
                return PredictDurationResponse(predicted_hours=round(max(0.0, hrs), 2))
        est = max(0.5, req.kwh_total / 10.0)
        return PredictDurationResponse(predicted_hours=round(est, 2), message="模型未加载，使用估算")

    def predict_platform(self, req: PredictPlatformRequest) -> PredictPlatformResponse:
        bundle = self._load("platform_model.pkl")
        if bundle and "model" in bundle:
            row = {
                "kwhTotal": str(req.kwh_total),
                "charging_fees": str(req.charging_fees),
                "chargeTimeHrs": str(req.charge_time_hrs),
                "startTime": str(req.start_at.hour),
                "weekday": req.weekday or weekday_label(req.start_at),
                "facilityType": str(req.facility_type),
            }
            f = platform_features(row)
            if f:
                pred = bundle["model"].predict([f])[0]
                enc = bundle.get("label_encoder")
                label = enc.inverse_transform([pred])[0] if enc else ("android" if pred == 1 else "ios")
                return PredictPlatformResponse(predicted_platform=str(label))
        return PredictPlatformResponse(predicted_platform="android", message="模型未加载，默认android")

    def predict_soc(self, req: PredictSocRequest) -> PredictSocResponse:
        bundle = self._load("soc_model.pkl")
        if bundle and "model" in bundle:
            row = {
                "pack_voltage": req.pack_voltage,
                "charge_current": req.charge_current,
                "max_cell_v": req.max_cell_voltage,
                "min_cell_v": req.min_cell_voltage,
                "max_temp": req.max_temperature,
                "min_temp": req.min_temperature,
                "energy": req.available_energy,
                "capacity": req.available_capacity,
            }
            f = soc_features(row)
            soc = float(bundle["model"].predict([f])[0])
            return PredictSocResponse(predicted_soc=round(max(0.0, min(100.0, soc)), 2))
        return PredictSocResponse(predicted_soc=50.0, message="模型未加载，使用默认值")
