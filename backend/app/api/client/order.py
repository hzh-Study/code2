"""小程序端：订单。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.deps import get_current_user_id
from app.models.cart import Cart
from app.models.dish import Dish
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.user import User
from app.schemas.common import R
from app.schemas.order import CreateOrderRequest
from app.services import wechat
from app.services.order_state import (
    DINING_HALL,
    PACKING,
    can_cancel,
    mark_cancelled,
)
from app.utils.time import expire_at, is_expired

router = APIRouter()


def _gen_order_no() -> str:
    import uuid
    return f"SW{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


def _serialize_order(order: Order, db: Session, with_items: bool = True) -> dict:
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    item_out = [{
        "id": it.id,
        "dish_id": it.dish_id,
        "dish_name": it.dish_name,
        "price": float(it.price),
        "quantity": it.quantity,
        "subtotal": float(it.subtotal),
    } for it in items]
    # 缩略图取首张菜品图片
    first_item = items[0] if items else None
    thumbnail = None
    if first_item:
        dish = db.query(Dish).filter(Dish.id == first_item.dish_id).first()
        thumbnail = dish.image if dish else None
    # 菜品摘要（列表页展示用）
    detail = "、".join(f"{it.dish_name}x{it.quantity}" for it in items)
    return {
        "id": order.id,
        "order_no": order.order_no,
        "total_amount": float(order.total_amount),
        "dining_mode": order.dining_mode,
        "status": order.status,
        "pay_status": order.pay_status,
        "address": order.address,
        "expire_at": order.expire_at.strftime("%Y-%m-%d %H:%M:%S") if order.expire_at else None,
        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else None,
        "paid_at": order.paid_at.strftime("%Y-%m-%d %H:%M:%S") if order.paid_at else None,
        "items": item_out if with_items else [],
        "detail": detail,
        "thumbnail": thumbnail,
    }


def _prepay(order: Order, db: Session) -> dict:
    user = db.query(User).filter(User.id == order.user_id).first()
    openid = user.openid if user else ""
    return wechat.build_pay_params(order, openid)


@router.get("/orders")
def list_orders(
    status: int = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    q = db.query(Order).filter(Order.user_id == user_id)
    if status is not None:
        q = q.filter(Order.status == status)
    rows = q.order_by(Order.id.desc()).all()
    
    # 懒校验超时关闭
    from app.services.order_state import STATUS_CANCELLED, STATUS_PENDING
    from app.utils.time import is_expired
    expired_count = 0
    for o in rows:
        if o.status == STATUS_PENDING and is_expired(o.expire_at):
            o.status = STATUS_CANCELLED
            expired_count += 1
    
    # 一次性提交所有过期订单的状态变更
    if expired_count:
        db.commit()
        # 重新查询以获取更新后的数据
        q = db.query(Order).filter(Order.user_id == user_id)
        if status is not None:
            q = q.filter(Order.status == status)
        rows = q.order_by(Order.id.desc()).all()
    
    return R.ok([_serialize_order(o, db, with_items=False) for o in rows])


@router.get("/orders/{order_id}")
def order_detail(order_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return R.ok(_serialize_order(order, db))


@router.post("/orders")
def create_order(
    body: CreateOrderRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if body.dining_mode not in (DINING_HALL, PACKING):
        raise HTTPException(status_code=400, detail="用餐方式必为 1(堂食) 或 2(打包)")
    # 对地址进行 strip 处理，纯空格视为无效地址
    if body.address:
        body.address = body.address.strip()
    if body.dining_mode == PACKING and not body.address:
        raise HTTPException(status_code=400, detail="打包订单需填写收货地址")
    cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="购物车为空")

    # 从购物车快照生成订单项，校验在售
    order_items = []
    total = 0.0
    for ci in cart_items:
        dish = db.query(Dish).filter(Dish.id == ci.dish_id).first()
        if not dish or dish.status != 1:
            raise HTTPException(status_code=400, detail=f"菜品「{dish.name if dish else '未知'}」已下架，无法下单")
        subtotal = round(float(dish.price) * ci.quantity, 2)
        total += subtotal
        order_items.append(OrderItem(
            dish_id=dish.id,
            dish_name=dish.name,
            price=dish.price,
            quantity=ci.quantity,
            subtotal=subtotal,
        ))
    total = round(total, 2)

    order = Order(
        order_no=_gen_order_no(),
        user_id=user_id,
        total_amount=total,
        dining_mode=body.dining_mode,
        status=1,
        pay_status=0,
        address=body.address if body.dining_mode == PACKING else None,
        expire_at=expire_at(),
    )
    try:
        db.add(order)
        db.flush()  # 先分配 order.id，不提交事务
        for oi in order_items:
            oi.order_id = order.id
            db.add(oi)
        # 清空已下单的购物车项
        db.query(Cart).filter(Cart.user_id == user_id).delete()
        db.commit()  # 订单 + 订单项 + 清空购物车一次性提交，避免产生无明细的孤儿订单
    except IntegrityError:
        db.rollback()
        # 创建全新的 Order 对象，避免复用 rollback 后过期的 ORM 对象
        order = Order(
            order_no=_gen_order_no(),
            user_id=user_id,
            total_amount=total,
            dining_mode=body.dining_mode,
            status=1,
            pay_status=0,
            address=body.address if body.dining_mode == PACKING else None,
            expire_at=expire_at(),
        )
        db.add(order)
        db.flush()
        # 重新构建订单项
        for ci in cart_items:
            dish = db.query(Dish).filter(Dish.id == ci.dish_id).first()
            if dish:
                db.add(OrderItem(
                    order_id=order.id,
                    dish_id=dish.id,
                    dish_name=dish.name,
                    price=dish.price,
                    quantity=ci.quantity,
                    subtotal=round(float(dish.price) * ci.quantity, 2),
                ))
        db.query(Cart).filter(Cart.user_id == user_id).delete()
        db.commit()

    pay_params = _prepay(order, db)
    data = _serialize_order(order, db)
    data["order_id"] = order.id
    data["pay_params"] = pay_params
    return R.ok(data)


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if not can_cancel(order):
        raise HTTPException(status_code=400, detail="仅待支付订单可取消")
    mark_cancelled(db, order)
    return R.ok(msg="订单已取消")


@router.post("/orders/{order_id}/repay")
def repay_order(order_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != 1:
        raise HTTPException(status_code=400, detail="仅待支付订单可重新支付")
    if is_expired(order.expire_at):
        mark_cancelled(db, order)
        raise HTTPException(status_code=400, detail="订单已超时取消")
    pay_params = _prepay(order, db)
    return R.ok({
        "id": order.id,
        "order_id": order.id,
        "order_no": order.order_no,
        "pay_params": pay_params,
    })
