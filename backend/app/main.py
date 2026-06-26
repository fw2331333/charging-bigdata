"""FastAPI 应用入口。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["首页"])
def root() -> dict:
    return {
        "project": settings.PROJECT_NAME,
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
        "note": "原始 CSV 由用户上传至 HDFS /Car/，本服务不存储数据集",
    }
