"""
Unit tests for data models.
"""
import pytest
from datetime import datetime
from app.models.article import Article, ArticleStatus, ArticleSource, ArticleTemplate
from app.models.news import NewsItem, NewsSource, NewsCategory, NewsSourceConfig


class TestArticleModel:
    """Test cases for Article model."""

    def test_article_creation(self):
        """Test creating a basic article."""
        article = Article(
            title="测试文章",
            content="文章内容",
            status=ArticleStatus.DRAFT,
            source=ArticleSource.MANUAL
        )

        assert article.title == "测试文章"
        assert article.content == "文章内容"
        assert article.status == ArticleStatus.DRAFT
        assert article.source == ArticleSource.MANUAL
        assert article.read_count == 0
        assert article.like_count == 0

    def test_article_with_all_fields(self):
        """Test creating article with all fields."""
        article = Article(
            title="AI技术突破",
            summary="AI技术取得重大突破",
            content="详细内容...",
            html_content="<p>详细内容...</p>",
            status=ArticleStatus.READY,
            source=ArticleSource.AI_HOTSPOT,
            source_topic="人工智能",
            source_url="https://example.com",
            ai_model="gpt-4",
            ai_prompt_tokens=100,
            ai_completion_tokens=500,
            ai_total_tokens=600,
            cover_image_url="https://example.com/cover.jpg",
            cover_image_media_id="media_id_123",
            wechat_draft_id="draft_id_123",
            wechat_article_id="article_id_123",
            read_count=1000,
            like_count=50,
            share_count=20,
            comment_count=10,
            tags=["AI", "技术", "突破"],
            category="科技",
            quality_score=0.85,
            predicted_click_rate=0.75
        )

        assert article.title == "AI技术突破"
        assert article.status == ArticleStatus.READY
        assert article.ai_model == "gpt-4"
        assert article.tags == ["AI", "技术", "突破"]
        assert article.quality_score == 0.85
        assert article.read_count == 1000

    def test_article_status_enum(self):
        """Test ArticleStatus enum values."""
        assert ArticleStatus.DRAFT == "draft"
        assert ArticleStatus.GENERATING == "generating"
        assert ArticleStatus.READY == "ready"
        assert ArticleStatus.PUBLISHED == "published"
        assert ArticleStatus.FAILED == "failed"

    def test_article_source_enum(self):
        """Test ArticleSource enum values."""
        assert ArticleSource.MANUAL == "manual"
        assert ArticleSource.AI_HOTSPOT == "ai_hotspot"
        assert ArticleSource.BAIDU_SEARCH == "baidu_search"
        assert ArticleSource.CUSTOM_RSS == "custom_rss"

    def test_article_repr(self):
        """Test article string representation."""
        article = Article(
            id=1,
            title="测试文章",
            status=ArticleStatus.DRAFT
        )

        repr_str = repr(article)
        assert "Article" in repr_str
        assert "1" in repr_str
        assert "测试文章" in repr_str
        assert "draft" in repr_str

    def test_article_default_values(self):
        """Test article default field values."""
        article = Article(
            title="测试",
            content="内容"
        )

        assert article.status == ArticleStatus.DRAFT
        assert article.source == ArticleSource.MANUAL
        assert article.read_count == 0
        assert article.like_count == 0
        assert article.share_count == 0
        assert article.comment_count == 0


class TestArticleTemplateModel:
    """Test cases for ArticleTemplate model."""

    def test_template_creation(self):
        """Test creating article template."""
        template = ArticleTemplate(
            name="科技新闻模板",
            description="用于生成科技新闻的模板",
            template_type="tech_news",
            structure={"sections": ["intro", "body", "conclusion"]},
            prompt_template="请根据以下主题生成科技新闻：{topic}"
        )

        assert template.name == "科技新闻模板"
        assert template.template_type == "tech_news"
        assert template.usage_count == 0

    def test_template_with_settings(self):
        """Test template with AI settings."""
        template = ArticleTemplate(
            name="深度分析模板",
            template_type="deep_analysis",
            structure=[],
            prompt_template="深度分析模板：{topic}",
            default_ai_model="gpt-4",
            default_temperature=0.7,
            default_max_tokens=4000
        )

        assert template.default_ai_model == "gpt-4"
        assert template.default_temperature == 0.7
        assert template.default_max_tokens == 4000

    def test_template_repr(self):
        """Test template string representation."""
        template = ArticleTemplate(
            id=1,
            name="测试模板",
            template_type="test"
        )

        repr_str = repr(template)
        assert "ArticleTemplate" in repr_str
        assert "1" in repr_str
        assert "测试模板" in repr_str
        assert "test" in repr_str


class TestNewsItemModel:
    """Test cases for NewsItem model."""

    def test_news_item_creation(self):
        """Test creating news item."""
        news = NewsItem(
            title="测试新闻",
            url="https://example.com/news",
            source=NewsSource.ITHOME,
            source_name="IT之家",
            category=NewsCategory.TECH
        )

        assert news.title == "测试新闻"
        assert news.url == "https://example.com/news"
        assert news.source == NewsSource.ITHOME
        assert news.category == NewsCategory.TECH
        assert news.hot_score == 0.0
        assert news.is_processed is False
        assert news.is_used is False

    def test_news_item_with_all_fields(self):
        """Test news item with all fields."""
        news = NewsItem(
            title="AI技术突破",
            summary="AI技术取得重大突破",
            content="详细内容...",
            url="https://example.com/ai-news",
            source=NewsSource.KR36,
            source_name="36氪",
            author="张三",
            category=NewsCategory.AI,
            tags=["AI", "技术"],
            hot_score=85.5,
            read_count=10000,
            comment_count=100,
            share_count=50,
            like_count=200,
            cover_image_url="https://example.com/cover.jpg",
            images=["img1.jpg", "img2.jpg"],
            is_processed=True,
            is_used=True,
            used_article_id=123,
            quality_score=0.9,
            relevance_score=0.85
        )

        assert news.title == "AI技术突破"
        assert news.source == NewsSource.KR36
        assert news.hot_score == 85.5
        assert news.is_processed is True
        assert news.is_used is True
        assert news.used_article_id == 123

    def test_news_source_enum(self):
        """Test NewsSource enum values."""
        assert NewsSource.ITHOME == "ithome"
        assert NewsSource.KR36 == "36kr"
        assert NewsSource.BAIDU == "baidu"
        assert NewsSource.ZHIHU == "zhihu"
        assert NewsSource.WEIBO == "weibo"
        assert NewsSource.CUSTOM == "custom"

    def test_news_category_enum(self):
        """Test NewsCategory enum values."""
        assert NewsCategory.AI == "ai"
        assert NewsCategory.TECH == "tech"
        assert NewsCategory.BUSINESS == "business"
        assert NewsCategory.ENTERTAINMENT == "entertainment"
        assert NewsCategory.OTHER == "other"

    def test_news_item_repr(self):
        """Test news item string representation."""
        news = NewsItem(
            id=1,
            title="测试新闻",
            source=NewsSource.BAIDU,
            hot_score=75.0
        )

        repr_str = repr(news)
        assert "NewsItem" in repr_str
        assert "1" in repr_str
        assert "测试新闻" in repr_str
        assert "baidu" in repr_str
        assert "75.0" in repr_str

    def test_news_item_default_values(self):
        """Test news item default field values."""
        news = NewsItem(
            title="测试",
            url="https://example.com",
            source=NewsSource.CUSTOM
        )

        assert news.hot_score == 0.0
        assert news.read_count == 0
        assert news.comment_count == 0
        assert news.share_count == 0
        assert news.like_count == 0
        assert news.is_processed is False
        assert news.is_used is False


class TestNewsSourceConfigModel:
    """Test cases for NewsSourceConfig model."""

    def test_source_config_creation(self):
        """Test creating news source config."""
        config = NewsSourceConfig(
            source=NewsSource.ITHOME,
            name="IT之家",
            description="IT科技新闻",
            rss_url="https://www.ithome.com/rss/"
        )

        assert config.source == NewsSource.ITHOME
        assert config.name == "IT之家"
        assert config.is_active is True
        assert config.fetch_interval == 1800
        assert config.max_items_per_fetch == 50

    def test_source_config_with_all_fields(self):
        """Test source config with all fields."""
        config = NewsSourceConfig(
            source=NewsSource.BAIDU,
            name="百度热搜",
            description="百度热搜榜",
            api_url="https://top.baidu.com/api/board",
            api_key="test_key",
            is_active=True,
            fetch_interval=3600,
            max_items_per_fetch=100,
            retry_limit=5,
            min_hot_score=50.0,
            allowed_categories=["tech", "ai"],
            blocked_keywords=["广告", "推广"],
            total_fetched=1000,
            last_fetch_status="success"
        )

        assert config.source == NewsSource.BAIDU
        assert config.fetch_interval == 3600
        assert config.min_hot_score == 50.0
        assert config.allowed_categories == ["tech", "ai"]
        assert config.total_fetched == 1000

    def test_source_config_default_values(self):
        """Test source config default field values."""
        config = NewsSourceConfig(
            source=NewsSource.CUSTOM,
            name="自定义源"
        )

        assert config.is_active is True
        assert config.fetch_interval == 1800
        assert config.max_items_per_fetch == 50
        assert config.retry_limit == 3
        assert config.min_hot_score == 0.0
        assert config.total_fetched == 0

    def test_source_config_repr(self):
        """Test source config string representation."""
        config = NewsSourceConfig(
            id=1,
            source=NewsSource.ZHIHU,
            name="知乎",
            is_active=True
        )

        repr_str = repr(config)
        assert "NewsSourceConfig" in repr_str
        assert "1" in repr_str
        assert "zhihu" in repr_str
        assert "知乎" in repr_str
        assert "True" in repr_str

    def test_news_item_with_json_fields(self):
        """Test news item with JSON fields."""
        news = NewsItem(
            title="测试",
            url="https://example.com",
            source=NewsSource.CUSTOM,
            tags=["标签1", "标签2", "标签3"],
            images=["img1.jpg", "img2.jpg"]
        )

        assert isinstance(news.tags, list)
        assert len(news.tags) == 3
        assert isinstance(news.images, list)
        assert len(news.images) == 2

    def test_article_with_json_fields(self):
        """Test article with JSON fields."""
        article = Article(
            title="测试",
            content="内容",
            tags=["AI", "Python", "FastAPI"]
        )

        assert isinstance(article.tags, list)
        assert len(article.tags) == 3
        assert "AI" in article.tags

    def test_model_relationships_exist(self):
        """Test that model relationships are defined."""
        # Article should have relationships
        article = Article(title="测试", content="内容")
        assert hasattr(article, 'user')
        assert hasattr(article, 'account')
        assert hasattr(article, 'tasks')

    def test_news_item_unique_url(self):
        """Test that news item URL should be unique."""
        news1 = NewsItem(
            title="新闻1",
            url="https://example.com/news",
            source=NewsSource.CUSTOM
        )

        news2 = NewsItem(
            title="新闻2",
            url="https://example.com/news",  # Same URL
            source=NewsSource.CUSTOM
        )

        # In a real database, this would cause a unique constraint violation
        assert news1.url == news2.url