"""时间相关工具。"""
from datetime import datetime, timedelta

from app.config import ORDER_EXPIRE_MINUTES


def now() -> datetime:
    return datetime.now()


def expire_at(minutes: int = ORDER_EXPIRE_MINUTES) -> datetime:
    """订单支付超时时间。"""
    return datetime.now() + timedelta(minutes=minutes)


def is_expired(dt) -> bool:
    if dt is None:
        return False
    return dt < datetime.now()
