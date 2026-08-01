"""小程序端：菜品（只读，仅返回在售）。"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import R
from app.schemas.dish import DishOut

router = APIRouter()


def _serialize(dish, category_name=None) -> dict:
    return DishOut(
        id=dish.id,
        name=dish.name,
        price=float(dish.price),
        description=dish.description,
        image=dish.image,
        category_id=dish.category_id,
        status=dish.status,
        category_name=category_name,
    ).model_dump()


@router.get("/dishes/hot")
def hot_dishes(limit: int = Query(6, ge=1, le=50), db: Session = Depends(get_db)):
    from app.models.dish import Dish

    rows = db.query(Dish).filter(Dish.status == 1).order_by(Dish.id.desc()).limit(limit).all()
    return R.ok([_serialize(d) for d in rows])


@router.get("/dishes")
def list_dishes(category_id: int = Query(None), db: Session = Depends(get_db)):
    from app.models.dish import Dish

    q = db.query(Dish).filter(Dish.status == 1)
    if category_id is not None:
        q = q.filter(Dish.category_id == category_id)
    rows = q.order_by(Dish.id.asc()).all()
    return R.ok([_serialize(d) for d in rows])


@router.get("/dishes/{dish_id}")
def dish_detail(dish_id: int, db: Session = Depends(get_db)):
    from app.models.dish import Dish

    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish or dish.status != 1:
        raise HTTPException(status_code=404, detail="菜品不存在或已下架")
    return R.ok(_serialize(dish))
