from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import secrets
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _default_database_url() -> str:
    """构建默认数据库 URL（可被环境变量覆盖）"""
    return f"sqlite+aiosqlite:///{(BACKEND_ROOT / 'app.db').as_posix()}"


def _default_upload_dir() -> str:
    """构建默认上传目录（可被环境变量覆盖）"""
    return (BACKEND_ROOT / "uploads").as_posix()


class Settings(BaseSettings):
    """应用配置类 - 个人商用简化版"""

    # Application
    APP_NAME: str = "AI公众号写作助手"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database (使用绝对路径，避免工作目录问题)
    DATABASE_URL: str = _default_database_url()

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

    # Image Generation - Tongyi Wanxiang (阿里通义万相)
    TONGYI_WANXIANG_API_KEY: Optional[str] = None
    TONGYI_WANXIANG_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    TONGYI_WANXIANG_MODEL: str = "wanx-v1"

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
    RSS_FETCH_RETRIES: int = 2
    RSS_FETCH_RETRY_DELAY: float = 0.8
    RSSHUB_BASE_URL: str = "https://rsshub.app"

    # File Storage
    UPLOAD_DIR: str = _default_upload_dir()
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

    # Mock/Fallback Configuration
    # 生产环境建议关闭，避免隐式返回模拟数据误导业务判断
    ALLOW_MOCK_FALLBACK: bool = False

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """兼容 JSON 数组与逗号分隔字符串两种 CORS 配置格式"""
        if isinstance(v, str):
            value = v.strip()
            if not value:
                return ["http://localhost:3000", "http://127.0.0.1:3000"]

            if value.startswith("[") and value.endswith("]"):
                import json
                return json.loads(value)

            return [origin.strip() for origin in value.split(",") if origin.strip()]

        return v

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v):
        """将 sqlite 相对路径标准化为项目根目录绝对路径"""
        if not isinstance(v, str):
            return v

        if not v.startswith("sqlite"):
            return v

        if ":///" not in v:
            return v

        schema, path_part = v.split(":///", 1)
        if not path_part or path_part == ":memory:":
            return v

        db_path = Path(path_part)
        if not db_path.is_absolute():
            db_path = (PROJECT_ROOT / db_path).resolve()
            return f"{schema}:///{db_path.as_posix()}"

        return v

    @field_validator("UPLOAD_DIR", mode="before")
    @classmethod
    def normalize_upload_dir(cls, v):
        """将上传目录标准化为项目根目录绝对路径"""
        if not v:
            return _default_upload_dir()

        upload_path = Path(str(v))
        if not upload_path.is_absolute():
            upload_path = (PROJECT_ROOT / upload_path).resolve()

        return upload_path.as_posix()

    @field_validator("RSSHUB_BASE_URL", mode="before")
    @classmethod
    def normalize_rsshub_base_url(cls, v):
        """标准化 RSSHub 基础地址，移除尾部斜杠。"""
        if v is None:
            return ""

        value = str(v).strip()
        if not value:
            return ""

        return value.rstrip("/")

    class Config:
        env_file = [str(PROJECT_ROOT / ".env"), str(BACKEND_ROOT / ".env")]
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# Create global settings instance
# 注意：pydantic_settings 会自动优先使用环境变量，无需手动删除
settings = Settings()
