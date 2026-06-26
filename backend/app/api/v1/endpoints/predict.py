"""机器学习预测接口（四项均已实现）。"""

from fastapi import APIRouter

from app.schemas.predict import (
    ModelMetricsResponse,
    PredictDurationRequest,
    PredictDurationResponse,
    PredictFeeRequest,
    PredictFeeResponse,
    PredictPlatformRequest,
    PredictPlatformResponse,
    PredictSocRequest,
    PredictSocResponse,
)
from app.services.predict_service import PredictService

router = APIRouter(prefix="/predict", tags=["预测"])
service = PredictService()


@router.get("/metrics", response_model=ModelMetricsResponse, summary="模型评估指标")
def get_metrics() -> ModelMetricsResponse:
    return service.get_metrics()


@router.post("/fee", response_model=PredictFeeResponse, summary="预测充电费用")
def predict_fee(body: PredictFeeRequest) -> PredictFeeResponse:
    return service.predict_fee(body)


@router.post("/duration", response_model=PredictDurationResponse, summary="预测充电时间")
def predict_duration(body: PredictDurationRequest) -> PredictDurationResponse:
    return service.predict_duration(body)


@router.post("/platform", response_model=PredictPlatformResponse, summary="预测用户平台")
def predict_platform(body: PredictPlatformRequest) -> PredictPlatformResponse:
    return service.predict_platform(body)


@router.post("/soc", response_model=PredictSocResponse, summary="预测剩余电量SOC")
def predict_soc(body: PredictSocRequest) -> PredictSocResponse:
    return service.predict_soc(body)
