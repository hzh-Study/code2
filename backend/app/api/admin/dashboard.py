"""管理后台：数据看板。"""
from datetime import datetime

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
from app.services.order_state import DINING_LABELS, STATUS_LABELS

router = APIRouter()


@router.get("/dashboard")
def dashboard(_: int = Depends(get_current_admin_id), db: Session = Depends(get_db)):
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    today_orders = db.query(Order).filter(Order.created_at >= today_start).count()
    on_sale_dishes = db.query(Dish).filter(Dish.status == 1).count()

    # 今日销售额：使用 SQL 聚合函数，避免全量加载到内存
    today_sales = db.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        Order.paid_at >= today_start,
        Order.pay_status == 1,
        Order.status != 4,
    ).scalar()
    today_sales = round(float(today_sales), 2)

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
            "status_label": STATUS_LABELS.get(o.status, ""),
            "created_at": o.created_at.strftime("%Y-%m-%d %H:%M:%S") if o.created_at else None,
        })

    return R.ok({
        "today_orders": today_orders,
        "today_sales": today_sales,
        "on_sale_dishes": on_sale_dishes,
        "recent_orders": recent_list,
    })
