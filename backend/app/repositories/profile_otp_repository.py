"""个人资料验证码数据访问。"""

from datetime import datetime

import pymysql


class ProfileOtpRepository:
    @staticmethod
    def _table_exists(conn: pymysql.connections.Connection) -> bool:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_name = 'sys_profile_otp'
                LIMIT 1
                """,
            )
            return cur.fetchone() is not None

    def invalidate_user_purpose(
        self,
        conn: pymysql.connections.Connection,
        user_id: int,
        purpose: str,
    ) -> None:
        if not self._table_exists(conn):
            return
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE sys_profile_otp SET used = 1
                WHERE user_id = %s AND purpose = %s AND used = 0
                """,
                (user_id, purpose),
            )

    def insert(
        self,
        conn: pymysql.connections.Connection,
        user_id: int,
        code_hash: str,
        purpose: str,
        expires_at: datetime,
    ) -> None:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sys_profile_otp (user_id, code_hash, purpose, expires_at)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, code_hash, purpose, expires_at.replace(tzinfo=None)),
            )

    def find_valid(
        self,
        conn: pymysql.connections.Connection,
        user_id: int,
        code_hash: str,
        purpose: str,
    ) -> dict | None:
        if not self._table_exists(conn):
            return None
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, expires_at, used
                FROM sys_profile_otp
                WHERE user_id = %s AND code_hash = %s AND purpose = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (user_id, code_hash, purpose),
            )
            row = cur.fetchone()
        if not row or row.get("used"):
            return None
        exp = row["expires_at"]
        if isinstance(exp, datetime) and exp < datetime.utcnow():
            return None
        return row

    def mark_used(self, conn: pymysql.connections.Connection, otp_id: int) -> None:
        with conn.cursor() as cur:
            cur.execute("UPDATE sys_profile_otp SET used = 1 WHERE id = %s", (otp_id,))
