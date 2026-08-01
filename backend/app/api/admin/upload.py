"""管理后台：本地图片上传。"""
from fastapi import APIRouter, Depends, File, UploadFile

from app.deps import get_current_admin_id
from app.schemas.common import R
from app.services.storage import save_upload

router = APIRouter()


@router.post("/upload")
def upload(
    file: UploadFile = File(...),
    _: int = Depends(get_current_admin_id),
):
    url = save_upload(file, sub_dir="dishes")
    return R.ok({"url": url, "path": url})
