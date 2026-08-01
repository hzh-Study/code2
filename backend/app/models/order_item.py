"""订单详情表模型（菜品快照）。"""
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, BigIntCol, BigIntPK, Money


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigIntCol, ForeignKey("orders.id"), nullable=False, index=True)
    dish_id: Mapped[int] = mapped_column(BigIntCol, nullable=False)
    dish_name: Mapped[str] = mapped_column(String(128), nullable=False)
    price: Mapped[object] = mapped_column(Money, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal: Mapped[object] = mapped_column(Money, nullable=False)
