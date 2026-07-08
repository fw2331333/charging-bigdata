"""BI 视图配置（对标 Davinci v3 数据视图）。"""

from pydantic import BaseModel, Field


class ChartViewConfig(BaseModel):
    chart_key: str = Field(..., description="图表标识，如 v1、p1")
    title: str
    chart_type: str = Field(..., description="line|bar|scatter|pie|heatmap")
    data_source: str = Field(..., description="API 路径或表名")
    drill_route: str | None = Field(None, description="下钻目标路由")
    grid_area: str | None = None
    sort_order: int = 0
    enabled: bool = True


class ChartViewUpdate(BaseModel):
    title: str | None = None
    drill_route: str | None = None
    enabled: bool | None = None
    sort_order: int | None = None
