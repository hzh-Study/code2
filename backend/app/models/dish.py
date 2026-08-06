"""菜品表模型。"""
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, BigIntCol, BigIntPK, Money


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    price: Mapped[object] = mapped_column(Money, nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category_id: Mapped[int] = mapped_column(
        BigIntCol, ForeignKey("categories.id"), nullable=False, index=True
    )
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="1=在售,0=下架")
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object] = mapped_column(DateTime, nullable=True, onupdate=func.now())
