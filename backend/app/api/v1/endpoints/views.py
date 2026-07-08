"""BI 视图配置 API（对标 Davinci v3 数据视图）。"""

import pymysql
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_db, require_admin
from app.schemas.auth import UserInfo
from app.schemas.views import ChartViewConfig, ChartViewUpdate
from app.services.view_config_service import ViewConfigService

router = APIRouter(prefix="/views", tags=["视图配置"])
_auth = [Depends(get_current_user)]
service = ViewConfigService()


@router.get("", response_model=list[ChartViewConfig], summary="获取 BI 图表视图配置", dependencies=_auth)
def list_views(db: pymysql.connections.Connection = Depends(get_db)) -> list[ChartViewConfig]:
    return service.list_views(db)


@router.get("/{chart_key}", response_model=ChartViewConfig, summary="单个图表配置", dependencies=_auth)
def get_view(chart_key: str, db: pymysql.connections.Connection = Depends(get_db)) -> ChartViewConfig:
    for item in service.list_views(db):
        if item.chart_key == chart_key:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视图不存在")


@router.patch("/{chart_key}", response_model=ChartViewConfig, summary="更新视图（管理员）")
def patch_view(
    chart_key: str,
    body: ChartViewUpdate,
    db: pymysql.connections.Connection = Depends(get_db),
    _: UserInfo = Depends(require_admin),
) -> ChartViewConfig:
    updated = service.update_view(db, chart_key, body)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视图不存在")
    return updated
