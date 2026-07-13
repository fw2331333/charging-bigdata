"""认证业务：邮箱登录 + 注册验证 + 双 Token 轮换。"""



import secrets



import pymysql



from app.core.auth_errors import AuthServiceError

from app.core.config import settings

from app.core.security import (

    access_token_expires_in,

    create_access_token,

    generate_refresh_token,

    hash_password,

    hash_refresh_token,

    verify_password,

)

from app.models.email_verification import PURPOSE_RESET_PASSWORD, PURPOSE_VERIFY_EMAIL

from app.repositories.auth_repository import AuthRepository

from app.repositories.refresh_token_repository import RefreshTokenRepository

from app.schemas.auth import (

    CompleteTokenResponse,

    ForgotPasswordRequest,

    InspectTokenResponse,

    LoginRequest,

    LoginResponse,

    MessageResponse,

    RegisterRequest,

    RegisterResponse,

    ResendVerificationRequest,

    TokenPairResponse,

    UserInfo,

)

from app.services.email_verification_service import EmailVerificationService



_BUILTIN_EMAILS: dict[str, dict[str, str]] = {

    "admin@example.com": {

        "username": "admin",

        "password": "admin123",

        "role": "admin",

    },

    "user@example.com": {

        "username": "user",

        "password": "user123",

        "role": "user",

    },

}





class AuthService:

    def __init__(self) -> None:

        self.repo = AuthRepository()

        self.refresh_repo = RefreshTokenRepository()

        self.email_svc = EmailVerificationService()



    def _user_info(self, username: str, role: str, email: str | None = None) -> UserInfo:

        return UserInfo(

            username=username,

            email=email,

            role=role,

            display_name=self.repo.display_name(username, role),

        )



    def _issue_token_pair(

        self,

        conn: pymysql.connections.Connection,

        user: UserInfo,

    ) -> TokenPairResponse:

        access_token = create_access_token(user.username, user.role)

        refresh_token = generate_refresh_token()

        from datetime import datetime, timedelta, timezone



        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)

        self.refresh_repo.store(conn, user.username, hash_refresh_token(refresh_token), expires_at)

        return TokenPairResponse(

            access_token=access_token,

            refresh_token=refresh_token,

            expires_in=access_token_expires_in(),

        )



    def _placeholder_password_hash(self) -> str:

        return hash_password(secrets.token_urlsafe(32))



    def _send_token_message(self, sent: bool, ok_msg: str, fail_msg: str) -> tuple[str, bool]:

        if sent:

            return ok_msg, True

        return fail_msg, False



    def register(self, conn: pymysql.connections.Connection, req: RegisterRequest) -> RegisterResponse:
        email = str(req.email).strip().lower()
        username = req.username.strip()

        if email in _BUILTIN_EMAILS:
            raise AuthServiceError(400, "该邮箱为系统演示账号，请直接登录或注册其他邮箱")

        existing = self.repo.find_by_email(conn, email)

        if existing:

            if existing.get("email_verified", 1):

                raise AuthServiceError(400, "该邮箱已注册，请直接登录或使用忘记密码")

            raise AuthServiceError(400, "该邮箱已注册但未完成验证，请使用「忘记密码」重发设置密码邮件")



        if self.repo.find_by_username(conn, username):

            raise AuthServiceError(400, "该用户名已被占用，请换一个昵称")



        user_id = self.repo.create_user(

            conn,

            username=username,

            email=email,

            password_hash=self._placeholder_password_hash(),

            role="user",

            email_verified=False,

        )

        conn.commit()



        _, _, sent = self.email_svc.issue_email_token(

            conn, user_id, email, PURPOSE_VERIFY_EMAIL

        )

        conn.commit()

        message, email_sent = self._send_token_message(

            sent,

            "验证邮件已发送，请打开链接设置密码并完成注册",

            "邮件发送失败，请检查 SMTP 配置后重试",

        )

        return RegisterResponse(message=message, email=email, email_sent=email_sent)



    def resend_verification(

        self,

        conn: pymysql.connections.Connection,

        req: ResendVerificationRequest,

    ) -> MessageResponse:

        email = str(req.email).strip().lower()

        user = self.repo.find_by_email(conn, email)

        if not user or user.get("email_verified", 1):

            return MessageResponse(message="若该邮箱已注册且未验证，你将收到设置密码邮件", email_sent=False)



        _, _, sent = self.email_svc.issue_email_token(

            conn, user["id"], email, PURPOSE_VERIFY_EMAIL

        )

        conn.commit()

        message = "设置密码邮件已发送，请查收（含垃圾箱）" if sent else "邮件发送失败，请检查 SMTP 配置"

        return MessageResponse(message=message, email_sent=sent)



    def forgot_password(

        self,

        conn: pymysql.connections.Connection,

        req: ForgotPasswordRequest,

    ) -> MessageResponse:

        email = str(req.email).strip().lower()

        user = self.repo.find_by_email(conn, email)

        if not user:

            return MessageResponse(message="若该邮箱已注册，你将收到相关邮件", email_sent=False)



        purpose = PURPOSE_VERIFY_EMAIL if not user.get("email_verified", 1) else PURPOSE_RESET_PASSWORD

        _, _, sent = self.email_svc.issue_email_token(conn, user["id"], email, purpose)

        conn.commit()



        if purpose == PURPOSE_VERIFY_EMAIL:

            message = (

                "该邮箱尚未完成验证，已发送「设置密码」邮件，请打开链接完成验证后再登录"

                if sent

                else "邮件发送失败，请检查 SMTP 配置"

            )

        else:

            message = "重置密码邮件已发送，请查收（含垃圾箱）" if sent else "邮件发送失败，请检查 SMTP 配置"

        return MessageResponse(message=message, email_sent=sent)



    def inspect_email_token(

        self,

        conn: pymysql.connections.Connection,

        token: str,

    ) -> InspectTokenResponse:

        try:

            data = self.email_svc.inspect_token(conn, token.strip())

        except ValueError as exc:

            code = str(exc)

            if code == "expired":

                raise AuthServiceError(400, "链接已过期，请重新注册或申请重置密码") from exc

            raise AuthServiceError(400, "链接无效") from exc

        return InspectTokenResponse(**data)



    def complete_email_token(

        self,

        conn: pymysql.connections.Connection,

        token: str,

        password: str,

    ) -> CompleteTokenResponse:

        try:

            email = self.email_svc.complete_token(conn, token.strip(), password)

            conn.commit()

        except ValueError as exc:

            code = str(exc)

            if code == "expired":

                raise AuthServiceError(400, "链接已过期，请重新注册或申请重置密码") from exc

            raise AuthServiceError(400, "链接无效") from exc

        return CompleteTokenResponse(message="密码已设置，请使用邮箱和新密码登录", email=email)



    def _login_builtin(self, conn: pymysql.connections.Connection, req: LoginRequest) -> LoginResponse | None:

        email = str(req.email).strip().lower()

        entry = _BUILTIN_EMAILS.get(email)

        if not entry or entry["password"] != req.password:

            return None

        user = self._user_info(entry["username"], entry["role"], email)

        pair = self._issue_token_pair(conn, user)

        return LoginResponse(user=user, **pair.model_dump())



    def login(self, conn: pymysql.connections.Connection, req: LoginRequest) -> LoginResponse:
        email = str(req.email).strip().lower()

        # 演示账号优先走内置凭据，避免 DB 中同邮箱未验证/错误哈希导致无法登录
        builtin = self._login_builtin(conn, req)
        if builtin:
            return builtin

        row = self.repo.find_by_email(conn, email)
        if row:
            if not row.get("is_active", 1):
                raise AuthServiceError(401, "邮箱或密码错误")
            if not verify_password(req.password, row["password_hash"]):
                raise AuthServiceError(401, "邮箱或密码错误")
            if not row.get("email_verified", 1):
                raise AuthServiceError(
                    403,
                    "邮箱尚未验证，请查收邮件完成设置密码，或使用忘记密码重发",
                )
            user = self.repo.to_user_info(row)
            pair = self._issue_token_pair(conn, user)
            return LoginResponse(user=user, **pair.model_dump())

        raise AuthServiceError(401, "邮箱或密码错误")



    def refresh(self, conn: pymysql.connections.Connection, refresh_token: str) -> TokenPairResponse | None:

        token_hash = hash_refresh_token(refresh_token)

        row = self.refresh_repo.find_valid(conn, token_hash)

        if not row:

            return None

        user = self.get_user(conn, row["username"])

        if not user:

            self.refresh_repo.revoke(conn, token_hash)

            return None

        self.refresh_repo.revoke(conn, token_hash)

        return self._issue_token_pair(conn, user)



    def logout(self, conn: pymysql.connections.Connection, refresh_token: str) -> None:

        self.refresh_repo.revoke(conn, hash_refresh_token(refresh_token))



    def get_user(self, conn: pymysql.connections.Connection, username: str) -> UserInfo | None:

        row = self.repo.find_by_username(conn, username)

        if row and row.get("is_active", 1):

            return self.repo.to_user_info(row)

        for email, entry in _BUILTIN_EMAILS.items():

            if entry["username"] == username:

                return self._user_info(username, entry["role"], email)

        return None


