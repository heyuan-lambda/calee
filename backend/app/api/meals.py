"""API 路由 - 餐食记录相关端点"""
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas import ApiResponse, DailySummary, MealCreate, MealResponse
from app.services.meal_service import meal_service

router = APIRouter(prefix="/meals", tags=["meals"])

# 临时用户 ID（简化版，实际应从认证获取）
DEFAULT_USER_ID = 1


@router.get("", response_model=ApiResponse)
async def get_meals(
    date_str: str | None = Query(None, description="日期 (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """获取餐食记录

    如果不提供日期，返回今天的记录
    """
    target_date = date_str or date.today().isoformat()

    meals = await meal_service.get_meals_by_date(db, DEFAULT_USER_ID, target_date)

    return ApiResponse(
        success=True,
        data={
            "date": target_date,
            "meals": {
                meal_type: [meal.model_dump() for meal in meal_list]
                for meal_type, meal_list in meals.items()
            },
        },
    )


@router.get("/{meal_id}", response_model=ApiResponse)
async def get_meal(
    meal_id: int,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """获取餐食详情"""
    meal = await meal_service.get_meal_by_id(db, meal_id)

    if meal is None:
        return ApiResponse(success=False, message="餐食记录不存在")

    return ApiResponse(success=True, data=meal.model_dump())


@router.post("", response_model=ApiResponse)
async def create_meal(
    meal_data: MealCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """添加餐食记录"""
    try:
        meal = await meal_service.create_meal(db, DEFAULT_USER_ID, meal_data)

        return ApiResponse(
            success=True,
            message="餐食记录添加成功",
            data=meal.model_dump(),
        )
    except Exception as e:
        return ApiResponse(success=False, message=f"添加失败: {e!s}")


@router.delete("/{meal_id}", response_model=ApiResponse)
async def delete_meal(
    meal_id: int,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """删除餐食记录"""
    success = await meal_service.delete_meal(db, meal_id, DEFAULT_USER_ID)

    if not success:
        return ApiResponse(success=False, message="餐食记录不存在或无权删除")

    return ApiResponse(success=True, message="餐食记录删除成功")


@router.post("/{meal_id}/entries/{entry_id}/delete", response_model=ApiResponse)
async def delete_meal_entry(
    meal_id: int,
    entry_id: int,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """删除餐食条目"""
    success = await meal_service.delete_meal_entry(db, meal_id, entry_id, DEFAULT_USER_ID)

    if not success:
        return ApiResponse(success=False, message="餐食条目不存在或无权删除")

    return ApiResponse(success=True, message="餐食条目删除成功")
