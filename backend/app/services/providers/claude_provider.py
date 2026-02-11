"""
Claude 提供商实现
"""

from typing import List, Dict, Any, AsyncGenerator
import anthropic
from ...core.logger import logger
from . import AIProvider, AIResponse, TokenUsage
from .base import BaseAIProvider


class ClaudeProvider(BaseAIProvider):
    """Claude AI提供商"""

    def __init__(self, api_key: str | None, base_url: str, default_model: str = "claude-3-opus-20240229"):
        super().__init__(AIProvider.CLAUDE, api_key, base_url)
        self.default_model = default_model
        self._init_client()

    def _init_client(self):
        """初始化客户端"""
        if self.api_key:
            try:
                self._client = anthropic.AsyncAnthropic(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                logger.info("Claude 提供商初始化成功")
            except Exception as e:
                logger.error(f"Claude 提供商初始化失败: {e}")
                self._client = None

    @property
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        return self.api_key is not None and self._client is not None

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AIResponse:
        """生成AI响应"""
        if not self._client:
            raise RuntimeError("Claude 客户端未初始化")

        # 转换消息格式
        system_message = None
        user_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append({"role": msg["role"], "content": msg["content"]})

        response = await self._client.messages.create(
            model=model,
            system=system_message,
            messages=user_messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        content = response.content[0].text if response.content else ""
        token_usage = TokenUsage(
            prompt_tokens=response.usage.input_tokens if response.usage else 0,
            completion_tokens=response.usage.output_tokens if response.usage else 0,
            total_tokens=(response.usage.input_tokens + response.usage.output_tokens) if response.usage else 0
        )

        return AIResponse(
            content=content,
            provider=AIProvider.CLAUDE,
            model=model,
            token_usage=token_usage,
            finish_reason=response.stop_reason or "stop"
        )

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AsyncGenerator[str, None]:
        """流式生成AI响应 - Claude暂不支持，模拟流式"""
        # Claude不直接支持流式，先生成完整响应
        response = await self.generate(messages, model, temperature, max_tokens)
        # 逐字返回模拟流式
        for char in response.content:
            yield char

    def get_default_model(self) -> str:
        """获取默认模型"""
        return self.default_model