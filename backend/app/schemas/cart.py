"""购物车相关 schema。"""
from typing import Optional

from pydantic import BaseModel, Field


class CartAdd(BaseModel):
    dish_id: int
    quantity: int = Field(default=1, gt=0)


class CartUpdate(BaseModel):
    dish_id: int
    quantity: int = Field(ge=0)  # 0 表示移除


class CartItemOut(BaseModel):
    id: int
    dish_id: int
    name: str
    price: float
    image: Optional[str] = None
    quantity: int
    subtotal: float
    status: int  # 菜品在售状态，便于前端判断是否下架
