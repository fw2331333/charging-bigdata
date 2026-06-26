"""FastAPI 依赖注入。"""

from collections.abc import Generator

import pymysql

from app.core.database import db_session


def get_db() -> Generator[pymysql.connections.Connection, None, None]:
    with db_session() as conn:
        yield conn
