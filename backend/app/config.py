"""应用配置管理"""
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 数据库
    database_url: str = Field(
        default="sqlite+aiosqlite:///./calee.db",
        description="数据库连接URL",
    )

    # API 配置
    dashscope_api_key: str = Field(
        default="",
        description="阿里云 DashScope API Key",
    )
    dashscope_api_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="阿里云 DashScope API URL",
    )

    # 应用设置
    daily_calorie_goal: int = Field(
        default=1200,
        description="每日卡路里目标",
    )
    allow_origins: str = Field(
        default="*",
        description="允许的跨域来源",
    )

    # 上传设置
    max_upload_size: int = Field(
        default=5242880,  # 5MB
        description="最大上传文件大小（字节）",
    )
    upload_dir: Path = Field(
        default=Path("./uploads"),
        description="上传文件存储目录",
    )

    @property
    def allow_origins_list(self) -> list[str]:
        """转换跨域来源为列表"""
        return [origin.strip() for origin in self.allow_origins.split(",")]


# 全局配置实例
settings = Settings()
