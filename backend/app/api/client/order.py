"""小程序端：订单。"""
import logging
import threading
from datetime import datetime
from decimal import Decimal

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
    STATUS_CANCELLED,
    STATUS_PENDING,
    can_cancel,
    expire_pending_orders,
    mark_cancelled,
    mark_paid,
)
from app.utils.time import expire_at, format_utc, is_expired

router = APIRouter()

# SQLite 结算串行化锁：避免原生 BEGIN IMMEDIATE 绕过 SQLAlchemy 事务管理
_checkout_locks: dict[int, threading.Lock] = {}
_checkout_locks_guard = threading.Lock()


def _gen_order_no() -> str:
    import uuid
    return f"SW{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:16].upper()}"


def _lock_checkout(db: Session, user_id: int) -> None:
    """串行化同一用户的结算，防止并发请求重复消费一份购物车。"""
    with _checkout_locks_guard:
        lock = _checkout_locks.setdefault(user_id, threading.Lock())
    lock.acquire()
    try:
        if db.bind is not None and db.bind.dialect.name == "sqlite":
            # SQLite：用应用层锁 + 普通查询，不走原生 BEGIN IMMEDIATE
            user_exists = db.query(User.id).filter(User.id == user_id).first()
        else:
            # MySQL：使用 SELECT ... FOR UPDATE 行级锁
            user_exists = db.query(User.id).filter(User.id == user_id).with_for_update().first()
    finally:
        lock.release()
    if user_exists is None:
        raise HTTPException(status_code=401, detail="用户不存在")


def _load_items_and_dish_map(db: Session, order_ids):
    """批量加载订单项与菜品映射，避免 N+1 查询。"""
    if not order_ids:
        return {}, {}
    all_items = db.query(OrderItem).filter(OrderItem.order_id.in_(order_ids)).all()
    dish_ids = {it.dish_id for it in all_items}
    dishes = db.query(Dish).filter(Dish.id.in_(dish_ids)).all() if dish_ids else []
    dish_map = {d.id: d for d in dishes}
    items_by_order = {}
    for it in all_items:
        items_by_order.setdefault(it.order_id, []).append(it)
    return items_by_order, dish_map


def _serialize_order(order: Order, items, dish_map, with_items: bool = True) -> dict:
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
        dish = dish_map.get(first_item.dish_id)
        thumbnail = dish.image if dish else None
    # 菜品摘要（列表页展示用）
    detail = "、".join(f"{it.dish_name}x{it.quantity}" for it in items)
    item_count = sum(item.quantity for item in items)
    return {
        "id": order.id,
        "order_no": order.order_no,
        "total_amount": float(order.total_amount),
        "dining_mode": order.dining_mode,
        "status": order.status,
        "pay_status": order.pay_status,
        "address": order.address,
        "expire_at": format_utc(order.expire_at),
        "created_at": format_utc(order.created_at),
        "paid_at": format_utc(order.paid_at),
        "items": item_out if with_items else [],
        "detail": detail,
        "item_count": item_count,
        "thumbnail": thumbnail,
    }


def _prepay(order: Order, db: Session) -> dict:
    user = db.query(User).filter(User.id == order.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    openid = user.openid
    return wechat.build_pay_params(order, openid)


@router.get("/orders")
def list_orders(
    status: int = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    expire_pending_orders(db, user_id)
    q = db.query(Order).filter(Order.user_id == user_id)
    if status is not None:
        q = q.filter(Order.status == status)
    rows = q.order_by(Order.id.desc()).all()

    if not rows:
        return R.ok([])

    # 批量加载订单项与菜品，避免 N+1
    items_by_order, dish_map = _load_items_and_dish_map(db, [o.id for o in rows])
    return R.ok([_serialize_order(o, items_by_order.get(o.id, []), dish_map, with_items=False) for o in rows])


@router.get("/orders/{order_id}")
def order_detail(order_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    expire_pending_orders(db, user_id)
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    items_by_order, dish_map = _load_items_and_dish_map(db, [order.id])
    return R.ok(_serialize_order(order, items_by_order.get(order.id, []), dish_map))


@router.post("/orders")
def create_order(
    body: CreateOrderRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if body.dining_mode not in (DINING_HALL, PACKING):
        raise HTTPException(status_code=400, detail="用餐方式必为 1(堂食) 或 2(打包)")
    # 主 PRD 约定打包仅标记用餐方式，不强制地址；保留可选字段兼容旧客户端。
    if body.address:
        body.address = body.address.strip()
        if not body.address:
            body.address = None
    _lock_checkout(db, user_id)
    cart_query = db.query(Cart).filter(Cart.user_id == user_id)
    if db.bind is not None and db.bind.dialect.name != "sqlite":
        cart_query = cart_query.with_for_update()
    cart_items = cart_query.all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="购物车为空")

    # 从购物车快照生成订单项，校验在售
    order_items = []
    total = Decimal("0")
    for ci in cart_items:
        dish = db.query(Dish).filter(Dish.id == ci.dish_id).first()
        if not dish:
            raise HTTPException(status_code=400, detail=f"菜品（id={ci.dish_id}）不存在，无法下单")
        if dish.status != 1:
            raise HTTPException(status_code=400, detail=f"菜品「{dish.name}」已下架，无法下单")
        subtotal = (Decimal(str(dish.price)) * ci.quantity).quantize(Decimal("0.01"))
        total += subtotal
        order_items.append(OrderItem(
            dish_id=dish.id,
            dish_name=dish.name,
            price=dish.price,
            quantity=ci.quantity,
            subtotal=subtotal,
        ))
    total = total.quantize(Decimal("0.01"))

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
    except Exception:
        logging.exception("订单创建失败（非唯一性冲突）")
        db.rollback()
        raise HTTPException(status_code=500, detail="订单创建失败，请重试")
        # 创建全新的 Order 对象，避免复用 rollback 后过期的 ORM 对象
        # 重新构建订单项，校验在售，使用 Decimal 计算小计和总额（与主路径一致）
        retry_order_items = []
        retry_total = Decimal("0")
        for ci in cart_items:
            dish = db.query(Dish).filter(Dish.id == ci.dish_id).first()
            if not dish:
                raise HTTPException(status_code=400, detail=f"菜品（id={ci.dish_id}）不存在，无法下单")
            if dish.status != 1:
                raise HTTPException(status_code=400, detail=f"菜品「{dish.name}」已下架，无法下单")
            subtotal = (Decimal(str(dish.price)) * ci.quantity).quantize(Decimal("0.01"))
            retry_total += subtotal
            retry_order_items.append(OrderItem(
                dish_id=dish.id,
                dish_name=dish.name,
                price=dish.price,
                quantity=ci.quantity,
                subtotal=subtotal,
            ))
        retry_total = retry_total.quantize(Decimal("0.01"))
        order = Order(
            order_no=_gen_order_no(),
            user_id=user_id,
            total_amount=retry_total,
            dining_mode=body.dining_mode,
            status=1,
            pay_status=0,
            address=body.address if body.dining_mode == PACKING else None,
            expire_at=expire_at(),
        )
        try:
            db.add(order)
            db.flush()
            for oi in retry_order_items:
                oi.order_id = order.id
                db.add(oi)
            db.query(Cart).filter(Cart.user_id == user_id).delete()
            db.commit()
        except Exception:
            logging.exception("订单创建重试失败")
            db.rollback()
            raise HTTPException(status_code=500, detail="订单创建失败，请重试")

    # 加载订单项与菜品映射用于序列化
    items_by_order, dish_map = _load_items_and_dish_map(db, [order.id])

    try:
        pay_params = _prepay(order, db)
    except Exception:
        logging.exception("订单已创建，但微信预下单失败: order_no=%s", order.order_no)
        # 预支付失败但订单已创建——返回订单信息，提示用户到订单列表完成支付
        data = _serialize_order(order, items_by_order.get(order.id, []), dish_map)
        data["order_id"] = order.id
        data["pay_params"] = None
        data["message"] = "订单已创建，请到订单列表完成支付"
        return R.ok(data)
    data = _serialize_order(order, items_by_order.get(order.id, []), dish_map)
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
    if not wechat.DEV_MODE:
        try:
            close_result = wechat.close_order(order)
        except Exception as exc:
            logging.exception("用户取消时微信关单失败: order_no=%s", order.order_no)
            raise HTTPException(status_code=502, detail="订单暂时无法取消，请稍后重试") from exc
        if close_result == "paid":
            mark_paid(db, order)
            raise HTTPException(status_code=409, detail="订单已支付，无法取消")
    if not mark_cancelled(db, order):
        raise HTTPException(status_code=409, detail="订单状态已变化，请刷新后重试")
    return R.ok(msg="订单已取消")


@router.post("/orders/{order_id}/repay")
def repay_order(order_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != 1:
        raise HTTPException(status_code=400, detail="仅待支付订单可重新支付")
    if is_expired(order.expire_at):
        expire_pending_orders(db, user_id)
        db.refresh(order)
        if order.status == STATUS_PENDING:
            raise HTTPException(status_code=502, detail="订单关闭失败，请稍后重试")
        raise HTTPException(status_code=400, detail="订单已超时取消")
    try:
        pay_params = _prepay(order, db)
    except HTTPException:
        raise
    except Exception as exc:
        logging.exception("微信预下单失败: order_no=%s", order.order_no)
        raise HTTPException(status_code=502, detail="支付服务暂不可用，请稍后重试") from exc
    return R.ok({
        "id": order.id,
        "order_id": order.id,
        "order_no": order.order_no,
        "pay_params": pay_params,
    })
