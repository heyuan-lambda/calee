"""API 路由 - 图片上传和识别端点"""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas import ApiResponse
from app.services import image_recognition_service

router = APIRouter(prefix="/upload", tags=["upload"])

# 确保上传目录存在
settings.upload_dir.mkdir(parents=True, exist_ok=True)


@router.post("/recognize", response_model=ApiResponse)
async def recognize_food_image(
    file: UploadFile = File(..., description="食物图片"),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """上传图片并识别食物

    支持的图片格式：jpg, jpeg, png, webp
    最大文件大小：5MB
    """
    # 验证文件大小
    content = await file.read()
    if len(content) > settings.max_upload_size:
        return ApiResponse(success=False, message="文件过大，最大支持 5MB")

    # 验证文件类型
    file_ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if file_ext not in ["jpg", "jpeg", "png", "webp"]:
        return ApiResponse(success=False, message="不支持的图片格式")

    # 保存图片
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    filename = f"{timestamp}_{unique_id}.{file_ext}"
    file_path = settings.upload_dir / filename

    with open(file_path, "wb") as f:
        f.write(content)

    # 调用识别服务
    image_format = "jpeg" if file_ext in ["jpg", "jpeg"] else file_ext
    result = await image_recognition_service.recognize_food(content, image_format)

    if not result.success:
        return ApiResponse(
            success=False,
            message=result.error or "识别失败",
            data={"image_url": f"/uploads/{filename}"},
        )

    # 返回识别结果
    return ApiResponse(
        success=True,
        message="识别成功",
        data={
            "image_url": f"/uploads/{filename}",
            "foods": [food.model_dump() for food in result.foods],
        },
    )
