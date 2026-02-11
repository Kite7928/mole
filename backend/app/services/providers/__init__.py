"""
AI提供商模块
提供统一的AI提供商接口和实现
"""

from enum import Enum
from typing import Dict, Any, List
from datetime import datetime


class AIProvider(str, Enum):
    """AI提供商枚举"""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    CLAUDE = "claude"
    GEMINI = "gemini"
    QWEN = "qwen"
    MOONSHOT = "moonshot"
    OLLAMA = "ollama"
    VOLCENGINE = "volcengine"
    ALIBABA_BAILIAN = "alibaba_bailian"
    SILICONFLOW = "siliconflow"
    OPENROUTER = "openrouter"
    ZHIPU = "zhipu"


class RotationStrategy(str, Enum):
    """轮询策略枚举"""
    SEQUENTIAL = "sequential"
    RANDOM = "random"


class TokenUsage:
    """Token使用量统计"""
    def __init__(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0
    ):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens

    def to_dict(self) -> Dict[str, int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens
        }


class AIResponse:
    """AI响应结果"""
    def __init__(
        self,
        content: str,
        provider: AIProvider,
        model: str,
        token_usage: TokenUsage,
        finish_reason: str = "stop",
        metadata: Dict[str, Any] | None = None
    ):
        self.content = content
        self.provider = provider
        self.model = model
        self.token_usage = token_usage
        self.finish_reason = finish_reason
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "provider": self.provider.value,
            "model": self.model,
            "token_usage": self.token_usage.to_dict(),
            "finish_reason": self.finish_reason,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


# 导出所有 provider 实现
from .base import BaseAIProvider
from .openai_provider import OpenAICompatibleProvider
from .claude_provider import ClaudeProvider
from .gemini_provider import GeminiProvider

__all__ = [
    "AIProvider",
    "RotationStrategy",
    "TokenUsage",
    "AIResponse",
    "BaseAIProvider",
    "OpenAICompatibleProvider",
    "ClaudeProvider",
    "GeminiProvider",
]