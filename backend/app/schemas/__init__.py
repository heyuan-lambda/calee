"""Pydantic Schema 定义"""
from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """统一 API 响应格式"""

    success: bool = True
    message: str | None = None
    data: dict | list | None = None


# ==================== Food Schema ====================


class FoodBase(BaseModel):
    """食物基础 Schema"""

    name: str = Field(..., min_length=1, max_length=100, description="食物名称")
    brand: str | None = Field(None, max_length=100, description="品牌")
    serving_size: float = Field(100, gt=0, description="份量大小")
    serving_unit: str = Field("g", max_length=20, description="份量单位")
    calories_per_serving: float = Field(..., ge=0, description="每份热量（卡路里）")
    carbohydrates: float = Field(0, ge=0, description="碳水化合物（克）")
    protein: float = Field(0, ge=0, description="蛋白质（克）")
    fat: float = Field(0, ge=0, description="脂肪（克）")
    fiber: float = Field(0, ge=0, description="纤维（克）")
    sugar: float = Field(0, ge=0, description="糖（克）")
    category: str = Field("other", description="食物分类")


class FoodCreate(FoodBase):
    """创建食物请求"""

    image_url: str | None = None


class FoodUpdate(BaseModel):
    """更新食物请求"""

    name: str | None = None
    brand: str | None = None
    serving_size: float | None = None
    serving_unit: str | None = None
    calories_per_serving: float | None = None
    carbohydrates: float | None = None
    protein: float | None = None
    fat: float | None = None
    fiber: float | None = None
    sugar: float | None = None
    category: str | None = None
    image_url: str | None = None


class FoodResponse(FoodBase):
    """食物响应"""

    id: int
    image_url: str | None
    is_custom: bool
    created_at: str

    class Config:
        from_attributes = True


class FoodListItem(BaseModel):
    """食物列表项"""

    id: int
    name: str
    brand: str | None
    image_url: str | None
    calories_per_serving: float
    category: str
    is_custom: bool

    class Config:
        from_attributes = True


# ==================== Meal Schema ====================


class MealEntryBase(BaseModel):
    """餐食条目基础 Schema"""

    food_id: int
    servings: float = Field(1.0, gt=0, description="份数")
    notes: str | None = None
    image_url: str | None = None


class MealEntryCreate(MealEntryBase):
    """创建餐食条目"""

    pass


class MealEntryResponse(MealEntryBase):
    """餐食条目响应"""

    id: int
    food: FoodResponse
    calories: float  # 计算后的热量
    created_at: str

    class Config:
        from_attributes = True


class MealCreate(BaseModel):
    """创建餐食请求"""

    meal_type: str = Field(..., pattern="^(breakfast|lunch|dinner|snack)$")
    date: str | None = None  # YYYY-MM-DD 格式
    entries: list[MealEntryCreate] = Field(..., min_length=1, max_length=50)


class MealResponse(BaseModel):
    """餐食响应"""

    id: int
    meal_type: str
    date: str
    entries: list[MealEntryResponse]
    total_calories: float
    created_at: str

    class Config:
        from_attributes = True


# ==================== Dashboard Schema ====================


class MacroNutrients(BaseModel):
    """宏量营养素"""

    carbohydrates: float = 0
    protein: float = 0
    fat: float = 0


class DailySummary(BaseModel):
    """每日摘要"""

    date: str
    total_calories: float
    calorie_goal: int
    calories_remaining: float
    calories_used_percentage: float
    macros: MacroNutrients
    meals: dict[str, list[MealResponse]]  # 按餐食类型分组


class UserGoalUpdate(BaseModel):
    """用户目标更新"""

    daily_calorie_goal: int = Field(..., ge=500, le=5000, description="每日卡路里目标")


# ==================== Image Recognition Schema ====================


class ImageRecognitionRequest(BaseModel):
    """图像识别请求"""

    image_base64: str | None = None  # Base64 编码的图片


class RecognizedFood(BaseModel):
    """识别出的食物"""

    name: str
    confidence: float
    estimated_calories: float
    estimated_macros: MacroNutrients
    suggested_servings: float


class ImageRecognitionResponse(BaseModel):
    """图像识别响应"""

    success: bool
    foods: list[RecognizedFood]
    error: str | None = None


# ==================== User Schema ====================


class UserCreate(BaseModel):
    """创建用户请求"""

    device_id: str
    username: str | None = None
    avatar_url: str | None = None


class UserResponse(BaseModel):
    """用户响应"""

    id: int
    device_id: str
    username: str | None
    avatar_url: str | None
    daily_calorie_goal: int
    created_at: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """更新用户请求"""

    username: str | None = None
    avatar_url: str | None = None
