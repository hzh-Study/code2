"""SSE 事件总线：订单变更时立即推送给所有已连接的管理端。"""
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

# 已连接的客户端队列集合
_subscribers: list[asyncio.Queue] = []


def _broadcast(event_type: str, data: dict) -> None:
    """向所有已连接的 SSE 客户端广播事件。"""
    payload = json.dumps({"type": event_type, "data": data}, ensure_ascii=False)
    dead = []
    for q in _subscribers:
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            dead.append(q)
    for q in dead:
        try:
            _subscribers.remove(q)
        except ValueError:
            pass


def emit_order_created(order_id: int, order_no: str, status: int) -> None:
    _broadcast("order.created", {"id": order_id, "order_no": order_no, "status": status})


def emit_order_updated(order_id: int, status: int) -> None:
    _broadcast("order.updated", {"id": order_id, "status": status})


async def subscribe() -> asyncio.Queue[str]:
    """注册一个新的 SSE 订阅者，返回用于接收消息的队列。"""
    q: asyncio.Queue[str] = asyncio.Queue(maxsize=32)
    _subscribers.append(q)
    logger.info("SSE subscriber connected (total=%d)", len(_subscribers))
    return q


def unsubscribe(q: asyncio.Queue[str]) -> None:
    """移除一个订阅者。"""
    try:
        _subscribers.remove(q)
        logger.info("SSE subscriber disconnected (total=%d)", len(_subscribers))
    except ValueError:
        pass
