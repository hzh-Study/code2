"""管理后台路由聚合。"""
from fastapi import APIRouter

from app.api.admin import auth, category, dish, order, upload, dashboard

router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(auth.router)
router.include_router(category.router)
router.include_router(dish.router)
router.include_router(order.router)
router.include_router(upload.router)
router.include_router(dashboard.router)
