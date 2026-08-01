"""FastAPI 入口：挂载路由、CORS、静态文件、统一异常处理。"""
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.admin import router as admin_router
from app.api.client import router as client_router
from app.config import CORS_ORIGINS, STATIC_URL_PREFIX, UPLOAD_DIR
from app.database import init_db
from app.schemas.common import R

app = FastAPI(title="拾味堂 · 餐厅堂食+外卖小程序后端", version="1.0.0")

# CORS：小程序/后台联调放开
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 统一异常 -> { code, msg, data }
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=R.fail(exc.status_code, str(exc.detail)))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content=R.fail(422, "参数校验失败", str(exc.errors())))


# 路由：/api/v1/client/* 与 /api/v1/admin/*
app.include_router(client_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    init_db()


# 静态资源：/static/... 访问 uploads/ 下的图片
app.mount(STATIC_URL_PREFIX, StaticFiles(directory=UPLOAD_DIR), name="static")


@app.get("/")
def root():
    return R.ok({"service": "restaurant backend", "docs": "/docs"})


@app.get("/health")
def health():
    return R.ok({"status": "ok"})
