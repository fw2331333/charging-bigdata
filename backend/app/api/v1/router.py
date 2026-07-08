"""API v1 路由聚合。"""

from fastapi import APIRouter

from app.api.v1.endpoints import assistant, auth, bi, health, predict, views

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(assistant.router)
api_router.include_router(views.router)
api_router.include_router(predict.router)
api_router.include_router(bi.router)
