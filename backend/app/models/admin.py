"""管理员表模型（后台登录必需，PRD 未单列但最小实现补充）。"""
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, BigIntPK


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
