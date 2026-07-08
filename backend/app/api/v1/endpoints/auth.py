"""认证接口。"""

import pymysql
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_db
from app.core.auth_errors import AuthServiceError
from app.schemas.auth import (
    CompleteTokenRequest,
    CompleteTokenResponse,
    EmailTokenRequest,
    ForgotPasswordRequest,
    InspectTokenResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    MessageResponse,
    ProfileChangePasswordRequest,
    ProfileCodeResponse,
    ProfileUpdateResponse,
    ProfileUpdateUsernameRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    TokenPairResponse,
    UserInfo,
)
from app.services.auth_service import AuthService
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/auth", tags=["认证"])
service = AuthService()
profile_service = ProfileService()


def _raise_auth_error(exc: AuthServiceError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.post("/register", response_model=RegisterResponse, summary="邮箱注册（邮件设密）")
def register(req: RegisterRequest, db: pymysql.connections.Connection = Depends(get_db)) -> RegisterResponse:
    try:
        return service.register(db, req)
    except AuthServiceError as exc:
        _raise_auth_error(exc)


@router.post("/resend-verification", response_model=MessageResponse, summary="重发验证邮件")
def resend_verification(
    req: ResendVerificationRequest,
    db: pymysql.connections.Connection = Depends(get_db),
) -> MessageResponse:
    return service.resend_verification(db, req)


@router.post("/forgot-password", response_model=MessageResponse, summary="忘记密码 / 重发验证")
def forgot_password(
    req: ForgotPasswordRequest,
    db: pymysql.connections.Connection = Depends(get_db),
) -> MessageResponse:
    return service.forgot_password(db, req)


@router.post("/inspect-email-token", response_model=InspectTokenResponse, summary="校验邮件令牌")
def inspect_email_token(
    req: EmailTokenRequest,
    db: pymysql.connections.Connection = Depends(get_db),
) -> InspectTokenResponse:
    try:
        return service.inspect_email_token(db, req.token)
    except AuthServiceError as exc:
        _raise_auth_error(exc)


@router.post("/complete-email-token", response_model=CompleteTokenResponse, summary="邮件链接设置密码")
def complete_email_token(
    req: CompleteTokenRequest,
    db: pymysql.connections.Connection = Depends(get_db),
) -> CompleteTokenResponse:
    try:
        return service.complete_email_token(db, req.token, req.password)
    except AuthServiceError as exc:
        _raise_auth_error(exc)


@router.post("/login", response_model=LoginResponse, summary="用户登录（双 Token）")
def login(req: LoginRequest, db: pymysql.connections.Connection = Depends(get_db)) -> LoginResponse:
    try:
        return service.login(db, req)
    except AuthServiceError as exc:
        _raise_auth_error(exc)


@router.post("/refresh", response_model=TokenPairResponse, summary="刷新 Access Token（轮换 Refresh Token）")
def refresh_tokens(
    req: RefreshTokenRequest,
    db: pymysql.connections.Connection = Depends(get_db),
) -> TokenPairResponse:
    result = service.refresh(db, req.refresh_token)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh Token 无效或已过期")
    return result


@router.post("/logout", summary="登出（吊销 Refresh Token）")
def logout(req: LogoutRequest, db: pymysql.connections.Connection = Depends(get_db)) -> dict:
    service.logout(db, req.refresh_token)
    return {"ok": True}


@router.get("/me", response_model=UserInfo, summary="当前用户信息")
def me(user: UserInfo = Depends(get_current_user)) -> UserInfo:
    return user


@router.post("/profile/send-code", response_model=ProfileCodeResponse, summary="发送修改密码验证码")
def profile_send_code(
    user: UserInfo = Depends(get_current_user),
    db: pymysql.connections.Connection = Depends(get_db),
) -> ProfileCodeResponse:
    try:
        return profile_service.send_password_code(db, user)
    except AuthServiceError as exc:
        _raise_auth_error(exc)


@router.patch("/profile/password", response_model=ProfileUpdateResponse, summary="验证码修改密码")
def profile_change_password(
    req: ProfileChangePasswordRequest,
    user: UserInfo = Depends(get_current_user),
    db: pymysql.connections.Connection = Depends(get_db),
) -> ProfileUpdateResponse:
    try:
        return profile_service.change_password(db, user, req)
    except AuthServiceError as exc:
        _raise_auth_error(exc)


@router.patch("/profile/username", response_model=ProfileUpdateResponse, summary="修改账号昵称")
def profile_update_username(
    req: ProfileUpdateUsernameRequest,
    user: UserInfo = Depends(get_current_user),
    db: pymysql.connections.Connection = Depends(get_db),
) -> ProfileUpdateResponse:
    try:
        return profile_service.update_username(db, user, req)
    except AuthServiceError as exc:
        _raise_auth_error(exc)
