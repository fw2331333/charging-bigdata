"""健康检查与就绪探针。"""

import pymysql
from fastapi import APIRouter, Depends

from app.api.deps import get_db
from app.services.predict_service import PredictService

router = APIRouter(tags=["健康检查"])
_predict_service = PredictService()


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "charging-bigdata-backend"}


@router.get("/health/ready")
def readiness_check(db: pymysql.connections.Connection = Depends(get_db)) -> dict:
    mysql_ok = False
    mysql_error: str | None = None
    try:
        with db.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        mysql_ok = True
    except Exception as exc:
        mysql_error = str(exc)

    models = _predict_service.models_status()
    models_ok = all(models.values())

    body: dict = {
        "ready": mysql_ok and models_ok,
        "mysql": mysql_ok,
        "models": models,
    }
    if mysql_error:
        body["mysql_error"] = mysql_error
    return body
