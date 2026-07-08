"""Refresh Token 持久化（服务端轮换）。"""

from datetime import datetime

import pymysql


class RefreshTokenRepository:
    @staticmethod
    def _table_exists(conn: pymysql.connections.Connection) -> bool:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_name = 'sys_refresh_token'
                LIMIT 1
                """,
            )
            return cur.fetchone() is not None

    def store(
        self,
        conn: pymysql.connections.Connection,
        username: str,
        token_hash: str,
        expires_at: datetime,
    ) -> bool:
        if not self._table_exists(conn):
            return False
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sys_refresh_token (username, token_hash, expires_at)
                VALUES (%s, %s, %s)
                """,
                (username, token_hash, expires_at.replace(tzinfo=None)),
            )
        conn.commit()
        return True

    def find_valid(self, conn: pymysql.connections.Connection, token_hash: str) -> dict | None:
        if not self._table_exists(conn):
            return None
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT username, token_hash, expires_at, revoked
                FROM sys_refresh_token
                WHERE token_hash = %s
                LIMIT 1
                """,
                (token_hash,),
            )
            row = cur.fetchone()
        if not row or row.get("revoked"):
            return None
        expires_at = row["expires_at"]
        if isinstance(expires_at, datetime) and expires_at < datetime.utcnow():
            return None
        return row

    def revoke(self, conn: pymysql.connections.Connection, token_hash: str) -> None:
        if not self._table_exists(conn):
            return
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE sys_refresh_token SET revoked = 1 WHERE token_hash = %s",
                (token_hash,),
            )
        conn.commit()

    def rename_username(
        self,
        conn: pymysql.connections.Connection,
        old_username: str,
        new_username: str,
    ) -> None:
        if not self._table_exists(conn):
            return
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE sys_refresh_token
                SET username = %s
                WHERE username = %s AND revoked = 0
                """,
                (new_username, old_username),
            )
        conn.commit()
