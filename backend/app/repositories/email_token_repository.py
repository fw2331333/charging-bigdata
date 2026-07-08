"""邮箱验证令牌数据访问。"""

from datetime import datetime

import pymysql


class EmailTokenRepository:
    @staticmethod
    def _table_exists(conn: pymysql.connections.Connection, table: str) -> bool:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_name = %s
                LIMIT 1
                """,
                (table,),
            )
            return cur.fetchone() is not None

    def delete_by_user_purpose(
        self,
        conn: pymysql.connections.Connection,
        user_id: int,
        purpose: str,
    ) -> None:
        if not self._table_exists(conn, "sys_email_verification_token"):
            return
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM sys_email_verification_token
                WHERE user_id = %s AND purpose = %s
                """,
                (user_id, purpose),
            )

    def insert(
        self,
        conn: pymysql.connections.Connection,
        user_id: int,
        token_hash: str,
        purpose: str,
        expires_at: datetime,
    ) -> None:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sys_email_verification_token
                    (user_id, token_hash, purpose, expires_at)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, token_hash, purpose, expires_at),
            )

    def find_valid_with_user(
        self,
        conn: pymysql.connections.Connection,
        token_hash: str,
    ) -> tuple[dict, dict] | None:
        if not self._table_exists(conn, "sys_email_verification_token"):
            return None
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    t.id AS token_id, t.user_id, t.purpose, t.expires_at,
                    u.id, u.username, u.email, u.password_hash, u.role,
                    u.is_active, u.email_verified
                FROM sys_email_verification_token t
                INNER JOIN sys_user u ON u.id = t.user_id
                WHERE t.token_hash = %s
                LIMIT 1
                """,
                (token_hash,),
            )
            row = cur.fetchone()
            if not row:
                return None
            token_row = {
                "id": row["token_id"],
                "user_id": row["user_id"],
                "purpose": row["purpose"],
                "expires_at": row["expires_at"],
            }
            user_row = {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "password_hash": row["password_hash"],
                "role": row["role"],
                "is_active": row["is_active"],
                "email_verified": row.get("email_verified", 1),
            }
            return token_row, user_row

    def delete_by_id(self, conn: pymysql.connections.Connection, token_id: int) -> None:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sys_email_verification_token WHERE id = %s", (token_id,))
