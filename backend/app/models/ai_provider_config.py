"""
AI 提供商配置模型
支持多个 AI 提供商的配置存储
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from ..core.database import Base


class AIProviderConfig(Base):
    """AI 提供商配置模型"""
    __tablename__ = "ai_provider_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 提供商标识
    provider = Column(String(50), unique=True, index=True, nullable=False)  # openai, deepseek, claude, gemini, qwen, moonshot
    
    # 是否启用
    is_enabled = Column(Boolean, default=True)
    
    # API 配置
    api_key = Column(String(500), nullable=True)  # API密钥
    base_url = Column(String(500), nullable=True)  # API基础URL
    model = Column(String(100), nullable=True)  # 模型名称
    
    # 高级配置（JSON格式存储额外参数）
    extra_config = Column(Text, nullable=True)
    
    # 是否为默认提供商
    is_default = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AIProviderConfig(id={self.id}, provider={self.provider}, is_enabled={self.is_enabled})>"
    
    def to_dict(self, hide_api_key: bool = True) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "provider": self.provider,
            "is_enabled": self.is_enabled,
            "api_key": "******" if hide_api_key and self.api_key else self.api_key,
            "has_api_key": bool(self.api_key),
            "base_url": self.base_url,
            "model": self.model,
            "extra_config": self.extra_config,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# 支持的 AI 提供商默认配置
DEFAULT_AI_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4-turbo-preview",
        "description": "OpenAI GPT-4 模型",
        "icon": "🤖"
    },
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "description": "DeepSeek 对话模型",
        "icon": "🐋"
    },
    "claude": {
        "name": "Claude",
        "base_url": "https://api.anthropic.com/v1",
        "model": "claude-3-opus-20240229",
        "description": "Anthropic Claude 模型",
        "icon": "🧠"
    },
    "gemini": {
        "name": "Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "model": "gemini-pro",
        "description": "Google Gemini 模型",
        "icon": "💎"
    },
    "qwen": {
        "name": "通义千问",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-max",
        "description": "阿里通义千问模型",
        "icon": "🌐"
    },
    "moonshot": {
        "name": "Moonshot",
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-8k",
        "description": "月之暗面 Moonshot 模型",
        "icon": "🌙"
    },
    "zhipu": {
        "name": "智谱 AI",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
        "description": "智谱 AI GLM-4 模型",
        "icon": "🔮"
    }
}
