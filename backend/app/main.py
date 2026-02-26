"""FastAPI 主应用"""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.config import settings
from app.database import init_db
from app.api import foods, meals, dashboard, upload


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时的清理工作


# 创建 FastAPI 应用
app = FastAPI(
    title="CalEE API",
    description="饮食热量追踪应用 API",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置模板目录
frontend_dir = Path(__file__).parent.parent.parent / "frontend"
templates = Jinja2Templates(directory=str(frontend_dir / "templates"))

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")
app.mount("/static", StaticFiles(directory=str(frontend_dir / "static")), name="static")

# 注册 API 路由
app.include_router(foods.router, prefix="/api/v1")
app.include_router(meals.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")


# ==================== 页面路由 ====================

@app.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """仪表板页面"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """搜索页面"""
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """上传页面"""
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/foods/{food_id}", response_class=HTMLResponse)
async def food_detail_page(request: Request, food_id: int):
    """食物详情页面"""
    return templates.TemplateResponse("food_detail.html", {"request": request})


@app.get("/progress", response_class=HTMLResponse)
async def progress_page(request: Request):
    """进度页面"""
    return templates.TemplateResponse("progress.html", {"request": request})


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """个人资料页面"""
    return templates.TemplateResponse("profile.html", {"request": request})


# ==================== API 端点 ====================

@app.get("/health")
async def health_check() -> dict:
    """健康检查"""
    return {"status": "healthy", "service": "CalEE API"}


@app.get("/api")
async def api_root() -> dict:
    """API 根路径"""
    return {
        "message": "CalEE API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
