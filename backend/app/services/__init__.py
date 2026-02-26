"""图像识别服务 - 调用阿里云 Qwen3-VL-Plus API"""
import base64
import json
import re
from typing import Any

import httpx

from app.config import settings
from app.schemas import ImageRecognitionResponse, MacroNutrients, RecognizedFood


class ImageRecognitionService:
    """图像识别服务"""

    def __init__(self) -> None:
        self.api_key = settings.dashscope_api_key
        self.api_url = settings.dashscope_api_url

    async def recognize_food(self, image_data: bytes, image_format: str = "jpeg") -> ImageRecognitionResponse:
        """识别食物图片

        Args:
            image_data: 图片二进制数据
            image_format: 图片格式（jpeg, png等）

        Returns:
            ImageRecognitionResponse: 识别结果
        """
        # 编码图片为 base64
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # 构造请求体
        payload = {
            "model": "qwen-vl-plus",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/{image_format};base64,{image_base64}"},
                        },
                        {
                            "type": "text",
                            "text": """请分析这张图片中的食物，返回 JSON 格式的结果。

请识别图片中的所有食物，并估算每样食物的：
1. 名称（中文）
2. 置信度（0-1之间的浮点数）
3. 估算热量（卡路里）
4. 宏量营养素（碳水化合物、蛋白质、脂肪，单位：克）

返回格式示例：
{
  "foods": [
    {
      "name": "白米饭",
      "confidence": 0.95,
      "estimated_calories": 200,
      "estimated_macros": {
        "carbohydrates": 45,
        "protein": 4,
        "fat": 0.5
      },
      "suggested_servings": 1.0
    }
  ]
}

请只返回 JSON，不要有其他文字说明。""",
                        },
                    ],
                }
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

            # 解析响应
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            # 尝试从内容中提取 JSON
            foods_data = self._extract_json_from_content(content)

            foods = []
            for food_data in foods_data:
                macros_data = food_data.get("estimated_macros", {})
                foods.append(
                    RecognizedFood(
                        name=food_data.get("name", "未知食物"),
                        confidence=food_data.get("confidence", 0.5),
                        estimated_calories=food_data.get("estimated_calories", 0),
                        estimated_macros=MacroNutrients(
                            carbohydrates=macros_data.get("carbohydrates", 0),
                            protein=macros_data.get("protein", 0),
                            fat=macros_data.get("fat", 0),
                        ),
                        suggested_servings=food_data.get("suggested_servings", 1.0),
                    )
                )

            return ImageRecognitionResponse(success=True, foods=foods)

        except httpx.HTTPError as e:
            return ImageRecognitionResponse(
                success=False, foods=[], error=f"API 请求失败: {e!s}"
            )
        except Exception as e:
            return ImageRecognitionResponse(
                success=False, foods=[], error=f"识别失败: {e!s}"
            )

    def _extract_json_from_content(self, content: str) -> list[dict[str, Any]]:
        """从内容中提取 JSON 数据

        Args:
            content: API 返回的内容

        Returns:
            解析后的食物列表
        """
        # 尝试直接解析
        try:
            data = json.loads(content)
            if "foods" in data:
                return data["foods"]
            return [data] if "name" in data else []
        except json.JSONDecodeError:
            pass

        # 尝试提取 JSON 代码块
        json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                if "foods" in data:
                    return data["foods"]
                return [data] if "name" in data else []
            except json.JSONDecodeError:
                pass

        # 尝试查找任何 JSON 对象
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                if "foods" in data:
                    return data["foods"]
                return [data] if "name" in data else []
            except json.JSONDecodeError:
                pass

        return []


# 全局服务实例
image_recognition_service = ImageRecognitionService()
