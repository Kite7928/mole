"""
数据模型测试
测试Article、News、WeChatConfig模型
"""

import pytest
from datetime import datetime
from app.models.article import Article, ArticleStatus
from app.models.news import NewsItem, NewsSource
from app.models.wechat import WeChatConfig


class TestArticle:
    """文章模型测试"""
    
    def test_create_article(self):
        """测试创建文章"""
        article = Article(
            title="测试文章",
            content="这是测试内容",
            status=ArticleStatus.DRAFT
        )
        
        assert article.title == "测试文章"
        assert article.content == "这是测试内容"
        assert article.status == ArticleStatus.DRAFT
        assert article.id is None  # 未保存到数据库
    
    def test_article_with_optional_fields(self):
        """测试带可选字段的文章"""
        article = Article(
            title="完整文章",
            content="完整内容",
            summary="文章摘要",
            source_topic="测试主题",
            source_url="https://example.com",
            status=ArticleStatus.READY,
            quality_score=85.5,
            wechat_draft_id="test_draft_id"
        )
        
        assert article.summary == "文章摘要"
        assert article.source_topic == "测试主题"
        assert article.source_url == "https://example.com"
        assert article.status == ArticleStatus.READY
        assert article.quality_score == 85.5
        assert article.wechat_draft_id == "test_draft_id"
    
    def test_article_status_enum(self):
        """测试文章状态枚举"""
        assert ArticleStatus.DRAFT.value == "draft"
        assert ArticleStatus.GENERATING.value == "generating"
        assert ArticleStatus.READY.value == "ready"
        assert ArticleStatus.PUBLISHED.value == "published"
        assert ArticleStatus.FAILED.value == "failed"
    
    def test_article_repr(self):
        """测试文章字符串表示"""
        article = Article(
            title="测试文章",
            content="内容",
            status=ArticleStatus.DRAFT
        )
        # 注意：id可能为None，所以测试部分内容
        repr_str = repr(article)
        assert "Article" in repr_str
        assert "测试文章" in repr_str


class TestNewsItem:
    """新闻模型测试"""
    
    def test_create_news_item(self):
        """测试创建新闻"""
        news = NewsItem(
            title="测试新闻",
            url="https://example.com/news",
            source=NewsSource.ITHOME,
            source_name="IT之家"
        )
        
        assert news.title == "测试新闻"
        assert news.url == "https://example.com/news"
        assert news.source == NewsSource.ITHOME
        assert news.source_name == "IT之家"
    
    def test_news_with_all_fields(self):
        """测试包含所有字段的新闻"""
        news = NewsItem(
            title="完整新闻",
            summary="新闻摘要",
            url="https://example.com/news",
            source=NewsSource.ITHOME,
            source_name="IT之家",
            hot_score=95.5,
            cover_image_url="https://example.com/image.jpg"
        )
        
        assert news.summary == "新闻摘要"
        assert news.hot_score == 95.5
        assert news.cover_image_url == "https://example.com/image.jpg"
    
    def test_news_source_enum(self):
        """测试新闻源枚举"""
        assert NewsSource.ITHOME.value == "ithome"
        assert NewsSource.BAIDU.value == "baidu"
    
    def test_news_repr(self):
        """测试新闻字符串表示"""
        news = NewsItem(
            title="测试新闻",
            url="https://example.com/news",
            source=NewsSource.ITHOME,
            source_name="IT之家",
            hot_score=80.0
        )
        repr_str = repr(news)
        assert "NewsItem" in repr_str
        assert "测试新闻" in repr_str


class TestWeChatConfig:
    """微信配置模型测试"""
    
    def test_create_wechat_config(self):
        """测试创建微信配置"""
        config = WeChatConfig(
            app_id="wx1234567890",
            app_secret="secret123456"
        )

        assert config.app_id == "wx1234567890"
        assert config.app_secret == "secret123456"
        # 注意：default=True只在数据库层面生效，Python对象创建时不会自动设置

    def test_wechat_config_with_optional_fields(self):
        """测试带可选字段的微信配置"""
        config = WeChatConfig(
            app_id="wx1234567890",
            app_secret="secret123456",
            access_token="test_token",
            is_active=False
        )

        assert config.access_token == "test_token"
        assert config.is_active == False
    
    def test_wechat_config_repr(self):
        """测试微信配置字符串表示"""
        config = WeChatConfig(
            app_id="wx1234567890",
            app_secret="secret123456"
        )
        repr_str = repr(config)
        assert "WeChatConfig" in repr_str
        assert "wx1234567890" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])