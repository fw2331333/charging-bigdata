"""健康检查。"""

from fastapi import APIRouter

router = APIRouter(tags=["健康检查"])


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "charging-bigdata-backend"}
