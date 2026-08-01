"""分类相关 schema。"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=64)
    sort_order: Optional[int] = None
