"""
简单的图像识别代理 - 唯一的后端功能
"""
import json
import base64
import os
from http import HTTPStatus

def handler(event, context):
    """Vercel serverless function handler"""
    try:
        # 只允许 POST 请求
        if event.get('httpMethod') != 'POST':
            return {
                'statusCode': 405,
                'body': json.dumps({'error': 'Method not allowed'})
            }

        # 解析请求体
        body = event.get('body', '')
        if isinstance(body, str):
            import urllib.parse
            body = urllib.parse.parse_qs(body)

        # 获取图片数据
        image_base64 = body.get('image', [None])[0]
        if not image_base64:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No image data'})
            }

        # 调用阿里云 API
        import httpx
        api_key = os.environ.get('DASHSCOPE_API_KEY')
        api_url = os.environ.get('DASHSCOPE_API_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }

        payload = {
            'model': 'qwen-vl-plus',
            'messages': [{
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {'url': f'data:image/jpeg;base64,{image_base64}'}
                    },
                    {
                        'type': 'text',
                        'text': """分析这张食物图片，返回 JSON 格式：
{
  "foods": [
    {
      "name": "食物名称",
      "confidence": 0.95,
      "estimated_calories": 200,
      "estimated_macros": {"carbohydrates": 45, "protein": 4, "fat": 0.5},
      "suggested_servings": 1.0
    }
  ]
}
只返回 JSON，不要其他文字。"""
                    }
                ]
            }]
        }

        response = httpx.post(api_url, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        result = response.json()

        # 解析结果
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')

        # 尝试提取 JSON
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            if 'foods' in data:
                foods = data['foods']
            else:
                foods = [data] if 'name' in data else []
        else:
            foods = []

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'foods': foods
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
