"""MySQL 连接：供 Repository 层查询 MapReduce 入库结果。"""

from collections.abc import Generator
from contextlib import contextmanager

import pymysql
from pymysql.connections import Connection

from app.core.config import settings


def get_connection() -> Connection:
    return pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


@contextmanager
def db_session() -> Generator[Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
