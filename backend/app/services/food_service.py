"""食物服务"""
from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Food
from app.schemas import FoodCreate, FoodResponse, FoodUpdate


class FoodService:
    """食物服务"""

    async def get_foods(
        self,
        db: AsyncSession,
        search: str | None = None,
        category: str | None = None,
        is_custom: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[FoodResponse], int]:
        """获取食物列表

        Args:
            db: 数据库会话
            search: 搜索关键词
            category: 分类筛选
            is_custom: 是否自定义食物
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            (食物列表, 总数)
        """
        query = select(Food)

        # 搜索过滤
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Food.name.like(search_pattern),
                    Food.brand.like(search_pattern),
                )
            )

        # 分类过滤
        if category:
            query = query.where(Food.category == category)

        # 自定义过滤
        if is_custom is not None:
            query = query.where(Food.is_custom == (1 if is_custom else 0))

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页和排序
        query = query.order_by(Food.name).offset(offset).limit(limit)

        result = await db.execute(query)
        foods = result.scalars().all()

        return [
            FoodResponse(
                id=f.id,
                name=f.name,
                brand=f.brand,
                image_url=f.image_url,
                serving_size=f.serving_size,
                serving_unit=f.serving_unit,
                calories_per_serving=f.calories_per_serving,
                carbohydrates=f.carbohydrates,
                protein=f.protein,
                fat=f.fat,
                fiber=f.fiber,
                sugar=f.sugar,
                category=f.category,
                is_custom=bool(f.is_custom),
                created_at=f.created_at,
            )
            for f in foods
        ], total

    async def get_food_by_id(self, db: AsyncSession, food_id: int) -> FoodResponse | None:
        """根据 ID 获取食物

        Args:
            db: 数据库会话
            food_id: 食物 ID

        Returns:
            食物响应或 None
        """
        result = await db.execute(select(Food).where(Food.id == food_id))
        food = result.scalar_one_or_none()

        if food is None:
            return None

        return FoodResponse(
            id=food.id,
            name=food.name,
            brand=food.brand,
            image_url=food.image_url,
            serving_size=food.serving_size,
            serving_unit=food.serving_unit,
            calories_per_serving=food.calories_per_serving,
            carbohydrates=food.carbohydrates,
            protein=food.protein,
            fat=food.fat,
            fiber=food.fiber,
            sugar=food.sugar,
            category=food.category,
            is_custom=bool(food.is_custom),
            created_at=food.created_at,
        )

    async def create_food(
        self, db: AsyncSession, food_data: FoodCreate, user_id: int | None = None
    ) -> FoodResponse:
        """创建食物

        Args:
            db: 数据库会话
            food_data: 食物数据
            user_id: 用户 ID（自定义食物）

        Returns:
            创建的食物响应
        """
        food = Food(
            name=food_data.name,
            brand=food_data.brand,
            image_url=food_data.image_url,
            serving_size=food_data.serving_size,
            serving_unit=food_data.serving_unit,
            calories_per_serving=food_data.calories_per_serving,
            carbohydrates=food_data.carbohydrates,
            protein=food_data.protein,
            fat=food_data.fat,
            fiber=food_data.fiber,
            sugar=food_data.sugar,
            category=food_data.category,
            is_custom=1 if user_id else 0,
            user_id=user_id,
            created_at=datetime.now().isoformat(),
        )

        db.add(food)
        await db.flush()
        await db.refresh(food)

        return FoodResponse(
            id=food.id,
            name=food.name,
            brand=food.brand,
            image_url=food.image_url,
            serving_size=food.serving_size,
            serving_unit=food.serving_unit,
            calories_per_serving=food.calories_per_serving,
            carbohydrates=food.carbohydrates,
            protein=food.protein,
            fat=food.fat,
            fiber=food.fiber,
            sugar=food.sugar,
            category=food.category,
            is_custom=bool(food.is_custom),
            created_at=food.created_at,
        )

    async def update_food(
        self, db: AsyncSession, food_id: int, food_data: FoodUpdate
    ) -> FoodResponse | None:
        """更新食物

        Args:
            db: 数据库会话
            food_id: 食物 ID
            food_data: 更新数据

        Returns:
            更新后的食物响应或 None
        """
        result = await db.execute(select(Food).where(Food.id == food_id))
        food = result.scalar_one_or_none()

        if food is None:
            return None

        # 更新字段
        update_data = food_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(food, field, value)
        await db.flush()
        await db.refresh(food)

        return FoodResponse(
            id=food.id,
            name=food.name,
            brand=food.brand,
            image_url=food.image_url,
            serving_size=food.serving_size,
            serving_unit=food.serving_unit,
            calories_per_serving=food.calories_per_serving,
            carbohydrates=food.carbohydrates,
            protein=food.protein,
            fat=food.fat,
            fiber=food.fiber,
            sugar=food.sugar,
            category=food.category,
            is_custom=bool(food.is_custom),
            created_at=food.created_at,
        )

    async def delete_food(self, db: AsyncSession, food_id: int) -> bool:
        """删除食物

        Args:
            db: 数据库会话
            food_id: 食物 ID

        Returns:
            是否删除成功
        """
        result = await db.execute(select(Food).where(Food.id == food_id))
        food = result.scalar_one_or_none()

        if food is None:
            return False

        await db.delete(food)
        return True


# 全局服务实例
food_service = FoodService()
