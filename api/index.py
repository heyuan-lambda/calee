"""
Vercel serverless function entry point for CalEE
"""
import os
import sys

# 获取项目根目录
root_dir = os.path.dirname(os.path.dirname(__file__))
backend_dir = os.path.join(root_dir, 'backend')

# 添加 backend 目录到 Python 路径
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 设置环境变量（必须在导入前设置）
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///tmp/calee.db')
os.environ.setdefault('DASHSCOPE_API_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
os.environ.setdefault('UPLOAD_DIR', '/tmp/uploads')
os.environ.setdefault('ALLOW_ORIGINS', '*')

# 确保上传目录存在
os.makedirs('/tmp/uploads', exist_ok=True)

# 导入应用
try:
    from app.main import app
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except Exception as e:
    # 如果导入失败，返回一个简单的错误处理函数
    def handler(event, context):
        return {
            'statusCode': 500,
            'body': f'Import error: {str(e)}'
        }
