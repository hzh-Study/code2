"""管理后台：管理员登录。"""
import time
from collections import deque
from threading import Lock

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import ADMIN_TOKEN_EXPIRE_HOURS
from app.database import get_db
from app.models.admin import Admin
from app.schemas.common import R
from app.utils.security import generate_token, verify_password

router = APIRouter()

# 单进程部署的轻量限流；状态有界且仅记录失败尝试。
_login_failures: dict[str, deque[float]] = {}
_login_failures_lock = Lock()
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 5  # failed attempts per window
RATE_LIMIT_MAX_CLIENTS = 10_000


def _prune_failures(failures: deque[float], current: float) -> None:
    while failures and current - failures[0] >= RATE_LIMIT_WINDOW:
        failures.popleft()


def _check_rate_limit(ip: str) -> None:
    current = time.monotonic()
    with _login_failures_lock:
        failures = _login_failures.get(ip)
        if failures is None:
            return
        _prune_failures(failures, current)
        if not failures:
            _login_failures.pop(ip, None)
            return
        if len(failures) >= RATE_LIMIT_MAX:
            raise HTTPException(status_code=429, detail="登录尝试过于频繁，请稍后再试")


def _record_login_failure(ip: str) -> None:
    current = time.monotonic()
    with _login_failures_lock:
        if ip not in _login_failures and len(_login_failures) >= RATE_LIMIT_MAX_CLIENTS:
            for client_ip, failures in list(_login_failures.items()):
                _prune_failures(failures, current)
                if not failures:
                    _login_failures.pop(client_ip, None)
            if len(_login_failures) >= RATE_LIMIT_MAX_CLIENTS:
                _login_failures.pop(next(iter(_login_failures)))
        failures = _login_failures.setdefault(ip, deque())
        _prune_failures(failures, current)
        failures.append(current)


def _clear_login_failures(ip: str) -> None:
    with _login_failures_lock:
        _login_failures.pop(ip, None)


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


@router.post("/auth/login")
def admin_login(body: AdminLoginRequest, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)
    admin = db.query(Admin).filter(Admin.username == body.username).first()
    if not admin or not verify_password(body.password, admin.password_hash):
        _record_login_failure(client_ip)
        return R.fail(3001, "账号或密码错误")
    _clear_login_failures(client_ip)
    token = generate_token(admin.id, ADMIN_TOKEN_EXPIRE_HOURS, role="a")
    return R.ok({"token": token, "username": admin.username, "admin_id": admin.id})
