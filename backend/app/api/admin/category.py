"""管理后台：分类管理。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_admin_id
from app.models.category import Category
from app.models.dish import Dish
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.common import R

router = APIRouter()


@router.get("/categories")
def list_categories(_: int = Depends(get_current_admin_id), db: Session = Depends(get_db)):
    rows = db.query(Category).order_by(Category.sort_order.asc(), Category.id.asc()).all()
    return R.ok([{"id": r.id, "name": r.name, "sort_order": r.sort_order} for r in rows])


@router.post("/categories")
def create_category(
    body: CategoryCreate,
    _: int = Depends(get_current_admin_id),
    db: Session = Depends(get_db),
):
    cat = Category(name=body.name, sort_order=body.sort_order)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return R.ok({"id": cat.id, "name": cat.name, "sort_order": cat.sort_order})


@router.put("/categories/{cat_id}")
def update_category(
    cat_id: int,
    body: CategoryUpdate,
    _: int = Depends(get_current_admin_id),
    db: Session = Depends(get_db),
):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        return R.fail(3002, "分类不存在")
    if body.name is not None:
        cat.name = body.name
    if body.sort_order is not None:
        cat.sort_order = body.sort_order
    db.commit()
    return R.ok(msg="已更新")


@router.delete("/categories/{cat_id}")
def delete_category(
    cat_id: int,
    _: int = Depends(get_current_admin_id),
    db: Session = Depends(get_db),
):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        return R.fail(3002, "分类不存在")
    count = db.query(Dish).filter(Dish.category_id == cat_id).count()
    if count > 0:
        return R.fail(3003, f"该分类下还有 {count} 个菜品，无法删除")
    db.delete(cat)
    db.commit()
    return R.ok(msg="已删除")
