"""订单相关 schema。"""
from typing import List, Literal, Optional

from pydantic import BaseModel


class OrderItemOut(BaseModel):
    id: int
    dish_id: int
    dish_name: str
    price: float
    quantity: int
    subtotal: float


class OrderOut(BaseModel):
    id: int
    order_no: str
    total_amount: float
    dining_mode: int  # 1=堂食,2=打包
    status: int  # 1=待支付,2=待出餐,3=已完成,4=已取消
    pay_status: int
    address: Optional[str] = None
    expire_at: Optional[str] = None
    created_at: Optional[str] = None
    paid_at: Optional[str] = None
    items: List[OrderItemOut] = []
    thumbnail: Optional[str] = None  # 首张菜品缩略图，用于列表展示


class CreateOrderRequest(BaseModel):
    dining_mode: Literal[1, 2]  # 1=堂食,2=打包，必填
    address: Optional[str] = None


class CreateOrderResponse(BaseModel):
    order_id: int
    order_no: str
    pay_params: Optional[dict] = None  # 微信支付预下单参数
