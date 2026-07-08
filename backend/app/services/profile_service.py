"""个人资料：昵称修改、邮箱验证码改密。"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import pymysql

from app.core.auth_errors import AuthServiceError
from app.core.config import settings
from app.core.security import hash_password
from app.models.profile_otp import PURPOSE_CHANGE_PASSWORD
from app.repositories.auth_repository import AuthRepository
from app.repositories.profile_otp_repository import ProfileOtpRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.schemas.auth import (
    ProfileChangePasswordRequest,
    ProfileCodeResponse,
    ProfileUpdateResponse,
    ProfileUpdateUsernameRequest,
    UserInfo,
)
from app.services.auth_service import AuthService
from app.services.email_sender import send_profile_otp_email_sync


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.strip().encode("utf-8")).hexdigest()


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


class ProfileService:
    def __init__(self) -> None:
        self.repo = AuthRepository()
        self.otp_repo = ProfileOtpRepository()
        self.refresh_repo = RefreshTokenRepository()
        self.auth = AuthService()

    def _db_user_or_error(self, conn: pymysql.connections.Connection, username: str) -> dict:
        row = self.repo.find_by_username(conn, username)
        if not row:
            raise AuthServiceError(400, "演示账号不支持在线修改个人资料，请使用数据库注册用户")
        if not row.get("email"):
            raise AuthServiceError(400, "当前账号未绑定邮箱，无法发送验证码")
        return row

    def send_password_code(
        self,
        conn: pymysql.connections.Connection,
        current: UserInfo,
    ) -> ProfileCodeResponse:
        row = self._db_user_or_error(conn, current.username)
        email = str(row["email"])
        code = _generate_code()
        expires = datetime.now(timezone.utc) + timedelta(minutes=settings.PROFILE_OTP_EXPIRE_MINUTES)

        self.otp_repo.invalidate_user_purpose(conn, row["id"], PURPOSE_CHANGE_PASSWORD)
        self.otp_repo.insert(conn, row["id"], _hash_code(code), PURPOSE_CHANGE_PASSWORD, expires)
        conn.commit()

        sent = send_profile_otp_email_sync(email, code)

        if sent:
            message = f"验证码已发送至 {email}（含垃圾箱），{settings.PROFILE_OTP_EXPIRE_MINUTES} 分钟内有效"
        else:
            message = "邮件发送失败，请检查 SMTP 配置"

        return ProfileCodeResponse(message=message, email_sent=sent)

    def _verify_code(self, conn: pymysql.connections.Connection, user_id: int, code: str) -> None:
        otp_row = self.otp_repo.find_valid(conn, user_id, _hash_code(code), PURPOSE_CHANGE_PASSWORD)
        if not otp_row:
            raise AuthServiceError(400, "验证码错误或已过期")
        self.otp_repo.mark_used(conn, otp_row["id"])

    def _reissue_session(
        self,
        conn: pymysql.connections.Connection,
        user: UserInfo,
        *,
        rename_from: str | None = None,
    ) -> ProfileUpdateResponse:
        if rename_from and rename_from != user.username:
            self.refresh_repo.rename_username(conn, rename_from, user.username)
        pair = self.auth._issue_token_pair(conn, user)
        conn.commit()
        return ProfileUpdateResponse(
            user=user,
            access_token=pair.access_token,
            refresh_token=pair.refresh_token,
            expires_in=pair.expires_in,
        )

    def change_password(
        self,
        conn: pymysql.connections.Connection,
        current: UserInfo,
        req: ProfileChangePasswordRequest,
    ) -> ProfileUpdateResponse:
        row = self._db_user_or_error(conn, current.username)
        self._verify_code(conn, row["id"], req.code.strip())
        self.repo.update_password_hash(conn, row["id"], hash_password(req.new_password))
        user = self.repo.to_user_info(row)
        return self._reissue_session(conn, user)

    def update_username(
        self,
        conn: pymysql.connections.Connection,
        current: UserInfo,
        req: ProfileUpdateUsernameRequest,
    ) -> ProfileUpdateResponse:
        row = self._db_user_or_error(conn, current.username)
        if row["role"] == "admin":
            raise AuthServiceError(400, "管理员账号名称固定为 admin，不可修改")
        new_name = req.username.strip()
        if new_name.lower() == "admin":
            raise AuthServiceError(400, "该昵称不可使用")
        if new_name == row["username"]:
            raise AuthServiceError(400, "新昵称与当前相同")
        if self.repo.find_by_username(conn, new_name):
            raise AuthServiceError(400, "该昵称已被占用")
        old_name = row["username"]
        self.repo.update_username(conn, row["id"], new_name)
        updated = self.repo.find_by_id(conn, row["id"])
        if not updated:
            raise AuthServiceError(500, "更新失败")
        user = self.repo.to_user_info(updated)
        return self._reissue_session(conn, user, rename_from=old_name)
