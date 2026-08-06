"""订单状态机与业务常量。"""
import logging
from sqlalchemy.orm import Session

from app.models.order import Order
from app.utils.time import utc_now

logger = logging.getLogger(__name__)

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


def mark_paid(db: Session, order: Order) -> bool:
    """支付成功：待支付 -> 待出餐，更新支付状态与时间。非待支付订单（已支付/已完成/已取消）忽略，保证幂等且不会重新激活已取消订单。"""
    updated = db.query(Order).filter(
        Order.id == order.id,
        Order.status == STATUS_PENDING,
    ).update(
        {
            Order.status: STATUS_COOKING,
            Order.pay_status: 1,
            Order.paid_at: utc_now(),
        },
        synchronize_session=False,
    )
    db.commit()
    db.refresh(order)
    return updated == 1


def expire_pending_orders(db: Session, user_id: int | None = None) -> int:
    """懒关闭所有已过支付期限的订单，返回更新数量。"""
    query = db.query(Order).filter(
        Order.status == STATUS_PENDING,
        Order.expire_at.is_not(None),
        Order.expire_at < utc_now(),
    )
    if user_id is not None:
        query = query.filter(Order.user_id == user_id)
    from app.services import wechat

    if wechat.DEV_MODE:
        count = query.update({Order.status: STATUS_CANCELLED}, synchronize_session=False)
        if count:
            db.commit()
        return count

    changed = 0
    for order in query.all():
        try:
            close_result = wechat.close_order(order)
        except Exception:
            logger.exception("自动关闭微信订单失败: order_no=%s", order.order_no)
            continue
        if close_result == "paid":
            changed += int(mark_paid(db, order))
        else:
            changed += int(mark_cancelled(db, order))
    return changed


def mark_cancelled(db: Session, order: Order) -> bool:
    updated = db.query(Order).filter(
        Order.id == order.id,
        Order.status == STATUS_PENDING,
    ).update({Order.status: STATUS_CANCELLED}, synchronize_session=False)
    db.commit()
    db.refresh(order)
    return updated == 1


def mark_done(db: Session, order: Order) -> bool:
    updated = db.query(Order).filter(
        Order.id == order.id,
        Order.status == STATUS_COOKING,
    ).update({Order.status: STATUS_DONE}, synchronize_session=False)
    db.commit()
    db.refresh(order)
    return updated == 1
