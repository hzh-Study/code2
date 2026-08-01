"""小程序端：购物车。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.deps import get_current_user_id
from app.models.cart import Cart
from app.models.dish import Dish
from app.schemas.cart import CartAdd, CartUpdate
from app.schemas.common import R

router = APIRouter()


@router.get("/cart")
def get_cart(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    # 使用 JOIN 一次性查询购物车和菜品信息，避免 N+1 查询
    rows = db.query(Cart, Dish).join(Dish, Cart.dish_id == Dish.id).filter(Cart.user_id == user_id).all()
    out = []
    for cart_item, dish in rows:
        out.append({
            "id": cart_item.id,
            "dish_id": cart_item.dish_id,
            "name": dish.name,
            "price": float(dish.price),
            "image": dish.image,
            "quantity": cart_item.quantity,
            "subtotal": round(float(dish.price) * cart_item.quantity, 2),
            "status": dish.status,
        })
    return R.ok(out)


@router.post("/cart/add")
def add_cart(body: CartAdd, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == body.dish_id).first()
    if not dish or dish.status != 1:
        raise HTTPException(status_code=400, detail="菜品不存在或已下架")
    if body.quantity <= 0:
        raise HTTPException(status_code=400, detail="数量必须大于 0")
    item = db.query(Cart).filter(Cart.user_id == user_id, Cart.dish_id == body.dish_id).first()
    if item:
        item.quantity += body.quantity
        db.commit()
    else:
        try:
            item = Cart(user_id=user_id, dish_id=body.dish_id, quantity=body.quantity)
            db.add(item)
            db.commit()
        except IntegrityError:
            db.rollback()
            item = db.query(Cart).filter(Cart.user_id == user_id, Cart.dish_id == body.dish_id).first()
            if item:
                item.quantity += body.quantity
            db.commit()
    return R.ok(msg="已加入购物车")


@router.post("/cart/update")
def update_cart(body: CartUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    item = db.query(Cart).filter(Cart.user_id == user_id, Cart.dish_id == body.dish_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="购物车中无此菜品")
    if body.quantity <= 0:
        db.delete(item)
        db.commit()
        return R.ok(msg="已移除")
    item.quantity = body.quantity
    db.commit()
    return R.ok(msg="已更新")


@router.post("/cart/clear")
def clear_cart(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    db.query(Cart).filter(Cart.user_id == user_id).delete()
    db.commit()
    return R.ok(msg="购物车已清空")
