"""用户相关 schema。"""
from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints

LoginCode = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=256)]


class LoginRequest(BaseModel):
    code: LoginCode
    nickname: Optional[str] = Field(default=None, max_length=64)
    avatar: Optional[str] = Field(default=None, max_length=255)


class UserInfo(BaseModel):
    id: int
    openid: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class LoginResponse(BaseModel):
    token: str
    user: UserInfo
