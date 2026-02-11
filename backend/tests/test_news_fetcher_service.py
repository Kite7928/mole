"""
Unit tests for News Fetcher Service.
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
from app.services.news_fetcher import NewsFetcherService
from app.models.news import NewsSource


@pytest.fixture
def news_fetcher():
    """Create news fetcher service instance for testing."""
    return NewsFetcherService()


@pytest.fixture
def mock_rss_feed():
    """Mock RSS feed response."""
    mock_feed = Mock()
    mock_feed.entries = [
        Mock(
            title="测试新闻1",
            link="https://example.com/1",
            summary="测试摘要1",
            published_parsed=(2024, 1, 1, 12, 0, 0, 0, 1, -1),
            content=[Mock(value='<p>内容1 <img src="https://example.com/img1.jpg"></p>')]
        ),
        Mock(
            title="测试新闻2",
            link="https://example.com/2",
            summary="测试摘要2",
            published_parsed=(2024, 1, 1, 10, 0, 0, 0, 1, -1),
            content=[]
        )
    ]
    return mock_feed


@pytest.fixture
def mock_baidu_response():
    """Mock Baidu hot search response."""
    return {
        "data": {
            "cards": [
                {
                    "content": [
                        {"word": "百度热搜1", "desc": "描述1"},
                        {"word": "百度热搜2", "desc": "描述2"}
                    ]
                }
            ]
        }
    }


@pytest.fixture
def mock_zhihu_response():
    """Mock Zhihu hot list response."""
    return {
        "data": [
            {
                "target": {
                    "id": "12345",
                    "title": "知乎热榜1",
                    "excerpt": "知乎摘要1"
                },
                "hot_value": 50000
            },
            {
                "target": {
                    "id": "67890",
                    "title": "知乎热榜2",
                    "excerpt": "知乎摘要2"
                },
                "hot_value": 30000
            }
        ]
    }


@pytest.fixture
def mock_weibo_response():
    """Mock Weibo hot search response."""
    return {
        "data": {
            "realtime": [
                {"word": "微博热搜1", "note": "微博备注1", "num": 100000},
                {"word": "微博热搜2", "note": "微博备注2", "num": 80000}
            ]
        }
    }


class TestNewsFetcherService:
    """Test cases for NewsFetcherService."""

    def test_initialization(self, news_fetcher):
        """Test service initialization."""
        assert news_fetcher.http_client is not None
        assert NewsSource.ITHOME in news_fetcher.sources
        assert NewsSource.KR36 in news_fetcher.sources
        assert NewsSource.BAIDU in news_fetcher.sources

    @pytest.mark.asyncio
    async def test_fetch_from_ithome(self, news_fetcher, mock_rss_feed):
        """Test fetching news from IT之家."""
        with patch('feedparser.parse', return_value=mock_rss_feed):
            result = await news_fetcher.fetch_news(NewsSource.ITHOME, limit=10)

            assert len(result) == 2
            assert result[0].title == "测试新闻1"
            assert result[0].source == NewsSource.ITHOME
            assert result[0].source_name == "IT之家"
            assert result[0].url == "https://example.com/1"
            assert result[0].cover_image_url == "https://example.com/img1.jpg"

    @pytest.mark.asyncio
    async def test_fetch_from_baidu(self, news_fetcher, mock_baidu_response):
        """Test fetching from Baidu hot search."""
        mock_response = Mock()
        mock_response.json.return_value = mock_baidu_response
        mock_response.raise_for_status = Mock()

        news_fetcher.http_client.get = AsyncMock(return_value=mock_response)

        result = await news_fetcher.fetch_news(NewsSource.BAIDU, limit=10)

        assert len(result) == 2
        assert result[0].title == "百度热搜1"
        assert result[0].source == NewsSource.BAIDU
        assert result[0].hot_score == 100  # 100 - 0 * 2

    @pytest.mark.asyncio
    async def test_fetch_from_zhihu(self, news_fetcher, mock_zhihu_response):
        """Test fetching from Zhihu hot list."""
        mock_response = Mock()
        mock_response.json.return_value = mock_zhihu_response
        mock_response.raise_for_status = Mock()

        news_fetcher.http_client.get = AsyncMock(return_value=mock_response)

        result = await news_fetcher.fetch_news(NewsSource.ZHIHU, limit=10)

        assert len(result) == 2
        assert result[0].title == "知乎热榜1"
        assert result[0].url == "https://www.zhihu.com/question/12345"
        assert result[0].hot_score == 50.0  # 50000 / 1000

    @pytest.mark.asyncio
    async def test_fetch_from_weibo(self, news_fetcher, mock_weibo_response):
        """Test fetching from Weibo hot search."""
        mock_response = Mock()
        mock_response.json.return_value = mock_weibo_response
        mock_response.raise_for_status = Mock()

        news_fetcher.http_client.get = AsyncMock(return_value=mock_response)

        result = await news_fetcher.fetch_news(NewsSource.WEIBO, limit=10)

        assert len(result) == 2
        assert result[0].title == "微博热搜1"
        assert result[0].hot_score == 10.0  # 100000 / 10000

    @pytest.mark.asyncio
    async def test_fetch_all_news(self, news_fetcher, mock_rss_feed):
        """Test fetching news from all sources."""
        with patch('feedparser.parse', return_value=mock_rss_feed):
            # Mock other sources
            mock_response = Mock()
            mock_response.json.return_value = {"data": {"cards": [{"content": []}]}}
            mock_response.raise_for_status = Mock()
            news_fetcher.http_client.get = AsyncMock(return_value=mock_response)

            result = await news_fetcher.fetch_all_news(limit_per_source=5)

            # Should have news from IT_HOME at least
            assert len(result) > 0
            # Should be sorted by hot score
            assert result[0].hot_score >= result[-1].hot_score

    @pytest.mark.asyncio
    async def test_fetch_news_handles_error(self, news_fetcher):
        """Test error handling in fetch_news."""
        with patch('feedparser.parse', side_effect=Exception("Network error")):
            result = await news_fetcher.fetch_news(NewsSource.ITHOME, limit=10)

            # Should return empty list on error
            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_all_news_handles_partial_failure(self, news_fetcher, mock_rss_feed):
        """Test fetch_all_news handles partial failures."""
        with patch('feedparser.parse', return_value=mock_rss_feed):
            # Mock one source to fail
            async def mock_get(*args, **kwargs):
                raise Exception("API Error")

            news_fetcher.http_client.get = mock_get

            result = await news_fetcher.fetch_all_news(limit_per_source=5)

            # Should still return results from successful sources
            assert len(result) > 0

    def test_calculate_hot_score_recent(self, news_fetcher):
        """Test hot score calculation for recent news."""
        recent_time = datetime.now() - timedelta(minutes=30)
        score = news_fetcher._calculate_hot_score(recent_time)

        assert score == 100.0

    def test_calculate_hot_score_old(self, news_fetcher):
        """Test hot score calculation for old news."""
        old_time = datetime.now() - timedelta(hours=100)
        score = news_fetcher._calculate_hot_score(old_time)

        assert score < 50.0

    def test_calculate_hot_score_none(self, news_fetcher):
        """Test hot score calculation with None."""
        score = news_fetcher._calculate_hot_score(None)

        assert score == 50.0

    def test_calculate_hot_score_decay(self, news_fetcher):
        """Test hot score decay over time."""
        times = [
            timedelta(minutes=30),   # < 1 hour
            timedelta(hours=2),      # < 6 hours
            timedelta(hours=10),     # < 12 hours
            timedelta(hours=20),     # < 24 hours
            timedelta(hours=40),     # < 48 hours
            timedelta(hours=60),     # < 72 hours
            timedelta(hours=100)     # > 72 hours
        ]

        scores = [
            news_fetcher._calculate_hot_score(datetime.now() - t)
            for t in times
        ]

        # Scores should decrease over time
        assert scores[0] >= scores[1] >= scores[2] >= scores[3] >= scores[4] >= scores[5] >= scores[6]

    @pytest.mark.asyncio
    async def test_fetch_news_limit(self, news_fetcher, mock_rss_feed):
        """Test that limit parameter works correctly."""
        # Create more entries than limit
        for i in range(10):
            mock_rss_feed.entries.append(
                Mock(
                    title=f"测试新闻{i}",
                    link=f"https://example.com/{i}",
                    summary=f"测试摘要{i}",
                    published_parsed=(2024, 1, 1, 12, 0, 0, 0, 1, -1),
                    content=[]
                )
            )

        with patch('feedparser.parse', return_value=mock_rss_feed):
            result = await news_fetcher.fetch_news(NewsSource.ITHOME, limit=5)

            assert len(result) == 5

    @pytest.mark.asyncio
    async def test_fetch_news_without_images(self, news_fetcher):
        """Test handling news without images."""
        mock_feed = Mock()
        mock_feed.entries = [
            Mock(
                title="无图片新闻",
                link="https://example.com/noimg",
                summary="摘要",
                published_parsed=(2024, 1, 1, 12, 0, 0, 0, 1, -1),
                content=[]
            )
        ]

        with patch('feedparser.parse', return_value=mock_feed):
            result = await news_fetcher.fetch_news(NewsSource.ITHOME, limit=10)

            assert len(result) == 1
            assert result[0].cover_image_url is None
            assert result[0].images is None

    @pytest.mark.asyncio
    async def test_close(self, news_fetcher):
        """Test closing the service."""
        news_fetcher.http_client.aclose = AsyncMock()

        await news_fetcher.close()

        news_fetcher.http_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_unsupported_source(self, news_fetcher):
        """Test fetching from unsupported source."""
        result = await news_fetcher.fetch_news("unsupported", limit=10)

        assert result == []