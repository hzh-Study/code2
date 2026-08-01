"""用户相关 schema。"""
from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    code: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class UserInfo(BaseModel):
    id: int
    openid: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class LoginResponse(BaseModel):
    token: str
    user: UserInfo
