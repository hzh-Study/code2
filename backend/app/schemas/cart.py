"""购物车相关 schema。"""
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

MAX_CART_QUANTITY = 99


class CartAdd(BaseModel):
    dish_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0, le=MAX_CART_QUANTITY)


class CartUpdate(BaseModel):
    dish_id: int = Field(gt=0)
    quantity: int = Field(ge=0, le=MAX_CART_QUANTITY)  # 0 表示移除


class CartItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dish_id: int
    name: str
    price: Decimal
    image: Optional[str] = None
    quantity: int
    subtotal: Decimal
    status: int  # 菜品在售状态，便于前端判断是否下架
