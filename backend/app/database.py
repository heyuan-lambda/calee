"""数据库连接管理"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings


# 创建异步引擎
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

# 创建异步 Session 工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（依赖注入）"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（上下文管理器）"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """初始化数据库表和种子数据"""
    from app.models import Base  # noqa: F401
    from app.seeds import seed_foods, init_default_user

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 初始化种子数据
    async with async_session_maker() as session:
        await init_default_user(session)
        await seed_foods(session)
