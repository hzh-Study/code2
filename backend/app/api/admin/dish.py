"""管理后台：菜品管理（含下架，支持分页/筛选）。"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_admin_id
from app.models.cart import Cart
from app.models.category import Category
from app.models.dish import Dish
from app.models.order_item import OrderItem
from app.schemas.common import R
from app.schemas.dish import DishCreate, DishUpdate

router = APIRouter()


@router.get("/dishes")
def list_dishes(
    category_id: int | None = Query(None),
    keyword: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: int = Depends(get_current_admin_id),
    db: Session = Depends(get_db),
):
    q = db.query(Dish)
    if category_id is not None:
        q = q.filter(Dish.category_id == category_id)
    if keyword is not None and keyword:
        escaped = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        q = q.filter(Dish.name.like(f"%{escaped}%", escape="\\"))
    total = q.count()
    rows = q.order_by(Dish.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    cat_map = {c.id: c.name for c in db.query(Category).all()}
    data = [{
        "id": d.id,
        "name": d.name,
        "price": float(d.price),
        "description": d.description,
        "image": d.image,
        "category_id": d.category_id,
        "category_name": cat_map.get(d.category_id),
        "status": d.status,
    } for d in rows]
    return R.ok({"list": data, "total": total, "page": page, "page_size": page_size})


def _validate_category(db: Session, category_id: int) -> str | None:
    """校验分类是否存在，返回错误信息或 None。"""
    if not db.query(Category).filter(Category.id == category_id).first():
        return "分类不存在"
    return None


@router.post("/dishes")
def create_dish(
    body: DishCreate,
    _: int = Depends(get_current_admin_id),
    db: Session = Depends(get_db),
):
    err = _validate_category(db, body.category_id)
    if err:
        return R.fail(3002, err)
    dish = Dish(
        name=body.name,
        price=body.price,
        description=body.description,
        image=body.image,
        category_id=body.category_id,
        status=body.status,
    )
    db.add(dish)
    db.commit()
    db.refresh(dish)
    return R.ok({"id": dish.id})


@router.put("/dishes/{dish_id}")
def update_dish(
    dish_id: int,
    body: DishUpdate,
    _: int = Depends(get_current_admin_id),
    db: Session = Depends(get_db),
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        return R.fail(3004, "菜品不存在")
    update_data = body.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        err = _validate_category(db, update_data["category_id"])
        if err:
            return R.fail(3002, err)
    for field, value in update_data.items():
        setattr(dish, field, value)
    db.commit()
    db.refresh(dish)
    return R.ok(msg="已更新")


@router.delete("/dishes/{dish_id}")
def delete_dish(
    dish_id: int,
    _: int = Depends(get_current_admin_id),
    db: Session = Depends(get_db),
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        return R.fail(3004, "菜品不存在")
    has_order_ref = db.query(OrderItem).filter(OrderItem.dish_id == dish_id).first() is not None
    if has_order_ref:
        return R.fail(3005, "该菜品已被订单引用，无法删除，建议下架")
    cart_count = db.query(Cart).filter(Cart.dish_id == dish_id).count()
    if cart_count > 0:
        raise HTTPException(status_code=400, detail=f"该菜品已被 {cart_count} 个购物车引用，请改为下架而非删除")
    db.delete(dish)
    db.commit()
    return R.ok(msg="已删除")


@router.post("/dishes/{dish_id}/toggle")
def toggle_dish(
    dish_id: int,
    _: int = Depends(get_current_admin_id),
    db: Session = Depends(get_db),
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        return R.fail(3004, "菜品不存在")
    dish.status = 0 if dish.status == 1 else 1
    db.commit()
    return R.ok({"id": dish.id, "status": dish.status})
