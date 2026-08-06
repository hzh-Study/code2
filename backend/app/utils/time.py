"""时间相关工具。数据库业务时间使用 UTC，展示时转换为门店时区。

应用层写入的 paid_at / expire_at / orders.created_at 统一使用 utc_now()。
"""
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.config import APP_TIMEZONE, ORDER_EXPIRE_MINUTES

try:
    LOCAL_TIMEZONE = ZoneInfo(APP_TIMEZONE)
except ZoneInfoNotFoundError as exc:
    # Windows 的 Python 发行版可能未附带 IANA tzdata；上海时区自 1991 年起无夏令时。
    if APP_TIMEZONE == "Asia/Shanghai":
        LOCAL_TIMEZONE = timezone(timedelta(hours=8), name=APP_TIMEZONE)
    else:
        raise RuntimeError(f"Unknown APP_TIMEZONE: {APP_TIMEZONE}") from exc


def now() -> datetime:
    """门店本地墙钟时间（无时区信息），用于展示层「今天」等业务语义。"""
    return datetime.now(LOCAL_TIMEZONE).replace(tzinfo=None)


def utc_now() -> datetime:
    """UTC 墙钟时间（无时区信息），用于写入数据库的业务时间戳。"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def expire_at(minutes: int = ORDER_EXPIRE_MINUTES) -> datetime:
    """订单支付超时时间（UTC）。"""
    return utc_now() + timedelta(minutes=minutes)


def is_expired(dt) -> bool:
    if dt is None:
        return False
    return dt < utc_now()


def format_utc(value: datetime | None) -> str | None:
    """把数据库中的无时区 UTC 时间转换成门店本地时间。"""
    if value is None:
        return None
    utc_value = value.replace(tzinfo=timezone.utc)
    return utc_value.astimezone(LOCAL_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")


def local_date_to_utc(value: date) -> datetime:
    local_value = datetime.combine(value, time.min, tzinfo=LOCAL_TIMEZONE)
    return local_value.astimezone(timezone.utc).replace(tzinfo=None)


def today_utc_range() -> tuple[datetime, datetime]:
    local_today = datetime.now(LOCAL_TIMEZONE).date()
    start = local_date_to_utc(local_today)
    return start, local_date_to_utc(local_today + timedelta(days=1))
