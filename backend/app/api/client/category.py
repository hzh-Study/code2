"""小程序端：分类（只读）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.category import CategoryOut
from app.schemas.common import R

router = APIRouter()


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    from app.models.category import Category

    rows = db.query(Category).order_by(Category.sort_order.asc(), Category.id.asc()).all()
    return R.ok([CategoryOut.model_validate(r).model_dump() for r in rows])
