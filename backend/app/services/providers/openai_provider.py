"""
OpenAI 兼容提供商实现
支持 OpenAI、DeepSeek、Moonshot、Qwen 等
"""

from typing import List, Dict, Any, AsyncGenerator
from openai import AsyncOpenAI
from ...core.logger import logger
from . import AIProvider, AIResponse, TokenUsage
from .base import BaseAIProvider


class OpenAICompatibleProvider(BaseAIProvider):
    """OpenAI 兼容API提供商"""

    def __init__(
        self,
        provider_type: AIProvider,
        api_key: str | None,
        base_url: str,
        default_model: str = "gpt-3.5-turbo",
        needs_api_key: bool = True
    ):
        super().__init__(provider_type, api_key, base_url)
        self.default_model = default_model
        self.needs_api_key = needs_api_key
        self._init_client()

    def _init_client(self):
        """初始化客户端"""
        if not self.needs_api_key or self.api_key:
            try:
                import httpx
                # 设置更长的超时时间（连接30秒，读取10分钟），确保长内容生成不会中断
                timeout = httpx.Timeout(600.0, connect=30.0, read=600.0, write=60.0)
                http_client = httpx.AsyncClient(timeout=timeout, trust_env=False)
                self._client = AsyncOpenAI(
                    api_key=self.api_key or "dummy",
                    base_url=self.base_url,
                    http_client=http_client,
                    max_retries=2
                )
                logger.info(f"{self.provider_type.value} 提供商初始化成功（超时: 600秒）")
            except Exception as e:
                logger.error(f"{self.provider_type.value} 提供商初始化失败: {e}")
                self._client = None

    @property
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        if self.needs_api_key and not self.api_key:
            return False
        return self._client is not None

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AIResponse:
        """生成AI响应"""
        if not self._client:
            raise RuntimeError(f"{self.provider_type.value} 客户端未初始化")

        response = await self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        content = response.choices[0].message.content or ""
        token_usage = TokenUsage(
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0
        )

        return AIResponse(
            content=content,
            provider=self.provider_type,
            model=model,
            token_usage=token_usage,
            finish_reason=response.choices[0].finish_reason or "stop"
        )

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AsyncGenerator[str, None]:
        """流式生成AI响应"""
        if not self._client:
            raise RuntimeError(f"{self.provider_type.value} 客户端未初始化")

        stream = await self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def get_default_model(self) -> str:
        """获取默认模型"""
        return self.default_model
