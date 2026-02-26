"""餐食服务"""
from datetime import date, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Food, Meal, MealEntry
from app.schemas import (
    DailySummary,
    FoodResponse,
    MacroNutrients,
    MealCreate,
    MealEntryCreate,
    MealEntryResponse,
    MealResponse,
)


class MealService:
    """餐食服务"""

    async def get_meals_by_date(
        self, db: AsyncSession, user_id: int, date_str: str
    ) -> dict[str, list[MealResponse]]:
        """获取指定日期的餐食记录

        Args:
            db: 数据库会话
            user_id: 用户 ID
            date_str: 日期字符串 (YYYY-MM-DD)

        Returns:
            按餐食类型分组的餐食记录
        """
        query = (
            select(Meal)
            .where(Meal.user_id == user_id, Meal.date == date_str)
            .options(selectinload(Meal.entries).selectinload(MealEntry.food))
            .order_by(Meal.created_at)
        )

        result = await db.execute(query)
        meals = result.scalars().all()

        grouped_meals: dict[str, list[MealResponse]] = {
            "breakfast": [],
            "lunch": [],
            "dinner": [],
            "snack": [],
        }

        for meal in meals:
            meal_response = await self._convert_to_response(meal)
            if meal_response:
                grouped_meals[meal.meal_type].append(meal_response)

        return grouped_meals

    async def get_meal_by_id(
        self, db: AsyncSession, meal_id: int
    ) -> MealResponse | None:
        """根据 ID 获取餐食

        Args:
            db: 数据库会话
            meal_id: 餐食 ID

        Returns:
            餐食响应或 None
        """
        query = (
            select(Meal)
            .where(Meal.id == meal_id)
            .options(selectinload(Meal.entries).selectinload(MealEntry.food))
        )

        result = await db.execute(query)
        meal = result.scalar_one_or_none()

        if meal is None:
            return None

        return await self._convert_to_response(meal)

    async def create_meal(
        self, db: AsyncSession, user_id: int, meal_data: MealCreate
    ) -> MealResponse:
        """创建餐食记录

        Args:
            db: 数据库会话
            user_id: 用户 ID
            meal_data: 餐食数据

        Returns:
            创建的餐食响应
        """
        # 使用当前日期或提供的日期
        meal_date = meal_data.date or date.today().isoformat()

        meal = Meal(
            user_id=user_id,
            date=meal_date,
            meal_type=meal_data.meal_type,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        db.add(meal)
        await db.flush()

        # 添加条目
        for entry_data in meal_data.entries:
            entry = MealEntry(
                meal_id=meal.id,
                food_id=entry_data.food_id,
                servings=entry_data.servings,
                notes=entry_data.notes,
                image_url=entry_data.image_url,
                created_at=datetime.now().isoformat(),
            )
            db.add(entry)

        await db.flush()
        await db.refresh(meal)

        # 重新查询以获取完整数据
        return await self.get_meal_by_id(db, meal.id)  # type: ignore

    async def delete_meal(self, db: AsyncSession, meal_id: int, user_id: int) -> bool:
        """删除餐食

        Args:
            db: 数据库会话
            meal_id: 餐食 ID
            user_id: 用户 ID

        Returns:
            是否删除成功
        """
        # 先检查餐食是否属于该用户
        result = await db.execute(select(Meal).where(Meal.id == meal_id))
        meal = result.scalar_one_or_none()

        if meal is None or meal.user_id != user_id:
            return False

        await db.delete(meal)
        return True

    async def delete_meal_entry(
        self, db: AsyncSession, meal_id: int, entry_id: int, user_id: int
    ) -> bool:
        """删除餐食条目

        Args:
            db: 数据库会话
            meal_id: 餐食 ID
            entry_id: 条目 ID
            user_id: 用户 ID

        Returns:
            是否删除成功
        """
        # 检查餐食是否属于该用户
        meal_result = await db.execute(
            select(Meal).where(Meal.id == meal_id, Meal.user_id == user_id)
        )
        meal = meal_result.scalar_one_or_none()

        if meal is None:
            return False

        # 删除条目
        result = await db.execute(
            select(MealEntry).where(MealEntry.id == entry_id, MealEntry.meal_id == meal_id)
        )
        entry = result.scalar_one_or_none()

        if entry is None:
            return False

        await db.delete(entry)
        return True

    async def get_daily_summary(
        self, db: AsyncSession, user_id: int, date_str: str, calorie_goal: int
    ) -> DailySummary:
        """获取每日摄入摘要

        Args:
            db: 数据库会话
            user_id: 用户 ID
            date_str: 日期字符串 (YYYY-MM-DD)
            calorie_goal: 每日卡路里目标

        Returns:
            每日摘要
        """
        meals = await self.get_meals_by_date(db, user_id, date_str)

        total_calories = 0.0
        total_macros = MacroNutrients()

        # 计算总热量和宏量营养素
        for meal_type, meal_list in meals.items():
            for meal in meal_list:
                total_calories += meal.total_calories
                total_macros.carbohydrates += sum(
                    e.food.carbohydrates * e.servings for e in meal.entries
                )
                total_macros.protein += sum(e.food.protein * e.servings for e in meal.entries)
                total_macros.fat += sum(e.food.fat * e.servings for e in meal.entries)

        calories_remaining = max(0, calorie_goal - total_calories)
        calories_used_percentage = (total_calories / calorie_goal * 100) if calorie_goal > 0 else 0

        return DailySummary(
            date=date_str,
            total_calories=round(total_calories, 1),
            calorie_goal=calorie_goal,
            calories_remaining=round(calories_remaining, 1),
            calories_used_percentage=round(calories_used_percentage, 1),
            macros=total_macros,
            meals=meals,
        )

    async def _convert_to_response(self, meal: Meal) -> MealResponse | None:
        """转换 Meal 模型为响应

        Args:
            meal: 餐食模型

        Returns:
            餐食响应
        """
        entries = []
        total_calories = 0.0

        for entry in meal.entries:
            if entry.food is None:
                continue

            food_response = FoodResponse(
                id=entry.food.id,
                name=entry.food.name,
                brand=entry.food.brand,
                image_url=entry.food.image_url,
                serving_size=entry.food.serving_size,
                serving_unit=entry.food.serving_unit,
                calories_per_serving=entry.food.calories_per_serving,
                carbohydrates=entry.food.carbohydrates,
                protein=entry.food.protein,
                fat=entry.food.fat,
                fiber=entry.food.fiber,
                sugar=entry.food.sugar,
                category=entry.food.category,
                is_custom=bool(entry.food.is_custom),
                created_at=entry.food.created_at,
            )

            entry_calories = entry.food.calories_per_serving * entry.servings
            total_calories += entry_calories

            entries.append(
                MealEntryResponse(
                    id=entry.id,
                    food_id=entry.food_id,
                    servings=entry.servings,
                    notes=entry.notes,
                    image_url=entry.image_url,
                    food=food_response,
                    calories=round(entry_calories, 1),
                    created_at=entry.created_at,
                )
            )

        return MealResponse(
            id=meal.id,
            meal_type=meal.meal_type,
            date=meal.date,
            entries=entries,
            total_calories=round(total_calories, 1),
            created_at=meal.created_at,
        )


# 全局服务实例
meal_service = MealService()
