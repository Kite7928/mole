"""
测试重构后的 UnifiedAIService
"""

import pytest
from app.services.unified_ai_service import (
    UnifiedAIService,
    AIProviderError,
    NoAvailableProviderError
)
from app.services.providers import AIProvider, TokenUsage, AIResponse
from app.services.cache import CacheService, ai_response_cache


class TestCacheService:
    """测试缓存服务"""

    def test_cache_set_and_get(self):
        """测试缓存设置和获取"""
        cache = CacheService(default_ttl=60)

        # 设置缓存
        cache.set("key1", "value1")

        # 获取缓存
        value = cache.get("key1")
        assert value == "value1"

    def test_cache_expiration(self):
        """测试缓存过期"""
        cache = CacheService(default_ttl=0)  # 立即过期

        cache.set("key1", "value1")

        # 应该返回None（已过期）
        value = cache.get("key1")
        assert value is None

    def test_cache_stats(self):
        """测试缓存统计"""
        cache = CacheService()

        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("key2")  # miss

        stats = cache.get_stats()
        assert stats["hit_count"] == 1
        assert stats["miss_count"] == 1

    def test_cache_clear(self):
        """测试清空缓存"""
        cache = CacheService()

        cache.set("key1", "value1")
        cache.clear()

        value = cache.get("key1")
        assert value is None


class TestUnifiedAIService:
    """测试 UnifiedAIService"""

    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """测试服务初始化"""
        service = UnifiedAIService()

        # 未初始化时应该没有提供商
        assert not service._initialized

        # 初始化
        await service.initialize()
        assert service._initialized

        await service.close()

    @pytest.mark.asyncio
    async def test_get_available_providers(self):
        """测试获取可用提供商"""
        service = UnifiedAIService()
        await service.initialize()

        providers = service.get_available_providers()
        assert isinstance(providers, list)

        # 每个提供商应该有这些字段
        for provider in providers:
            assert "name" in provider
            assert "display_name" in provider
            assert "available" in provider

        await service.close()

    def test_set_rotation_strategy(self):
        """测试设置轮询策略"""
        service = UnifiedAIService()

        from app.services.providers import RotationStrategy

        service.set_rotation_strategy(RotationStrategy.RANDOM)
        assert service.rotation_strategy == RotationStrategy.RANDOM

        service.set_rotation_strategy(RotationStrategy.SEQUENTIAL)
        assert service.rotation_strategy == RotationStrategy.SEQUENTIAL

    def test_cache_stats(self):
        """测试获取缓存统计"""
        service = UnifiedAIService()
        stats = service.get_cache_stats()

        assert "total_entries" in stats
        assert "hit_count" in stats
        assert "miss_count" in stats
        assert "hit_rate" in stats


class TestAIResponse:
    """测试 AIResponse"""

    def test_ai_response_creation(self):
        """测试 AIResponse 创建"""
        token_usage = TokenUsage(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )

        response = AIResponse(
            content="测试内容",
            provider=AIProvider.OPENAI,
            model="gpt-4",
            token_usage=token_usage
        )

        assert response.content == "测试内容"
        assert response.provider == AIProvider.OPENAI
        assert response.token_usage.total_tokens == 30

    def test_ai_response_to_dict(self):
        """测试 AIResponse 转换为字典"""
        token_usage = TokenUsage(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )

        response = AIResponse(
            content="测试内容",
            provider=AIProvider.OPENAI,
            model="gpt-4",
            token_usage=token_usage
        )

        data = response.to_dict()
        assert data["content"] == "测试内容"
        assert data["provider"] == "openai"
        assert "token_usage" in data


class TestExceptions:
    """测试异常类"""

    def test_ai_provider_error(self):
        """测试 AIProviderError"""
        error = AIProviderError("测试错误")
        assert str(error) == "测试错误"

    def test_no_available_provider_error(self):
        """测试 NoAvailableProviderError"""
        error = NoAvailableProviderError("没有可用提供商")
        assert str(error) == "没有可用提供商"