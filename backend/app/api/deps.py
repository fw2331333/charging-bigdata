"""FastAPI 依赖注入。"""

from collections.abc import Generator
from typing import Annotated

import pymysql
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.database import db_session
from app.core.security import decode_access_token
from app.schemas.auth import UserInfo
from app.services.auth_service import AuthService

_bearer = HTTPBearer(auto_error=False)
_auth_service = AuthService()


def get_db() -> Generator[pymysql.connections.Connection, None, None]:
    with db_session() as conn:
        yield conn


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    conn: Annotated[pymysql.connections.Connection, Depends(get_db)],
) -> UserInfo:
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或令牌无效")
    try:
        payload = decode_access_token(creds.credentials)
        username = str(payload.get("sub", ""))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌已过期或无效") from exc
    user = _auth_service.get_user(conn, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user


def require_admin(user: Annotated[UserInfo, Depends(get_current_user)]) -> UserInfo:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return user
