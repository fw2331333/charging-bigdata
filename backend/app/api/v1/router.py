"""API v1 路由聚合。"""

from fastapi import APIRouter

from app.api.v1.endpoints import bi, health, predict

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(predict.router)
api_router.include_router(bi.router)
