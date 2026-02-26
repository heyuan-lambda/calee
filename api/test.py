"""
简单的测试函数，用于验证 Vercel Python 环境是否正常
"""
def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': '{"status": "ok", "message": "CalEE API is working"}'
    }
