"""小程序端：登录授权。"""
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.config import TOKEN_EXPIRE_HOURS
from app.database import get_db
from app.deps import get_current_user_id
from app.schemas.common import R
from app.schemas.user import LoginRequest
from app.services.wechat import code2session
from app.utils.security import generate_token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/auth/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """微信 code 换 openid，自动注册/登录，返回 token + 用户信息。"""
    from app.models.user import User

    try:
        openid = code2session(body.code)
    except Exception:
        logger.exception("微信登录 code2session 失败")
        return R.fail(1001, "微信登录失败，请稍后重试")

    user = db.query(User).filter(User.openid == openid).first()
    if user is None:
        try:
            user = User(openid=openid)
            db.add(user)
            db.commit()
            db.refresh(user)
        except IntegrityError:
            db.rollback()
            user = db.query(User).filter(User.openid == openid).first()
            if user is None:
                logger.error("用户并发注册后未找到记录")
                return R.fail(1003, "登录失败，请重试")

    # 昵称/头像（新版头像昵称组件）一并提交时更新
    # 仅在用户未设置昵称时才使用传入的默认值，避免覆盖用户自定义昵称
    need_commit = False
    if body.nickname and not user.nickname:
        user.nickname = body.nickname
        need_commit = True
    if body.avatar and not user.avatar:
        user.avatar = body.avatar
        need_commit = True
    if need_commit:
        db.commit()
        db.refresh(user)

    token = generate_token(user.id, TOKEN_EXPIRE_HOURS, role="u")
    return R.ok({"token": token, "user": _to_dict(user)})


@router.get("/auth/me")
def me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    from app.models.user import User

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return R.fail(1002, "用户不存在")
    return R.ok(_to_dict(user))


def _to_dict(user) -> dict:
    return {
        "id": user.id,
        "openid": user.openid,
        "nickname": user.nickname,
        "avatar": user.avatar,
    }
