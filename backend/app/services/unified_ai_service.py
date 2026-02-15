"""
统一AI模型服务 - 重构版
支持多个AI提供商，提供统一的调用接口、Token计算、日志记录、错误处理和轮询机制
支持从数据库读取配置（优先）或环境变量（回退）
"""

from typing import List, Dict, Any, AsyncGenerator, Optional
import random
import asyncio
import tiktoken
from sqlalchemy import select

from ..core.config import settings
from ..core.logger import logger
from ..core.database import async_session_maker
from .sensitive_words import filter_sensitive_words, check_sensitive_words
from .providers import (
    AIProvider,
    AIResponse,
    TokenUsage,
    RotationStrategy,
    OpenAICompatibleProvider,
    ClaudeProvider,
    GeminiProvider,
    BaseAIProvider
)
from .cache import ai_response_cache
from .config_service import config_service


class AIProviderError(Exception):
    """AI提供商错误"""
    pass


class NoAvailableProviderError(AIProviderError):
    """没有可用提供商错误"""
    pass


# 提供商默认配置映射
DEFAULT_PROVIDER_CONFIGS = {
    AIProvider.OPENAI: {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4-turbo-preview",
        "env_key": "OPENAI_API_KEY"
    },
    AIProvider.DEEPSEEK: {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY"
    },
    AIProvider.CLAUDE: {
        "base_url": "https://api.anthropic.com/v1",
        "model": "claude-3-opus-20240229",
        "env_key": "CLAUDE_API_KEY"
    },
    AIProvider.GEMINI: {
        "base_url": None,  # Gemini 使用特殊处理
        "model": "gemini-pro",
        "env_key": "GEMINI_API_KEY"
    },
    AIProvider.QWEN: {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-max",
        "env_key": "QWEN_API_KEY"
    },
    AIProvider.MOONSHOT: {
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-8k",
        "env_key": "MOONSHOT_API_KEY"
    },
    AIProvider.OLLAMA: {
        "base_url": "http://localhost:11434/v1",
        "model": "llama2",
        "env_key": None  # Ollama 不需要 API Key
    },
    AIProvider.ZHIPU: {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
        "env_key": "ZHIPU_API_KEY"
    },
}


class UnifiedAIService:
    """统一AI模型服务 - 重构版
    
    配置优先级：
    1. 数据库配置（如果已配置且启用）
    2. 环境变量配置（.env 文件）
    3. 默认配置
    """

    def __init__(self):
        self.providers: Dict[AIProvider, BaseAIProvider] = {}
        self.rotation_strategy = RotationStrategy.SEQUENTIAL
        self.current_provider_index = 0
        self._initialized = False
        self._db_configs: Dict[str, Dict[str, Any]] = {}

    async def _load_db_configs(self) -> Dict[str, Dict[str, Any]]:
        """从数据库加载AI提供商配置（包含真实API Key）"""
        try:
            async with async_session_maker() as db:
                from ..models.ai_provider_config import AIProviderConfig
                result = await db.execute(
                    select(AIProviderConfig).where(AIProviderConfig.api_key.isnot(None))
                )
                configs = result.scalars().all()
                result_dict = {}
                for cfg in configs:
                    result_dict[cfg.provider] = {
                        "provider": cfg.provider,
                        "api_key": cfg.api_key,
                        "has_api_key": bool(cfg.api_key),
                        "base_url": cfg.base_url,
                        "model": cfg.model,
                        "is_enabled": cfg.is_enabled,
                        "is_default": cfg.is_default,
                    }
                return result_dict
        except Exception as e:
            logger.warning(f"从数据库加载配置失败: {e}，将使用环境变量配置")
            return {}

    def _get_api_key(self, provider: AIProvider, default_config: Dict[str, Any]) -> Optional[str]:
        """获取API密钥（优先从环境变量读取敏感信息）"""
        env_key_name = default_config.get("env_key")
        if env_key_name:
            return getattr(settings, env_key_name, None)
        return None

    def _init_provider(self, provider_type: AIProvider, api_key: str, base_url: str, model: str):
        """初始化单个提供商"""
        if provider_type == AIProvider.GEMINI:
            self.providers[provider_type] = GeminiProvider(
                api_key=api_key,
                default_model=model
            )
        elif provider_type == AIProvider.CLAUDE:
            self.providers[provider_type] = ClaudeProvider(
                api_key=api_key,
                base_url=base_url,
                default_model=model
            )
        else:
            # OpenAI 兼容格式
            needs_api_key = provider_type != AIProvider.OLLAMA
            self.providers[provider_type] = OpenAICompatibleProvider(
                provider_type=provider_type,
                api_key=api_key,
                base_url=base_url,
                default_model=model,
                needs_api_key=needs_api_key
            )

    async def initialize(self):
        """初始化所有提供商（优先从数据库读取配置）"""
        if self._initialized:
            return

        # 从数据库加载配置
        self._db_configs = await self._load_db_configs()

        if self._db_configs:
            logger.info(f"从数据库加载了 {len(self._db_configs)} 个AI提供商配置")

        # 初始化所有支持的提供商
        for provider_type, default_config in DEFAULT_PROVIDER_CONFIGS.items():
            provider_id = provider_type.value

            # 检查数据库配置
            db_config = self._db_configs.get(provider_id)

            if db_config and db_config.get("is_enabled"):
                # 使用数据库配置的API Key、URL和模型
                api_key = db_config.get("api_key") or self._get_api_key(provider_type, default_config)
                if api_key or provider_type == AIProvider.OLLAMA:
                    base_url = db_config.get("base_url") or default_config["base_url"]
                    # 优先使用数据库中的模型配置
                    model = db_config.get("model") or default_config["model"]
                    self._init_provider(provider_type, api_key, base_url, model)
                    logger.info(f"已初始化 {provider_id}（模型: {model}）")
            else:
                # 使用环境变量配置
                api_key = self._get_api_key(provider_type, default_config)
                if api_key or provider_type == AIProvider.OLLAMA:
                    base_url = default_config["base_url"]
                    model = default_config["model"]
                    self._init_provider(provider_type, api_key, base_url, model)

        self._initialized = True
        available_count = len([p for p in self.providers.values() if p.is_available])
        logger.info(f"UnifiedAIService 初始化完成，{available_count} 个提供商可用")

    async def reload_configs(self):
        """重新加载配置（用于配置更新后）"""
        logger.info("重新加载AI提供商配置...")
        self._initialized = False
        self.providers.clear()
        await self.initialize()

    def _get_available_providers(self) -> List[AIProvider]:
        """获取所有可用的提供商（默认提供商排在最前面）"""
        available = []
        default_provider = None

        # 找出默认提供商
        for provider_id, config in self._db_configs.items():
            if config.get("is_default"):
                try:
                    default_provider = AIProvider(provider_id)
                    break
                except ValueError:
                    continue

        # 收集所有可用提供商
        for provider_type, provider in self.providers.items():
            if provider.is_available:
                available.append(provider_type)

        # 将默认提供商移到最前面
        if default_provider and default_provider in available:
            available.remove(default_provider)
            available.insert(0, default_provider)

        return available

    def _get_next_provider(self) -> AIProvider | None:
        """获取下一个提供商（根据轮询策略）"""
        available = self._get_available_providers()

        if not available:
            logger.error("没有可用的AI提供商")
            return None

        if self.rotation_strategy == RotationStrategy.SEQUENTIAL:
            provider = available[self.current_provider_index % len(available)]
            self.current_provider_index += 1
        else:  # RANDOM
            provider = random.choice(available)

        logger.debug(f"选择提供商: {provider.value} (策略: {self.rotation_strategy.value})")
        return provider

    def _count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """计算Token数量"""
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception:
            try:
                encoding = tiktoken.get_encoding("cl100k_base")
                return len(encoding.encode(text))
            except Exception as e:
                logger.warning(f"Token计算失败: {e}")
                return len(text) // 3

    def _generate_cache_key(
        self,
        messages: List[Dict[str, str]],
        provider: AIProvider | None,
        model: str | None,
        temperature: float,
        max_tokens: int
    ) -> str:
        """生成缓存键"""
        return ai_response_cache._generate_key(
            "ai_generate",
            messages,
            provider.value if provider else "auto",
            model or "default",
            temperature,
            max_tokens
        )

    async def generate(
        self,
        messages: List[Dict[str, str]],
        provider: AIProvider | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        max_retries: int = 3,
        use_cache: bool = True
    ) -> AIResponse:
        """
        生成AI响应（支持轮询、重试和缓存）

        Args:
            messages: 消息列表
            provider: 指定提供商（可选）
            model: 指定模型（可选）
            temperature: 温度参数
            max_tokens: 最大token数
            max_retries: 最大重试次数
            use_cache: 是否使用缓存

        Returns:
            AIResponse: AI响应结果
        """
        if not self._initialized:
            await self.initialize()

        # 检查缓存
        if use_cache:
            cache_key = self._generate_cache_key(messages, provider, model, temperature, max_tokens)
            cached_response = ai_response_cache.get(cache_key)
            if cached_response:
                logger.info(f"缓存命中，返回缓存的响应")
                return cached_response

        last_error = None
        specified_provider = provider
        specified_model = model

        for attempt in range(max_retries):
            try:
                # 如果没有指定提供商，使用轮询策略
                if specified_provider is None:
                    provider = self._get_next_provider()
                    if provider is None:
                        raise NoAvailableProviderError("没有可用的AI提供商")

                provider_instance = self.providers.get(provider)
                if not provider_instance or not provider_instance.is_available:
                    logger.warning(f"提供商 {provider.value} 不可用，尝试下一个")
                    continue

                # 获取模型（使用局部变量，避免修改外部参数）
                current_model = specified_model
                if current_model is None:
                    current_model = provider_instance.get_default_model()

                logger.info(f"调用 {provider.value}，模型: {current_model} (尝试 {attempt + 1}/{max_retries})")

                # 调用提供商生成响应
                response = await provider_instance.generate(
                    messages=messages,
                    model=current_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                # 过滤敏感词
                sensitive_words = check_sensitive_words(response.content)
                if sensitive_words:
                    logger.info(f"检测到敏感词: {', '.join(sensitive_words)}")

                filtered_content = filter_sensitive_words(response.content)
                response.content = filtered_content
                response.metadata = {
                    "sensitive_words_filtered": len(sensitive_words),
                    "sensitive_words_list": sensitive_words
                }

                # 存入缓存
                if use_cache:
                    ai_response_cache.set(cache_key, response)

                return response

            except Exception as e:
                last_error = e
                logger.error(f"调用 {provider.value if provider else '未知提供商'} 失败: {str(e)}")

                # 如果是指定的提供商失败，不重试
                if specified_provider is not None:
                    raise AIProviderError(f"指定的提供商 {specified_provider.value} 调用失败: {e}")

                # 等待后重试
                await asyncio.sleep(1 * (attempt + 1))

        # 所有重试都失败
        raise AIProviderError(f"经过 {max_retries} 次尝试后仍然失败。最后错误: {last_error}")

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        provider: AIProvider | None = None,
        model: str | None = None,
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
        if not self._initialized:
            await self.initialize()

        if provider is None:
            provider = self._get_next_provider()

        if provider is None:
            raise NoAvailableProviderError("没有可用的AI提供商")

        provider_instance = self.providers.get(provider)
        if not provider_instance:
            raise AIProviderError(f"未知的提供商: {provider.value}")

        if model is None:
            model = provider_instance.get_default_model()

        async for chunk in provider_instance.generate_stream(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        ):
            yield chunk

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """获取所有可用的提供商"""
        if not self._initialized:
            asyncio.create_task(self.initialize())

        result = []
        for provider_type in AIProvider:
            provider = self.providers.get(provider_type)
            is_available = provider.is_available if provider else False
            result.append({
                "name": provider_type.value,
                "display_name": provider_type.value.replace("_", " ").title(),
                "available": is_available,
                "default_model": provider.get_default_model() if is_available else None
            })
        return result

    def set_rotation_strategy(self, strategy: RotationStrategy):
        """设置轮询策略"""
        self.rotation_strategy = strategy
        self.current_provider_index = 0
        logger.info(f"轮询策略已设置为: {strategy.value}")

    def clear_cache(self):
        """清空AI响应缓存"""
        ai_response_cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return ai_response_cache.get_stats()

    async def close(self):
        """关闭所有提供商连接"""
        for provider in self.providers.values():
            try:
                await provider.close()
            except Exception as e:
                logger.warning(f"关闭提供商连接失败: {e}")

        logger.info("UnifiedAIService 已关闭")


# 全局实例
unified_ai_service = UnifiedAIService()