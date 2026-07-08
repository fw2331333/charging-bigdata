"""BI 视图配置仓储。"""

import pymysql

from app.schemas.views import ChartViewConfig


class ViewConfigRepository:
    @staticmethod
    def _table_exists(conn: pymysql.connections.Connection) -> bool:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_name = 'bi_chart_view'
                LIMIT 1
                """
            )
            return cur.fetchone() is not None

    def list_enabled(self, conn: pymysql.connections.Connection) -> list[ChartViewConfig]:
        if not self._table_exists(conn):
            return []
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT chart_key, title, chart_type, data_source, drill_route, grid_area, sort_order, enabled
                FROM bi_chart_view
                WHERE enabled = 1
                ORDER BY sort_order, chart_key
                """
            )
            rows = cur.fetchall()
        return [ChartViewConfig(**row) for row in rows]

    def upsert(self, conn: pymysql.connections.Connection, item: ChartViewConfig) -> None:
        if not self._table_exists(conn):
            return
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO bi_chart_view
                    (chart_key, title, chart_type, data_source, drill_route, grid_area, sort_order, enabled)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    chart_type = VALUES(chart_type),
                    data_source = VALUES(data_source),
                    drill_route = VALUES(drill_route),
                    grid_area = VALUES(grid_area),
                    sort_order = VALUES(sort_order),
                    enabled = VALUES(enabled)
                """,
                (
                    item.chart_key,
                    item.title,
                    item.chart_type,
                    item.data_source,
                    item.drill_route,
                    item.grid_area,
                    item.sort_order,
                    int(item.enabled),
                ),
            )
        conn.commit()

    def ensure_seed(self, conn: pymysql.connections.Connection, defaults: list[ChartViewConfig]) -> None:
        if not self._table_exists(conn):
            return
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM bi_chart_view")
            if (cur.fetchone() or {}).get("c", 0) > 0:
                return
        for item in defaults:
            self.upsert(conn, item)
