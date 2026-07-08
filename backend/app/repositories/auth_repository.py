"""用户数据访问。"""

import pymysql

from app.schemas.auth import UserInfo


class AuthRepository:
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

    def find_by_username(self, conn: pymysql.connections.Connection, username: str) -> dict | None:
        if not self._table_exists(conn, "sys_user"):
            return None
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, email, password_hash, role, is_active, email_verified
                FROM sys_user
                WHERE username = %s
                LIMIT 1
                """,
                (username,),
            )
            return cur.fetchone()

    def find_by_email(self, conn: pymysql.connections.Connection, email: str) -> dict | None:
        if not self._table_exists(conn, "sys_user"):
            return None
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, email, password_hash, role, is_active, email_verified
                FROM sys_user
                WHERE email = %s
                LIMIT 1
                """,
                (email,),
            )
            return cur.fetchone()

    def create_user(
        self,
        conn: pymysql.connections.Connection,
        *,
        username: str,
        email: str,
        password_hash: str,
        role: str = "user",
        email_verified: bool = False,
    ) -> int:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sys_user (username, email, password_hash, role, is_active, email_verified)
                VALUES (%s, %s, %s, %s, 1, %s)
                """,
                (username, email, password_hash, role, 1 if email_verified else 0),
            )
            return int(cur.lastrowid)

    def update_password_hash(
        self,
        conn: pymysql.connections.Connection,
        user_id: int,
        password_hash: str,
    ) -> None:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE sys_user
                SET password_hash = %s, updated_at = NOW()
                WHERE id = %s
                """,
                (password_hash, user_id),
            )

    def mark_email_verified(self, conn: pymysql.connections.Connection, user_id: int) -> None:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE sys_user
                SET email_verified = 1, updated_at = NOW()
                WHERE id = %s
                """,
                (user_id,),
            )

    def update_username(
        self,
        conn: pymysql.connections.Connection,
        user_id: int,
        username: str,
    ) -> None:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE sys_user
                SET username = %s, updated_at = NOW()
                WHERE id = %s
                """,
                (username, user_id),
            )

    def find_by_id(self, conn: pymysql.connections.Connection, user_id: int) -> dict | None:
        if not self._table_exists(conn, "sys_user"):
            return None
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, email, password_hash, role, is_active, email_verified
                FROM sys_user WHERE id = %s LIMIT 1
                """,
                (user_id,),
            )
            return cur.fetchone()

    @staticmethod
    def display_name(username: str, role: str) -> str:
        return username

    def to_user_info(self, row: dict) -> UserInfo:
        return UserInfo(
            username=row["username"],
            email=row.get("email"),
            role=row["role"],
            display_name=self.display_name(row["username"], row["role"]),
        )
