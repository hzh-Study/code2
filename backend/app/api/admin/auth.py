"""管理后台：管理员登录。"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import ADMIN_TOKEN_EXPIRE_HOURS
from app.database import get_db
from app.models.admin import Admin
from app.schemas.common import R
from app.utils.security import generate_token, verify_password

router = APIRouter()


class AdminLoginRequest(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
def admin_login(body: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == body.username).first()
    if not admin or not verify_password(body.password, admin.password_hash):
        return R.fail(3001, "账号或密码错误")
    token = generate_token(admin.id, ADMIN_TOKEN_EXPIRE_HOURS, role="a")
    return R.ok({"token": token, "username": admin.username, "admin_id": admin.id})
