"""分类相关 schema。"""
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

CategoryName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int


class CategoryCreate(BaseModel):
    name: CategoryName
    sort_order: int = Field(default=0, ge=0)


class CategoryUpdate(BaseModel):
    name: Optional[CategoryName] = None
    sort_order: Optional[int] = Field(default=None, ge=0)
