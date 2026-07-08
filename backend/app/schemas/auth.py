"""认证相关请求/响应模型。"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class EmailTokenRequest(BaseModel):
    token: str = Field(..., min_length=16)


class CompleteTokenRequest(BaseModel):
    token: str = Field(..., min_length=16)
    password: str = Field(..., min_length=6, max_length=72)


class MessageResponse(BaseModel):
    message: str
    email_sent: bool = False


class RegisterResponse(MessageResponse):
    email: str


class InspectTokenResponse(BaseModel):
    valid: bool = True
    purpose: str
    email_masked: str


class CompleteTokenResponse(BaseModel):
    message: str
    email: str


class UserInfo(BaseModel):
    username: str
    email: str | None = None
    role: str
    display_name: str


class ProfileChangePasswordRequest(BaseModel):
    code: str = Field(..., min_length=4, max_length=8)
    new_password: str = Field(..., min_length=6, max_length=72)


class ProfileUpdateUsernameRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)


class ProfileCodeResponse(BaseModel):
    message: str
    email_sent: bool = False


class ProfileUpdateResponse(BaseModel):
    user: UserInfo
    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access Token 有效期（秒）")


class LoginResponse(TokenPairResponse):
    user: UserInfo


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=16, max_length=512)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., min_length=16, max_length=512)


class TokenPayload(BaseModel):
    sub: str
    role: str
    typ: str = "access"
