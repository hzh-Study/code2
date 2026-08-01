"""订单状态机与业务常量。"""
from sqlalchemy.orm import Session

from app.models.order import Order

# 订单状态
STATUS_PENDING = 1    # 待支付
STATUS_COOKING = 2     # 待出餐
STATUS_DONE = 3        # 已完成
STATUS_CANCELLED = 4   # 已取消

# 用餐方式
DINING_HALL = 1        # 堂食
PACKING = 2            # 打包

STATUS_LABELS = {
    STATUS_PENDING: "待支付",
    STATUS_COOKING: "待出餐",
    STATUS_DONE: "已完成",
    STATUS_CANCELLED: "已取消",
}

DINING_LABELS = {
    DINING_HALL: "堂食",
    PACKING: "打包",
}


def can_pay_success(order: Order) -> bool:
    return order.status == STATUS_PENDING


def can_cancel(order: Order) -> bool:
    return order.status == STATUS_PENDING


def can_complete(order: Order) -> bool:
    return order.status == STATUS_COOKING


def mark_paid(db: Session, order: Order) -> Order:
    """支付成功：待支付 -> 待出餐，更新支付状态与时间。非待支付订单（已支付/已完成/已取消）忽略，保证幂等且不会重新激活已取消订单。"""
    if order.status != STATUS_PENDING:
        return order
    from app.utils.time import now
    order.status = STATUS_COOKING
    order.pay_status = 1
    order.paid_at = now()
    db.commit()
    db.refresh(order)
    return order


def mark_cancelled(db: Session, order: Order) -> Order:
    if order.status != STATUS_PENDING:
        return order
    order.status = STATUS_CANCELLED
    db.commit()
    db.refresh(order)
    return order


def mark_done(db: Session, order: Order) -> Order:
    if order.status != STATUS_COOKING:
        return order
    order.status = STATUS_DONE
    db.commit()
    db.refresh(order)
    return order
