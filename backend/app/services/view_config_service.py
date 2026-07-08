"""BI 视图配置服务。"""

import pymysql

from app.repositories.view_config_repository import ViewConfigRepository
from app.schemas.views import ChartViewConfig, ChartViewUpdate

DEFAULT_VIEWS: list[ChartViewConfig] = [
    ChartViewConfig(chart_key="v1", title="组电压与充电电流", chart_type="line", data_source="/bi/voltage-current", drill_route="/bda1", grid_area="v1", sort_order=1),
    ChartViewConfig(chart_key="v2", title="单体电压范围", chart_type="line", data_source="/bi/cell-voltage-range", drill_route="/bda2", grid_area="v2", sort_order=2),
    ChartViewConfig(chart_key="v3", title="电池温度趋势", chart_type="line", data_source="/bi/temperature", drill_route="/bda2", grid_area="v3", sort_order=3),
    ChartViewConfig(chart_key="v4", title="可用能量与容量", chart_type="line", data_source="/bi/energy-capacity", drill_route="/bda3", grid_area="v4", sort_order=4),
    ChartViewConfig(chart_key="v5", title="充电电流统计", chart_type="line", data_source="/bi/charge-current-stats", drill_route="/bda4", grid_area="v5", sort_order=5),
    ChartViewConfig(chart_key="v6", title="电压-电流关系", chart_type="scatter", data_source="/bi/voltage-current-relation", drill_route="/bda1", grid_area="v6", sort_order=6),
    ChartViewConfig(chart_key="v7", title="SOC区间平均温度", chart_type="bar", data_source="/bi/soc-temperature", drill_route="/bda2", grid_area="v7", sort_order=7),
    ChartViewConfig(chart_key="p1", title="单体电压占比", chart_type="pie", data_source="/bi/cell-voltage-range", drill_route="/bda2", grid_area="p1", sort_order=8),
    ChartViewConfig(chart_key="p2", title="充电电流占比", chart_type="pie", data_source="/bi/charge-current-stats", drill_route="/bda4", grid_area="p2", sort_order=9),
]


class ViewConfigService:
    def __init__(self) -> None:
        self.repo = ViewConfigRepository()

    def ensure_defaults(self, conn: pymysql.connections.Connection) -> None:
        self.repo.ensure_seed(conn, DEFAULT_VIEWS)

    def list_views(self, conn: pymysql.connections.Connection) -> list[ChartViewConfig]:
        self.ensure_defaults(conn)
        rows = self.repo.list_enabled(conn)
        return rows if rows else DEFAULT_VIEWS

    def update_view(
        self,
        conn: pymysql.connections.Connection,
        chart_key: str,
        patch: ChartViewUpdate,
    ) -> ChartViewConfig | None:
        views = {v.chart_key: v for v in self.list_views(conn)}
        current = views.get(chart_key)
        if not current:
            return None
        data = current.model_dump()
        for k, v in patch.model_dump(exclude_unset=True).items():
            data[k] = v
        updated = ChartViewConfig(**data)
        self.repo.upsert(conn, updated)
        return updated
