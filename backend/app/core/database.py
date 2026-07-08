"""MySQL 连接池：供 Repository 层查询 MapReduce 入库结果。"""

from collections.abc import Generator
from contextlib import contextmanager

import pymysql
from dbutils.pooled_db import PooledDB
from pymysql.connections import Connection

from app.core.config import settings

_pool: PooledDB | None = None


def _get_pool() -> PooledDB:
    global _pool
    if _pool is None:
        _pool = PooledDB(
            creator=pymysql,
            maxconnections=20,
            mincached=2,
            maxcached=10,
            blocking=True,
            ping=1,
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
    return _pool


def get_connection() -> Connection:
    return _get_pool().connection()


@contextmanager
def db_session() -> Generator[Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
