from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置类 - 个人商用简化版"""

    # Application
    APP_NAME: str = "AI公众号写作助手"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list = ["*"]

    # Database (优先使用环境变量，适用于部署环境)
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    # AI Configuration - OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.7

    # AI Configuration - DeepSeek (可选)
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Image Generation - DALL-E
    DALL_E_API_KEY: Optional[str] = None
    DALL_E_BASE_URL: str = "https://api.openai.com/v1"
    DALL_E_MODEL: str = "dall-e-3"
    DALL_E_SIZE: str = "1024x1024"
    DALL_E_QUALITY: str = "standard"

    # Image Generation - Midjourney
    MIDJOURNEY_API_KEY: Optional[str] = None
    MIDJOURNEY_BASE_URL: str = "https://api.midjourney.com/v1"

    # Image Generation - Stable Diffusion
    STABLE_DIFFUSION_API_KEY: Optional[str] = None
    STABLE_DIFFUSION_BASE_URL: str = "https://api.stability.ai/v1"
    STABLE_DIFFUSION_MODEL: str = "stable-diffusion-xl-1024-v1-0"

    # Image Generation - Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    GEMINI_MODEL: str = "gemini-2.0-flash-exp-image-generation"

    # Image Generation - Cogview (Zhipu AI)
    COGVIEW_API_KEY: Optional[str] = None
    COGVIEW_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4/images/generations"
    COGVIEW_MODEL: str = "cogview-3-flash"

    # AI Configuration - Zhipu AI (智谱)
    ZHIPU_API_KEY: Optional[str] = None
    ZHIPU_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    ZHIPU_MODEL: str = "glm-4-flash"

    # WeChat Configuration
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    WECHAT_TOKEN_CACHE_TTL: int = 7200  # 2 hours

    # Image Processing
    IMAGE_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    IMAGE_ALLOWED_FORMATS: list = ["jpg", "jpeg", "png", "webp"]
    COVER_IMAGE_WIDTH: int = 900
    COVER_IMAGE_HEIGHT: int = 383

    # Data Sources
    NEWS_SOURCES: list = ["ithome", "36kr", "baidu"]
    NEWS_REFRESH_INTERVAL: int = 1800  # 30 minutes

    # File Storage
    UPLOAD_DIR: str = "uploads"
    TEMP_DIR: str = "temp"
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024  # 20MB

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5

    # Cache Configuration
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 1800  # 默认缓存30分钟
    CACHE_MAX_SIZE: int = 1000  # 最大缓存条目数

    # Database Pool Configuration
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# Create global settings instance
# 注意：pydantic_settings 会自动优先使用环境变量，无需手动删除
settings = Settings()