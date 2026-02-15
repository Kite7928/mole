"""
AI提供商抽象基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator
import inspect
from . import AIProvider, AIResponse


class BaseAIProvider(ABC):
    """AI提供商抽象基类"""

    def __init__(self, provider_type: AIProvider, api_key: str | None, base_url: str):
        self.provider_type = provider_type
        self.api_key = api_key
        self.base_url = base_url
        self._client = None

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AIResponse:
        """生成AI响应"""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AsyncGenerator[str, None]:
        """流式生成AI响应"""
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        """获取默认模型"""
        pass

    async def close(self):
        """关闭连接"""
        if self._client:
            close_func = getattr(self._client, "aclose", None)
            if close_func is None:
                close_func = getattr(self._client, "close", None)

            if close_func is None:
                return

            result = close_func()
            if inspect.isawaitable(result):
                await result
