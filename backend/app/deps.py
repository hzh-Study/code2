"""依赖注入：数据库会话、用户端鉴权、管理端鉴权。"""
from fastapi import Depends, HTTPException, Request

from app.database import get_db
from app.models.admin import Admin
from app.models.user import User
from app.utils.security import verify_token, _ROLE_USER, _ROLE_ADMIN


def _extract_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return ""


def get_current_user_id(request: Request) -> int:
    """解析用户端 token，返回 user_id。"""
    token = _extract_token(request)
    uid = verify_token(token, _ROLE_USER)
    if uid is None:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    return uid


def get_current_admin_id(request: Request) -> int:
    """解析管理端 token，返回 admin_id。"""
    token = _extract_token(request)
    aid = verify_token(token, _ROLE_ADMIN)
    if aid is None:
        raise HTTPException(status_code=401, detail="管理员未登录或登录已过期")
    return aid
