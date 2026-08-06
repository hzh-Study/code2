"""管理后台：数据看板。"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_admin_id
from app.models.dish import Dish
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.user import User
from app.schemas.common import R
from app.services.order_state import DINING_LABELS, STATUS_LABELS, expire_pending_orders
from app.utils.time import format_utc, today_utc_range

router = APIRouter()


@router.get("/dashboard")
def dashboard(_: int = Depends(get_current_admin_id), db: Session = Depends(get_db)):
    expire_pending_orders(db)
    today_start, tomorrow_start = today_utc_range()

    today_orders = db.query(Order).filter(
        Order.created_at >= today_start,
        Order.created_at < tomorrow_start,
    ).count()
    on_sale_dishes = db.query(Dish).filter(Dish.status == 1).count()

    # 今日销售额：paid_at 存 UTC，与 today_orders 使用同一本地日边界
    today_sales = db.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        Order.paid_at >= today_start,
        Order.paid_at < tomorrow_start,
        Order.pay_status == 1,
        Order.status != 4,
    ).scalar()
    today_sales = round(float(today_sales), 2)

    status_counts = {
        status: count
        for status, count in db.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    }

    # 近期订单（最近 10 条）- 批量预加载用户避免 N+1 查询
    recent = db.query(Order).order_by(Order.id.desc()).limit(10).all()
    user_ids = [o.user_id for o in recent]
    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    user_map = {u.id: u for u in users}
    recent_list = []
    for o in recent:
        user = user_map.get(o.user_id)
        recent_list.append({
            "order_no": o.order_no,
            "username": user.nickname if user and user.nickname else "微信用户",
            "total_amount": float(o.total_amount),
            "dining_mode_label": DINING_LABELS.get(o.dining_mode, ""),
            "status": o.status,
            "status_label": STATUS_LABELS.get(o.status, ""),
            "created_at": format_utc(o.created_at),
        })

    return R.ok({
        "today_orders": today_orders,
        "today_sales": today_sales,
        "on_sale_dishes": on_sale_dishes,
        "status_counts": {
            "pending_pay": status_counts.get(1, 0),
            "pending_meal": status_counts.get(2, 0),
            "completed": status_counts.get(3, 0),
            "cancelled": status_counts.get(4, 0),
        },
        "recent_orders": recent_list,
    })
