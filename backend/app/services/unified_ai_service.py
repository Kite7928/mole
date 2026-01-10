"""
统一AI模型服务
支持多个AI提供商，提供统一的调用接口、Token计算、日志记录、错误处理和轮询机制
"""

from typing import Optional, List, Dict, Any, AsyncGenerator
from enum import Enum
import random
import asyncio
from datetime import datetime
import tiktoken
import httpx
from openai import AsyncOpenAI
import anthropic
from ..core.config import settings
from ..core.logger import logger


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


class RotationStrategy(str, Enum):
    """轮询策略枚举"""
    SEQUENTIAL = "sequential"  # 顺序轮询
    RANDOM = "random"  # 随机轮询


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
        metadata: Optional[Dict[str, Any]] = None
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


class UnifiedAIService:
    """统一AI模型服务"""

    def __init__(self):
        self.providers: Dict[AIProvider, Any] = {}
        self.rotation_strategy = RotationStrategy(settings.AI_ROTATION_STRATEGY)
        self.current_provider_index = 0
        self.enabled_providers = [
            AIProvider(p) for p in settings.AI_ENABLED_PROVIDERS
        ]
        self.http_client = httpx.AsyncClient(timeout=60.0)
        
        # 初始化所有提供商
        self._initialize_providers()
        
        logger.info(f"UnifiedAIService initialized with {len(self.providers)} providers")

    def _initialize_providers(self):
        """初始化所有AI提供商"""
        # OpenAI
        if settings.OPENAI_API_KEY:
            self.providers[AIProvider.OPENAI] = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )
            logger.info("OpenAI provider initialized")

        # DeepSeek
        if settings.DEEPSEEK_API_KEY:
            self.providers[AIProvider.DEEPSEEK] = AsyncOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL
            )
            logger.info("DeepSeek provider initialized")

        # Claude
        if settings.CLAUDE_API_KEY:
            self.providers[AIProvider.CLAUDE] = anthropic.AsyncAnthropic(
                api_key=settings.CLAUDE_API_KEY,
                base_url=settings.CLAUDE_BASE_URL
            )
            logger.info("Claude provider initialized")

        # Gemini
        if settings.GEMINI_API_KEY:
            self.providers[AIProvider.GEMINI] = {
                "api_key": settings.GEMINI_API_KEY,
                "model": settings.GEMINI_MODEL
            }
            logger.info("Gemini provider initialized")

        # Qwen (阿里云百炼)
        if settings.QWEN_API_KEY:
            self.providers[AIProvider.QWEN] = AsyncOpenAI(
                api_key=settings.QWEN_API_KEY,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            logger.info("Qwen provider initialized")

        # Moonshot
        if settings.MOONSHOT_API_KEY:
            self.providers[AIProvider.MOONSHOT] = AsyncOpenAI(
                api_key=settings.MOONSHOT_API_KEY,
                base_url=settings.MOONSHOT_BASE_URL
            )
            logger.info("Moonshot provider initialized")

        # Ollama
        self.providers[AIProvider.OLLAMA] = AsyncOpenAI(
            base_url=settings.OLLAMA_BASE_URL,
            api_key="ollama"  # Ollama不需要API key
        )
        logger.info("Ollama provider initialized")

        # 火山引擎
        if settings.VOLCENGINE_API_KEY:
            self.providers[AIProvider.VOLCENGINE] = AsyncOpenAI(
                api_key=settings.VOLCENGINE_API_KEY,
                base_url=settings.VOLCENGINE_BASE_URL
            )
            logger.info("Volcengine provider initialized")

        # 阿里云百炼
        if settings.ALIBABA_BAILIAN_API_KEY:
            self.providers[AIProvider.ALIBABA_BAILIAN] = AsyncOpenAI(
                api_key=settings.ALIBABA_BAILIAN_API_KEY,
                base_url=settings.ALIBABA_BAILIAN_BASE_URL
            )
            logger.info("Alibaba Bailian provider initialized")

        # 硅基流动
        if settings.SILICONFLOW_API_KEY:
            self.providers[AIProvider.SILICONFLOW] = AsyncOpenAI(
                api_key=settings.SILICONFLOW_API_KEY,
                base_url=settings.SILICONFLOW_BASE_URL
            )
            logger.info("SiliconFlow provider initialized")

        # OpenRouter
        if settings.OPENROUTER_API_KEY:
            self.providers[AIProvider.OPENROUTER] = AsyncOpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL
            )
            logger.info("OpenRouter provider initialized")

    def _get_next_provider(self) -> Optional[AIProvider]:
        """获取下一个提供商（根据轮询策略）"""
        available_providers = [
            p for p in self.enabled_providers 
            if p in self.providers
        ]
        
        if not available_providers:
            logger.error("No available providers")
            return None

        if self.rotation_strategy == RotationStrategy.SEQUENTIAL:
            provider = available_providers[self.current_provider_index % len(available_providers)]
            self.current_provider_index += 1
        else:  # RANDOM
            provider = random.choice(available_providers)

        logger.info(f"Selected provider: {provider.value} (strategy: {self.rotation_strategy.value})")
        return provider

    def _count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """计算Token数量"""
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception:
            # 如果模型不支持，使用默认编码
            try:
                encoding = tiktoken.get_encoding("cl100k_base")
                return len(encoding.encode(text))
            except Exception as e:
                logger.warning(f"Failed to count tokens: {e}")
                # 粗略估算：1个token约等于4个字符（英文）或1.5个汉字
                return len(text) // 3

    async def _call_openai_compatible(
        self,
        provider: AIProvider,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AIResponse:
        """调用OpenAI兼容的API"""
        client = self.providers[provider]
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        content = response.choices[0].message.content
        token_usage = TokenUsage(
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens
        )

        return AIResponse(
            content=content,
            provider=provider,
            model=model,
            token_usage=token_usage,
            finish_reason=response.choices[0].finish_reason
        )

    async def _call_claude(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AIResponse:
        """调用Claude API"""
        client = self.providers[AIProvider.CLAUDE]
        
        # 转换消息格式
        system_message = None
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)

        response = await client.messages.create(
            model=model,
            system=system_message,
            messages=user_messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        content = response.content[0].text
        token_usage = TokenUsage(
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens
        )

        return AIResponse(
            content=content,
            provider=AIProvider.CLAUDE,
            model=model,
            token_usage=token_usage,
            finish_reason=response.stop_reason
        )

    async def _call_gemini(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AIResponse:
        """调用Gemini API"""
        config = self.providers[AIProvider.GEMINI]
        
        # 转换消息格式
        contents = [{"parts": [{"text": msg["content"]}]} for msg in messages]
        
        response = await self.http_client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={config['api_key']}",
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
        
        content = data["candidates"][0]["content"]["parts"][0]["text"]
        
        # Gemini不返回精确的token数，使用估算
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

    async def generate(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[AIProvider] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        max_retries: int = 3
    ) -> AIResponse:
        """
        生成AI响应（支持轮询和重试）
        
        Args:
            messages: 消息列表
            provider: 指定提供商（可选，不指定则使用轮询）
            model: 指定模型（可选）
            temperature: 温度参数
            max_tokens: 最大token数
            max_retries: 最大重试次数
            
        Returns:
            AIResponse: AI响应结果
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # 如果没有指定提供商，使用轮询策略
                if provider is None:
                    provider = self._get_next_provider()
                    if provider is None:
                        raise ValueError("No available AI providers")
                
                # 获取模型
                if model is None:
                    model = self._get_default_model(provider)
                
                logger.info(f"Calling {provider.value} with model {model} (attempt {attempt + 1}/{max_retries})")
                
                # 根据提供商调用不同的API
                if provider == AIProvider.CLAUDE:
                    response = await self._call_claude(messages, model, temperature, max_tokens)
                elif provider == AIProvider.GEMINI:
                    response = await self._call_gemini(messages, model, temperature, max_tokens)
                else:
                    # OpenAI兼容的API
                    response = await self._call_openai_compatible(provider, messages, model, temperature, max_tokens)
                
                logger.info(f"Successfully generated response from {provider.value}")
                return response
                
            except Exception as e:
                last_error = e
                logger.error(f"Error calling {provider.value if provider else 'provider'}: {str(e)}")
                
                # 如果是指定的提供商失败，不重试
                if provider is not None:
                    raise
                
                # 如果是轮询，尝试下一个提供商
                logger.info(f"Retrying with next provider...")
                await asyncio.sleep(1)  # 等待1秒后重试
        
        # 所有重试都失败
        raise Exception(f"Failed to generate response after {max_retries} attempts. Last error: {last_error}")

    def _get_default_model(self, provider: AIProvider) -> str:
        """获取提供商的默认模型"""
        model_map = {
            AIProvider.OPENAI: settings.OPENAI_MODEL,
            AIProvider.DEEPSEEK: settings.DEEPSEEK_MODEL,
            AIProvider.CLAUDE: settings.CLAUDE_MODEL,
            AIProvider.GEMINI: settings.GEMINI_MODEL,
            AIProvider.QWEN: settings.QWEN_MODEL,
            AIProvider.MOONSHOT: settings.MOONSHOT_MODEL,
            AIProvider.OLLAMA: settings.OLLAMA_MODEL,
            AIProvider.VOLCENGINE: settings.VOLCENGINE_MODEL,
            AIProvider.ALIBABA_BAILIAN: settings.ALIBABA_BAILIAN_MODEL,
            AIProvider.SILICONFLOW: settings.SILICONFLOW_MODEL,
            AIProvider.OPENROUTER: settings.OPENROUTER_MODEL,
        }
        return model_map.get(provider, "gpt-3.5-turbo")

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[AIProvider] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AsyncGenerator[str, None]:
        """
        流式生成AI响应
        
        Args:
            messages: 消息列表
            provider: 指定提供商（可选）
            model: 指定模型（可选）
            temperature: 温度参数
            max_tokens: 最大token数
            
        Yields:
            str: 生成的文本片段
        """
        # 获取提供商
        if provider is None:
            provider = self._get_next_provider()
        
        if provider is None:
            raise ValueError("No available AI providers")
        
        # 获取模型
        if model is None:
            model = self._get_default_model(provider)
        
        # 只支持OpenAI兼容的API的流式输出
        if provider in [AIProvider.CLAUDE, AIProvider.GEMINI]:
            # 对于不支持流式的提供商，先生成完整响应，然后逐字返回
            response = await self.generate(messages, provider, model, temperature, max_tokens)
            for char in response.content:
                yield char
                await asyncio.sleep(0.01)
            return
        
        # OpenAI兼容的流式输出
        client = self.providers[provider]
        
        try:
            stream = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error in stream generation: {str(e)}")
            raise

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """获取所有可用的提供商"""
        providers = []
        for provider in AIProvider:
            is_available = provider in self.providers
            providers.append({
                "name": provider.value,
                "display_name": provider.value.replace("_", " ").title(),
                "available": is_available,
                "default_model": self._get_default_model(provider) if is_available else None
            })
        return providers

    def set_rotation_strategy(self, strategy: RotationStrategy):
        """设置轮询策略"""
        self.rotation_strategy = strategy
        self.current_provider_index = 0
        logger.info(f"Rotation strategy set to: {strategy.value}")

    async def close(self):
        """关闭所有连接"""
        await self.http_client.aclose()
        logger.info("UnifiedAIService closed")


# 全局实例
unified_ai_service = UnifiedAIService()