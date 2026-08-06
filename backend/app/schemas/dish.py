"""菜品相关 schema。"""
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

DishName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)]


class DishOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    description: Optional[str] = None
    image: Optional[str] = None
    category_id: int
    status: int
    category_name: Optional[str] = None


class DishCreate(BaseModel):
    name: DishName
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    description: Optional[str] = Field(default=None, max_length=512)
    image: Optional[str] = Field(default=None, max_length=255)
    category_id: int = Field(gt=0)
    status: int = Field(default=1, ge=0, le=1)


class DishUpdate(BaseModel):
    name: Optional[DishName] = None
    price: Optional[Decimal] = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    description: Optional[str] = Field(default=None, max_length=512)
    image: Optional[str] = Field(default=None, max_length=255)
    category_id: Optional[int] = Field(default=None, gt=0)
    status: Optional[int] = Field(default=None, ge=0, le=1)
