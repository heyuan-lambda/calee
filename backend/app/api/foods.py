"""API 路由 - 食物相关端点"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    ApiResponse,
    FoodCreate,
    FoodListItem,
    FoodResponse,
    FoodUpdate,
)
from app.services.food_service import food_service

router = APIRouter(prefix="/foods", tags=["foods"])


@router.get("", response_model=ApiResponse)
async def get_foods(
    search: str | None = Query(None, description="搜索关键词"),
    category: str | None = Query(None, description="食物分类"),
    is_custom: bool | None = Query(None, description="是否自定义食物"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """获取食物列表

    支持搜索和筛选：
    - search: 按名称或品牌搜索
    - category: 按分类筛选 (main, side, drink, snack, fruit, vegetable, other)
    - is_custom: 筛选自定义/预设食物
    """
    foods, total = await food_service.get_foods(
        db,
        search=search,
        category=category,
        is_custom=is_custom,
        limit=limit,
        offset=offset,
    )

    return ApiResponse(
        success=True,
        data={
            "foods": [
                FoodListItem(
                    id=f.id,
                    name=f.name,
                    brand=f.brand,
                    image_url=f.image_url,
                    calories_per_serving=f.calories_per_serving,
                    category=f.category,
                    is_custom=f.is_custom,
                ).model_dump()
                for f in foods
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        },
    )


@router.get("/categories/list", response_model=ApiResponse)
async def get_categories() -> ApiResponse:
    """获取食物分类列表"""
    categories = [
        {"value": "main", "label": "主食"},
        {"value": "side", "label": "配菜"},
        {"value": "drink", "label": "饮品"},
        {"value": "snack", "label": "零食"},
        {"value": "fruit", "label": "水果"},
        {"value": "vegetable", "label": "蔬菜"},
        {"value": "other", "label": "其他"},
    ]

    return ApiResponse(success=True, data=categories)


@router.get("/{food_id}", response_model=ApiResponse)
async def get_food(
    food_id: int,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """获取食物详情"""
    food = await food_service.get_food_by_id(db, food_id)

    if food is None:
        return ApiResponse(success=False, message="食物不存在")

    return ApiResponse(success=True, data=food.model_dump())


@router.post("", response_model=ApiResponse)
async def create_food(
    food_data: FoodCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """创建自定义食物"""
    food = await food_service.create_food(db, food_data, user_id=None)

    return ApiResponse(
        success=True,
        message="食物创建成功",
        data=food.model_dump(),
    )


@router.put("/{food_id}", response_model=ApiResponse)
async def update_food(
    food_id: int,
    food_data: FoodUpdate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """更新食物"""
    food = await food_service.update_food(db, food_id, food_data)

    if food is None:
        return ApiResponse(success=False, message="食物不存在")

    return ApiResponse(
        success=True,
        message="食物更新成功",
        data=food.model_dump(),
    )


@router.delete("/{food_id}", response_model=ApiResponse)
async def delete_food(
    food_id: int,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """删除食物"""
    success = await food_service.delete_food(db, food_id)

    if not success:
        return ApiResponse(success=False, message="食物不存在")

    return ApiResponse(success=True, message="食物删除成功")
