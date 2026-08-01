"""购物车表模型。"""
from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, BigIntCol, BigIntPK


class Cart(Base):
    __tablename__ = "cart"
    __table_args__ = (UniqueConstraint("user_id", "dish_id", name="uk_user_dish"),)

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigIntCol, ForeignKey("users.id"), nullable=False, index=True)
    dish_id: Mapped[int] = mapped_column(BigIntCol, ForeignKey("dishes.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object] = mapped_column(DateTime, nullable=True, onupdate=func.now())
