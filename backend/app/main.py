"""FastAPI 应用入口。"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.rag.retriever import get_retriever
from app.seed.sync_v6_v7 import sync_v6_v7_seed
from app.services.predict_service import PredictService


@asynccontextmanager
async def lifespan(_app: FastAPI):
    loaded = PredictService().warmup_models()
    print(f"[startup] ML models warmed: {loaded}")
    try:
        synced = await asyncio.to_thread(sync_v6_v7_seed)
        if synced:
            print("[startup] v6/v7 seed synced from bundled JSON")
    except Exception as exc:
        print(f"[startup] v6/v7 seed sync skipped: {exc}")
    if settings.RAG_USE_VECTOR:
        try:
            retriever = await asyncio.to_thread(get_retriever)
            print(
                f"[startup] RAG retriever ready: "
                f"backend={retriever.embedding_backend}, chunks={len(retriever.chunks)}"
            )
        except Exception as exc:
            print(f"[startup] RAG warmup failed (lexical fallback): {exc}")
    yield


app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)

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
