"""API 路由 - 仪表板相关端点"""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas import ApiResponse, DailySummary, UserGoalUpdate
from app.services.meal_service import meal_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# 临时用户 ID（简化版，实际应从认证获取）
DEFAULT_USER_ID = 1


@router.get("/summary", response_model=ApiResponse)
async def get_daily_summary(
    date_str: str | None = Query(None, description="日期 (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """获取每日摄入摘要

    包含：
    - 总摄入热量
    - 卡路里目标
    - 剩余卡路里
    - 使用百分比
    - 宏量营养素统计
    - 各餐食记录
    """
    target_date = date_str or date.today().isoformat()

    summary = await meal_service.get_daily_summary(
        db, DEFAULT_USER_ID, target_date, settings.daily_calorie_goal
    )

    return ApiResponse(success=True, data=summary.model_dump())


@router.post("/goals/update", response_model=ApiResponse)
async def update_goals(
    goal_data: UserGoalUpdate,
) -> ApiResponse:
    """更新用户目标（仅支持卡路里目标）"""
    settings.daily_calorie_goal = goal_data.daily_calorie_goal

    return ApiResponse(
        success=True,
        message="目标更新成功",
        data={"daily_calorie_goal": settings.daily_calorie_goal},
    )
