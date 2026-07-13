"""启动时从打包的 JSON 同步 v6/v7 表（无需 Hadoop）。"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pymysql

from app.core.config import settings

log = logging.getLogger(__name__)

SEED_FILE = Path(__file__).with_name("v6_v7_data.json")


def _connect() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE,
        charset="utf8mb4",
        autocommit=True,
    )


def _column_exists(conn: pymysql.connections.Connection, table: str, column: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
            """,
            (settings.MYSQL_DATABASE, table, column),
        )
        return int(cur.fetchone()[0]) > 0


def _migrate_schema_if_needed(conn: pymysql.connections.Connection) -> None:
    if _column_exists(conn, "t_voltage_current_relation", "voltage_change_rate"):
        return
    if not _column_exists(conn, "t_voltage_current_relation", "record_time"):
        return
    migration = Path("/app/sql/migrations/009_v6_v7_manual_align.sql")
    if not migration.is_file():
        migration = Path(__file__).resolve().parents[3] / "sql" / "migrations" / "009_v6_v7_manual_align.sql"
    if not migration.is_file():
        raise FileNotFoundError(f"migration not found: {migration}")
    sql = migration.read_text(encoding="utf-8")
    statements = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]
    with conn.cursor() as cur:
        for stmt in statements:
            if stmt.upper().startswith("USE "):
                continue
            cur.execute(stmt)
    log.info("Applied v6/v7 schema migration 009")


def sync_v6_v7_seed() -> bool:
    """将 backend/app/seed/v6_v7_data.json 写入 MySQL（幂等，每次启动执行）。"""
    if not SEED_FILE.is_file():
        log.warning("v6/v7 seed file missing: %s", SEED_FILE)
        return False

    payload = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    v6 = payload.get("v6") or []
    v7 = payload.get("v7") or []
    version = payload.get("version", "unknown")
    if not v6 and not v7:
        log.warning("v6/v7 seed payload empty")
        return False

    conn = _connect()
    try:
        _migrate_schema_if_needed(conn)
        if not _column_exists(conn, "t_voltage_current_relation", "voltage_change_rate"):
            log.warning("v6 table schema still old; cannot sync seed")
            return False
        if not _column_exists(conn, "t_soc_temperature", "battery_status"):
            log.warning("v7 table schema still old; cannot sync seed")
            return False

        with conn.cursor() as cur:
            if v6:
                cur.execute("DELETE FROM t_voltage_current_relation")
                cur.executemany(
                    """
                    INSERT INTO t_voltage_current_relation
                    (record_hour, voltage_change_rate, current_change_rate)
                    VALUES (%s, %s, %s)
                    """,
                    [
                        (r["record_hour"], r["voltage_change_rate"], r["current_change_rate"])
                        for r in v6
                    ],
                )
            if v7:
                cur.execute("DELETE FROM t_soc_temperature")
                cur.executemany(
                    """
                    INSERT INTO t_soc_temperature
                    (battery_status, avg_max_temperature, avg_min_temperature,
                     var_max_temperature, var_min_temperature)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [
                        (
                            r["battery_status"],
                            r["avg_max_temperature"],
                            r["avg_min_temperature"],
                            r["var_max_temperature"],
                            r["var_min_temperature"],
                        )
                        for r in v7
                    ],
                )

        log.info("Synced v6/v7 seed %s (v6=%d rows, v7=%d rows)", version, len(v6), len(v7))
        return True
    finally:
        conn.close()
