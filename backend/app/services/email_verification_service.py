"""邮件令牌：生成、校验、完成设密。"""

from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import pymysql

from app.core.config import settings
from app.core.security import hash_password
from app.models.email_verification import PURPOSE_VERIFY_EMAIL
from app.repositories.auth_repository import AuthRepository
from app.repositories.email_token_repository import EmailTokenRepository
from app.services.email_sender import send_set_password_email_sync

logger = logging.getLogger(__name__)


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_set_password_url(raw_token: str) -> str:
    base = settings.APP_PUBLIC_URL.rstrip("/")
    return f"{base}/set-password?{urlencode({'token': raw_token})}"


def _mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    if len(local) <= 2:
        masked = local[0] + "*"
    else:
        masked = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked}@{domain}"


class EmailVerificationService:
    def __init__(self) -> None:
        self.tokens = EmailTokenRepository()
        self.users = AuthRepository()

    def issue_email_token(
        self,
        conn: pymysql.connections.Connection,
        user_id: int,
        email: str,
        purpose: str,
    ) -> tuple[str, str, bool]:
        raw = secrets.token_urlsafe(32)
        token_hash = _hash_token(raw)
        expires = datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_VERIFY_EXPIRE_HOURS)

        self.tokens.delete_by_user_purpose(conn, user_id, purpose)
        self.tokens.insert(conn, user_id, token_hash, purpose, expires.replace(tzinfo=None))

        action_url = build_set_password_url(raw)
        sent = send_set_password_email_sync(email, action_url, purpose)

        if not sent:
            logger.warning(
                "[email-token] 邮件未发送 purpose=%s user_id=%s email=%s",
                purpose,
                user_id,
                email,
            )

        return raw, action_url, sent

    def _lookup(
        self,
        conn: pymysql.connections.Connection,
        raw_token: str,
    ) -> tuple[dict, dict]:
        token_hash = _hash_token(raw_token.strip())
        found = self.tokens.find_valid_with_user(conn, token_hash)
        if not found:
            raise ValueError("invalid")

        token_row, user_row = found
        exp = token_row["expires_at"]
        if isinstance(exp, datetime):
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                self.tokens.delete_by_id(conn, token_row["id"])
                raise ValueError("expired")

        return token_row, user_row

    def inspect_token(self, conn: pymysql.connections.Connection, raw_token: str) -> dict:
        token_row, user_row = self._lookup(conn, raw_token)
        return {
            "valid": True,
            "purpose": token_row["purpose"],
            "email_masked": _mask_email(str(user_row["email"])),
        }

    def complete_token(
        self,
        conn: pymysql.connections.Connection,
        raw_token: str,
        password: str,
    ) -> str:
        token_row, user_row = self._lookup(conn, raw_token)
        self.users.update_password_hash(conn, user_row["id"], hash_password(password))
        if token_row["purpose"] == PURPOSE_VERIFY_EMAIL:
            self.users.mark_email_verified(conn, user_row["id"])
        self.tokens.delete_by_id(conn, token_row["id"])
        return str(user_row["email"])
