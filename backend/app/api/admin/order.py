"""管理后台：订单管理。"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_admin_id
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.user import User
from app.schemas.common import R
from app.services.order_state import (
    DINING_LABELS,
    STATUS_LABELS,
    can_complete,
    mark_done,
)

router = APIRouter()


def _serialize(order: Order, user: User | None, items: list[OrderItem]) -> dict:
    item_list = [{
        "dish_name": it.dish_name,
        "price": float(it.price),
        "quantity": it.quantity,
        "subtotal": float(it.subtotal),
    } for it in items]
    dish_names = "、".join(f"{it['dish_name']}x{it['quantity']}" for it in item_list)
    return {
        "id": order.id,
        "order_no": order.order_no,
        "user_id": order.user_id,
        "username": user.nickname if user and user.nickname else "微信用户",
        "total_amount": float(order.total_amount),
        "dining_mode": order.dining_mode,
        "dining_mode_label": DINING_LABELS.get(order.dining_mode, ""),
        "status": order.status,
        "status_label": STATUS_LABELS.get(order.status, ""),
        "pay_status": order.pay_status,
        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else None,
        "paid_at": order.paid_at.strftime("%Y-%m-%d %H:%M:%S") if order.paid_at else None,
        "detail": dish_names,
        "items": item_list,
    }


@router.get("/orders")
def list_orders(
    status: int = Query(None),
    start: str = Query(None),
    end: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: int = Depends(get_current_admin_id),
    db: Session = Depends(get_db),
):
    q = db.query(Order)
    if status is not None:
        q = q.filter(Order.status == status)
    try:
        if start:
            q = q.filter(Order.created_at >= datetime.strptime(start, "%Y-%m-%d"))
        if end:
            # 结束日期包含当天（次日 0 点前）
            q = q.filter(Order.created_at < datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1))
    except ValueError:
        return R.fail(3007, "日期格式错误，应为 YYYY-MM-DD")
    total = q.count()
    rows = q.order_by(Order.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 批量预加载用户和订单项，避免 N+1 查询
    order_ids = [o.id for o in rows]
    user_ids = [o.user_id for o in rows]
    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    user_map = {u.id: u for u in users}
    all_items = db.query(OrderItem).filter(OrderItem.order_id.in_(order_ids)).all() if order_ids else []
    items_map: dict[int, list[OrderItem]] = {}
    for item in all_items:
        items_map.setdefault(item.order_id, []).append(item)

    return R.ok({
        "list": [_serialize(o, user_map.get(o.user_id), items_map.get(o.id, [])) for o in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/orders/{order_id}")
def order_detail(order_id: int, _: int = Depends(get_current_admin_id), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return R.fail(3005, "订单不存在")
    user = db.query(User).filter(User.id == order.user_id).first()
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    return R.ok(_serialize(order, user, items))


@router.post("/orders/{order_id}/status")
def update_status(
    order_id: int,
    _: int = Depends(get_current_admin_id),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return R.fail(3005, "订单不存在")
    if not can_complete(order):
        return R.fail(3006, "仅待出餐订单可标记完成")
    mark_done(db, order)
    return R.ok(msg="已标记完成")
