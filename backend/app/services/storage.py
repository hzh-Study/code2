"""本地图片存储：按日期子目录保存，返回静态访问路径。"""
import os
import uuid

from fastapi import HTTPException, UploadFile

from app.config import STATIC_URL_PREFIX, UPLOAD_DIR
from app.utils.time import now

ALLOWED_EXT = {".jpg", ".jpeg", ".png"}
MAX_SIZE = 2 * 1024 * 1024  # 2MB


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def save_upload(file: UploadFile, sub_dir: str = "dishes") -> str:
    """保存上传文件，返回形如 /static/dishes/2026/07/uuid.ext 的访问路径。"""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="仅支持 jpg/png 图片")
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="仅支持 jpg/png 图片")
    # 分块读取累计大小，超限立即终止
    content = bytearray()
    while True:
        chunk = file.file.read(64 * 1024)
        if not chunk:
            break
        content.extend(chunk)
        if len(content) > MAX_SIZE:
            raise HTTPException(status_code=400, detail="图片需小于 2MB")
    if not content.startswith(b'\xff\xd8') and not content.startswith(b'\x89PNG'):
        raise HTTPException(status_code=400, detail="文件内容非有效图片")

    current_time = now()
    rel_dir = os.path.join(sub_dir, f"{current_time.year}", f"{current_time.month:02d}")
    abs_dir = os.path.join(UPLOAD_DIR, rel_dir)
    _ensure_dir(abs_dir)

    fname = f"{uuid.uuid4().hex}{ext}"
    abs_path = os.path.join(abs_dir, fname)
    with open(abs_path, "wb") as f:
        f.write(content)

    # 归一化为正斜杠 URL
    url = f"{STATIC_URL_PREFIX}/{rel_dir.replace(os.sep, '/')}/{fname}"
    return url
