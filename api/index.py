"""
Vercel serverless function entry point for CalEE

This file serves as the entry point for Vercel's Python runtime.
It wraps the FastAPI application to work with Vercel's serverless functions.
"""
import sys
import os

# 获取项目根目录
root_dir = os.path.dirname(os.path.dirname(__file__))
backend_dir = os.path.join(root_dir, 'backend')

# 添加 backend 目录到 Python 路径
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 环境变量设置
if 'DATABASE_URL' not in os.environ:
    # 使用 Vercel 的 tmp 目录存储数据库
    os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///tmp/calee.db'

if 'UPLOAD_DIR' not in os.environ:
    os.environ['UPLOAD_DIR'] = '/tmp/uploads'

# 确保上传目录存在
os.makedirs('/tmp/uploads', exist_ok=True)

# 导入 FastAPI 应用
from app.main import app

# Vercel Python Runtime 需要 ASGI 应用
# FastAPI app 本身就是 ASGI 应用，直接导出即可
handler = app
