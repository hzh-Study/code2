"""用户表模型。"""
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, BigIntPK


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    openid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object] = mapped_column(DateTime, nullable=True, onupdate=func.now())
