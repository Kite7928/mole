"""
Unit tests for AI Writer Service.
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from app.services.ai_writer import AIWriterService
from app.core.config import settings


@pytest.fixture
def ai_writer():
    """Create AI writer service instance for testing."""
    return AIWriterService()


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"titles": [{"title": "测试标题1", "predicted_click_rate": 0.85, "emotion": "强烈"}, {"title": "测试标题2", "predicted_click_rate": 0.78, "emotion": "中等"}]}'
    return mock_response


@pytest.fixture
def mock_content_response():
    """Mock content generation response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"content": "这是测试文章内容", "summary": "测试摘要", "tags": ["AI", "测试"], "quality_score": 0.85}'
    return mock_response


class TestAIWriterService:
    """Test cases for AIWriterService."""

    @pytest.mark.asyncio
    async def test_generate_titles_with_openai(self, ai_writer, mock_openai_response):
        """Test generating titles using OpenAI."""
        # Mock OpenAI client
        ai_writer.openai_client = AsyncMock()
        ai_writer.openai_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)

        # Test
        result = await ai_writer.generate_titles("测试主题", count=2, model="openai")

        # Assertions
        assert len(result) == 2
        assert result[0]["title"] == "测试标题1"
        assert result[0]["predicted_click_rate"] == 0.85
        assert result[1]["title"] == "测试标题2"

    @pytest.mark.asyncio
    async def test_generate_titles_without_api_key(self, ai_writer):
        """Test generating titles without API key raises error."""
        ai_writer.openai_client = None

        with pytest.raises(ValueError, match="OpenAI client not initialized"):
            await ai_writer.generate_titles("测试主题", model="openai")

    @pytest.mark.asyncio
    async def test_generate_content(self, ai_writer, mock_content_response):
        """Test generating article content."""
        # Mock OpenAI client
        ai_writer.openai_client = AsyncMock()
        ai_writer.openai_client.chat.completions.create = AsyncMock(return_value=mock_content_response)

        # Test
        result = await ai_writer.generate_content(
            topic="AI技术",
            title="AI技术突破",
            style="professional",
            length="short"
        )

        # Assertions
        assert result["content"] == "这是测试文章内容"
        assert result["summary"] == "测试摘要"
        assert result["tags"] == ["AI", "测试"]
        assert result["quality_score"] == 0.85

    @pytest.mark.asyncio
    async def test_optimize_content_enhance(self, ai_writer, mock_content_response):
        """Test content optimization - enhance."""
        ai_writer.openai_client = AsyncMock()
        ai_writer.openai_client.chat.completions.create = AsyncMock(return_value=mock_content_response)

        result = await ai_writer.optimize_content(
            content="原始内容",
            optimization_type="enhance"
        )

        assert result == "这是测试文章内容"

    @pytest.mark.asyncio
    async def test_optimize_content_shorten(self, ai_writer, mock_content_response):
        """Test content optimization - shorten."""
        ai_writer.openai_client = AsyncMock()
        ai_writer.openai_client.chat.completions.create = AsyncMock(return_value=mock_content_response)

        result = await ai_writer.optimize_content(
            content="原始内容",
            optimization_type="shorten"
        )

        assert result == "这是测试文章内容"

    @pytest.mark.asyncio
    async def test_optimize_content_on_error_returns_original(self, ai_writer):
        """Test that optimization returns original content on error."""
        ai_writer.openai_client = AsyncMock()
        ai_writer.openai_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))

        original_content = "原始内容"
        result = await ai_writer.optimize_content(
            content=original_content,
            optimization_type="enhance"
        )

        # Should return original content on error
        assert result == original_content

    def test_build_title_prompt(self, ai_writer):
        """Test building title generation prompt."""
        prompt = ai_writer._build_title_prompt("测试主题", 5)

        assert "测试主题" in prompt
        assert "5" in prompt
        assert "JSON 格式" in prompt
        assert "predicted_click_rate" in prompt

    def test_build_content_prompt(self, ai_writer):
        """Test building content generation prompt."""
        prompt = ai_writer._build_content_prompt(
            topic="AI技术",
            title="AI突破",
            style="professional",
            length="short",
            enable_research=True
        )

        assert "AI技术" in prompt
        assert "AI突破" in prompt
        assert "专业" in prompt
        assert "800-1200 字" in prompt
        assert "深度研究" in prompt

    def test_build_content_prompt_with_research_disabled(self, ai_writer):
        """Test building content prompt without research."""
        prompt = ai_writer._build_content_prompt(
            topic="AI技术",
            title="AI突破",
            style="casual",
            length="long",
            enable_research=False
        )

        assert "深度研究" not in prompt
        assert "轻松" in prompt
        assert "3000-5000 字" in prompt

    def test_build_optimization_prompt(self, ai_writer):
        """Test building optimization prompt."""
        prompt = ai_writer._build_optimization_prompt("原始内容", "enhance")

        assert "原始内容" in prompt
        assert "增强" in prompt

    @pytest.mark.asyncio
    async def test_generate_with_deepseek(self, ai_writer):
        """Test generating content with DeepSeek."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"titles": [{"title": "DeepSeek标题"}]'}}}]
        }
        mock_response.raise_for_status = Mock()

        ai_writer.http_client = AsyncMock()
        ai_writer.http_client.post = AsyncMock(return_value=mock_response)

        result = await ai_writer._generate_with_deepseek("prompt", 1)

        assert len(result) == 1
        assert result[0]["title"] == "DeepSeek标题"

    @pytest.mark.asyncio
    async def test_generate_with_deepseek_no_api_key(self, ai_writer):
        """Test DeepSeek generation without API key."""
        with patch.object(settings, 'DEEPSEEK_API_KEY', None):
            with pytest.raises(ValueError, match="DeepSeek API key not configured"):
                await ai_writer._generate_with_deepseek("prompt", 1)

    @pytest.mark.asyncio
    async def test_close(self, ai_writer):
        """Test closing the service."""
        ai_writer.http_client = AsyncMock()
        ai_writer.http_client.aclose = AsyncMock()

        await ai_writer.close()

        ai_writer.http_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_titles_handles_json_error(self, ai_writer):
        """Test handling of JSON parsing errors."""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON"

        ai_writer.openai_client = AsyncMock()
        ai_writer.openai_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with pytest.raises(Exception):
            await ai_writer.generate_titles("测试主题", model="openai")