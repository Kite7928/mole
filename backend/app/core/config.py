from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI公众号自动写作助手 Pro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # JWT Authentication
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list = ["*"]  # Allow all origins for development

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/wechat_ai_writer"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50

    # AI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.7

    # DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Anthropic Claude
    CLAUDE_API_KEY: Optional[str] = None
    CLAUDE_BASE_URL: str = "https://api.anthropic.com/v1"
    CLAUDE_MODEL: str = "claude-3-opus-20240229"

    # Google Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"

    # Ollama (本地部署)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"

    # 火山引擎 (字节跳动)
    VOLCENGINE_API_KEY: Optional[str] = None
    VOLCENGINE_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"
    VOLCENGINE_MODEL: str = "ep-20240110134838-xxxxx"

    # 阿里云百炼
    ALIBABA_BAILIAN_API_KEY: Optional[str] = None
    ALIBABA_BAILIAN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    ALIBABA_BAILIAN_MODEL: str = "qwen-max"

    # Moonshot Kimi
    MOONSHOT_API_KEY: Optional[str] = None
    MOONSHOT_BASE_URL: str = "https://api.moonshot.cn/v1"
    MOONSHOT_MODEL: str = "moonshot-v1-8k"

    # 硅基流动
    SILICONFLOW_API_KEY: Optional[str] = None
    SILICONFLOW_BASE_URL: str = "https://api.siliconflow.cn/v1"
    SILICONFLOW_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"

    # OpenRouter
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "openai/gpt-4-turbo"

    # AI轮询策略配置
    AI_ROTATION_STRATEGY: str = "sequential"  # "sequential" or "random"
    AI_ENABLED_PROVIDERS: list = [
        "openai",
        "deepseek",
        "claude",
        "gemini",
        "qwen",
        "moonshot",
        "ollama",
        "volcengine",
        "alibaba_bailian",
        "siliconflow",
        "openrouter"
    ]

    # Image Generation API (图片生成API)
    DALL_E_API_KEY: Optional[str] = None
    DALL_E_MODEL: str = "dall-e-3"
    DALL_E_SIZE: str = "1024x1024"
    DALL_E_QUALITY: str = "standard"

    MIDJOURNEY_API_KEY: Optional[str] = None
    MIDJOURNEY_BASE_URL: str = "https://api.midjourney.com/v1"

    STABLE_DIFFUSION_API_KEY: Optional[str] = None
    STABLE_DIFFUSION_BASE_URL: str = "https://api.stability.ai/v1"
    STABLE_DIFFUSION_MODEL: str = "stable-diffusion-xl-1024-v1-0"

    # Data Analysis API (数据分析API)
    BAIDU_INDEX_API_KEY: Optional[str] = None
    BAIDU_INDEX_SECRET: Optional[str] = None

    WECHAT_INDEX_API_KEY: Optional[str] = None
    WECHAT_INDEX_SECRET: Optional[str] = None

    WEIBO_API_KEY: Optional[str] = None
    WEIBO_API_SECRET: Optional[str] = None
    WEIBO_REDIRECT_URI: Optional[str] = None

    # GitHub API
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_API_BASE_URL: str = "https://api.github.com"
    GITHUB_WEBHOOK_SECRET: Optional[str] = None
    GITHUB_REPO_OWNER: Optional[str] = None
    GITHUB_REPO_NAME: Optional[str] = None

    # WeChat Configuration
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    WECHAT_TOKEN_CACHE_TTL: int = 7200  # 2 hours

    # Image Processing
    IMAGE_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    IMAGE_ALLOWED_FORMATS: list = ["jpg", "jpeg", "png", "webp"]
    COVER_IMAGE_WIDTH: int = 900
    COVER_IMAGE_HEIGHT: int = 500
    COVER_IMAGE_MIN_WIDTH: int = 500
    COVER_IMAGE_MIN_HEIGHT: int = 300

    # Task Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    TASK_TIMEOUT: int = 3600  # 1 hour
    TASK_MAX_RETRIES: int = 3

    # Data Sources
    NEWS_SOURCES: list = [
        "ithome",
        "36kr",
        "baidu",
        "zhihu",
        "weibo"
    ]
    NEWS_REFRESH_INTERVAL: int = 1800  # 30 minutes

    # File Storage
    UPLOAD_DIR: str = "uploads"
    TEMP_DIR: str = "temp"
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024  # 20MB

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 10

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    SENTRY_DSN: Optional[str] = None

    # Security
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# Create global settings instance
settings = Settings()