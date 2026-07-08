"""机器学习预测接口（四项均已实现）。"""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, require_admin
from app.schemas.auth import UserInfo
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
from app.services.predict_service import PredictService

router = APIRouter(prefix="/predict", tags=["预测"])
auth_router = APIRouter(dependencies=[Depends(get_current_user)])
service = PredictService()


@auth_router.get("/metrics", response_model=ModelMetricsResponse, summary="模型评估指标")
def get_metrics() -> ModelMetricsResponse:
    return service.get_metrics()


@auth_router.get(
    "/performance-report",
    response_model=PerformanceReportResponse,
    summary="电池性能分类报告（§4.6 Classification Report）",
)
def get_performance_report() -> PerformanceReportResponse:
    return service.get_performance_report()


@auth_router.post("/fee", response_model=PredictFeeResponse, summary="预测充电费用")
def predict_fee(body: PredictFeeRequest) -> PredictFeeResponse:
    return service.predict_fee(body)


@auth_router.post("/duration", response_model=PredictDurationResponse, summary="预测充电时间")
def predict_duration(body: PredictDurationRequest) -> PredictDurationResponse:
    return service.predict_duration(body)


@auth_router.post("/platform", response_model=PredictPlatformResponse, summary="预测用户平台")
def predict_platform(body: PredictPlatformRequest) -> PredictPlatformResponse:
    return service.predict_platform(body)


@auth_router.post("/soc", response_model=PredictSocResponse, summary="预测剩余电量SOC")
def predict_soc(body: PredictSocRequest) -> PredictSocResponse:
    return service.predict_soc(body)


@router.post("/reload-models", summary="重新加载磁盘模型（管理员）")
def reload_models(_: UserInfo = Depends(require_admin)) -> dict:
    files = service.reload_models()
    return {"reloaded": True, "model_files": files}


router.include_router(auth_router)
