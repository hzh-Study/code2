"""订单表模型。"""
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, BigIntCol, BigIntPK, Money


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigIntCol, ForeignKey("users.id"), nullable=False, index=True)
    total_amount: Mapped[object] = mapped_column(Money, nullable=False)
    dining_mode: Mapped[int] = mapped_column(Integer, nullable=False, comment="1=堂食,2=打包")
    status: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, comment="1=待支付,2=待出餐,3=已完成,4=已取消"
    )
    pay_status: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="0=未付,1=已付")
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expire_at: Mapped[object] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    paid_at: Mapped[object] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[object] = mapped_column(DateTime, nullable=True, onupdate=func.now())
