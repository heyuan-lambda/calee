"""数据库模型"""
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """ORM 基类"""

    pass


class User(Base):
    """用户模型（简化版，仅用于本地存储用户偏好）"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    daily_calorie_goal: Mapped[int] = mapped_column(Integer, default=1200)
    created_at: Mapped[str] = mapped_column(DateTime, server_default="datetime('now')")
    updated_at: Mapped[str] = mapped_column(DateTime, server_default="datetime('now')")

    # 关系
    meals: Mapped[list["Meal"]] = relationship(
        "Meal", back_populates="user", cascade="all, delete-orphan"
    )
    custom_foods: Mapped[list["Food"]] = relationship(
        "Food", back_populates="creator", cascade="all, delete-orphan"
    )


class Food(Base):
    """食物模型"""

    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    serving_size: Mapped[float] = mapped_column(Float, default=100)
    serving_unit: Mapped[str] = mapped_column(String(20), default="g")
    calories_per_serving: Mapped[float] = mapped_column(Float, nullable=False)
    carbohydrates: Mapped[float] = mapped_column(Float, default=0)
    protein: Mapped[float] = mapped_column(Float, default=0)
    fat: Mapped[float] = mapped_column(Float, default=0)
    fiber: Mapped[float] = mapped_column(Float, default=0)
    sugar: Mapped[float] = mapped_column(Float, default=0)
    category: Mapped[str] = mapped_column(
        Enum("main", "side", "drink", "snack", "fruit", "vegetable", "other", name="food_category"),
        default="other",
    )
    is_custom: Mapped[bool] = mapped_column(Integer, default=0)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[str] = mapped_column(DateTime, server_default="datetime('now')")

    # 关系
    creator: Mapped["User"] = relationship("User", back_populates="custom_foods")


class Meal(Base):
    """餐食记录模型"""

    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    meal_type: Mapped[str] = mapped_column(
        Enum("breakfast", "lunch", "dinner", "snack", name="meal_type"),
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(DateTime, server_default="datetime('now')")
    updated_at: Mapped[str] = mapped_column(DateTime, server_default="datetime('now')")

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="meals")
    entries: Mapped[list["MealEntry"]] = relationship(
        "MealEntry", back_populates="meal", cascade="all, delete-orphan"
    )


class MealEntry(Base):
    """餐食条目模型（关联表）"""

    __tablename__ = "meal_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meal_id: Mapped[int] = mapped_column(Integer, ForeignKey("meals.id"), nullable=False)
    food_id: Mapped[int] = mapped_column(Integer, ForeignKey("foods.id"), nullable=False)
    servings: Mapped[float] = mapped_column(Float, default=1.0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)  # 用户上传的图片
    created_at: Mapped[str] = mapped_column(DateTime, server_default="datetime('now')")

    # 关系
    meal: Mapped["Meal"] = relationship("Meal", back_populates="entries")
    food: Mapped["Food"] = relationship("Food")
