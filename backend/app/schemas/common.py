"""统一响应结构 R<T> 与分页模型。"""
from typing import Any, List

from pydantic import BaseModel, Field


class R:
    """统一响应：{ code, msg, data }，code!=0 表示业务失败。"""

    @staticmethod
    def ok(data: Any = None, msg: str = "success"):
        return {"code": 0, "msg": msg, "data": data}

    @staticmethod
    def fail(code: int = 1, msg: str = "error", data: Any = None):
        return {"code": code, "msg": msg, "data": data}


class PageData(BaseModel):
    """分页返回结构。"""
    list: List[Any] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
