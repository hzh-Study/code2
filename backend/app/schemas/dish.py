"""菜品相关 schema。"""
from typing import Optional

from pydantic import BaseModel, Field


class DishOut(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    image: Optional[str] = None
    category_id: int
    status: int
    category_name: Optional[str] = None


class DishCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    price: float = Field(ge=0)
    description: Optional[str] = None
    image: Optional[str] = None
    category_id: int
    status: int = Field(default=1, ge=0, le=1)


class DishUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    price: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = None
    image: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[int] = Field(default=None, ge=0, le=1)
