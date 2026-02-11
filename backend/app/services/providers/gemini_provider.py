"""
Gemini 提供商实现
"""

from typing import List, Dict, Any, AsyncGenerator
import httpx
import tiktoken
from ...core.config import settings
from ...core.logger import logger
from . import AIProvider, AIResponse, TokenUsage
from .base import BaseAIProvider


class GeminiProvider(BaseAIProvider):
    """Google Gemini AI提供商"""

    def __init__(
        self,
        api_key: str | None,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        default_model: str = "gemini-2.0-flash-exp-image-generation"
    ):
        super().__init__(AIProvider.GEMINI, api_key, base_url)
        self.default_model = default_model
        self._http_client = httpx.AsyncClient(timeout=60.0)

    @property
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        return self.api_key is not None

    def _count_tokens(self, text: str) -> int:
        """估算Token数量"""
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception:
            # 粗略估算
            return len(text) // 3

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AIResponse:
        """生成AI响应"""
        if not self.api_key:
            raise RuntimeError("Gemini API key 未配置")

        # 转换消息格式
        contents = [{"parts": [{"text": msg["content"]}]} for msg in messages]

        response = await self._http_client.post(
            f"{self.base_url}/models/{model}:generateContent",
            params={"key": self.api_key},
            json={
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens
                }
            }
        )

        response.raise_for_status()
        data = response.json()

        content = data["candidates"][0]["content"]["parts"][0]["text"] if data.get("candidates") else ""

        # Gemini不返回精确token数，使用估算
        prompt_text = " ".join([msg["content"] for msg in messages])
        prompt_tokens = self._count_tokens(prompt_text)
        completion_tokens = self._count_tokens(content)

        token_usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens
        )

        return AIResponse(
            content=content,
            provider=AIProvider.GEMINI,
            model=model,
            token_usage=token_usage,
            finish_reason="stop"
        )

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AsyncGenerator[str, None]:
        """流式生成AI响应 - Gemini暂不支持，模拟流式"""
        response = await self.generate(messages, model, temperature, max_tokens)
        for char in response.content:
            yield char

    def get_default_model(self) -> str:
        """获取默认模型"""
        return self.default_model

    async def close(self):
        """关闭连接"""
        await self._http_client.aclose()