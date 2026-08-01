"""小程序端路由聚合。"""
from fastapi import APIRouter

from app.api.client import auth, category, dish, cart, order, pay

router = APIRouter(prefix="/client", tags=["client"])
router.include_router(auth.router)
router.include_router(category.router)
router.include_router(dish.router)
router.include_router(cart.router)
router.include_router(order.router)
router.include_router(pay.router)
