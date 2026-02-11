"""
API端点测试
测试news、wechat、articles、unified_ai API
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.models.article import Article, ArticleStatus
from app.models.news import NewsSource
from datetime import datetime


client = TestClient(app)


class TestNewsAPI:
    """新闻API测试"""

    @patch('app.api.news.news_fetcher_service')
    def test_get_hotspots(self, mock_service):
        """测试获取热点新闻"""
        # 模拟返回数据
        mock_news = MagicMock()
        mock_news.id = 1
        mock_news.title = "测试新闻"
        mock_news.summary = "新闻摘要"
        mock_news.url = "https://example.com/news"
        mock_news.source = NewsSource.ITHOME
        mock_news.source_name = "IT之家"
        mock_news.hot_score = 85.0
        mock_news.published_at = datetime.now()
        mock_news.created_at = datetime.now()

        mock_service.fetch_news = AsyncMock(return_value=[mock_news])

        # 测试API
        response = client.get("/api/news/hotspots?limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["count"] == 1
        assert len(data["news_items"]) == 1
        assert data["news_items"][0]["title"] == "测试新闻"

    @patch('app.api.news.news_fetcher_service')
    def test_refresh_news(self, mock_service):
        """测试刷新热点新闻"""
        mock_service.fetch_news = AsyncMock(return_value=[])

        response = client.post("/api/news/refresh", json={
            "source": "ithome",
            "limit": 20
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["source"] == "ithome"


class TestWeChatAPI:
    """微信API测试"""

    def test_get_wechat_config(self):
        """测试获取微信配置"""
        response = client.get("/api/wechat/config")

        assert response.status_code == 200
        data = response.json()
        assert "app_id" in data
        assert "configured" in data

    @patch('app.api.wechat.wechat_service')
    def test_test_wechat_connection(self, mock_service):
        """测试微信连接"""
        mock_service.get_access_token = AsyncMock(return_value="test_token")

        response = client.post("/api/wechat/test")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    @patch('app.api.wechat.wechat_service')
    def test_publish_to_wechat(self, mock_service):
        """测试发布到微信"""
        mock_service.get_access_token = AsyncMock(return_value="test_token")
        mock_service.create_draft = AsyncMock(return_value="draft_id_123")

        response = client.post("/api/wechat/publish", json={
            "title": "测试文章",
            "content": "<p>内容</p>",
            "digest": "摘要",
            "author": "作者"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["draft_id"] == "draft_id_123"


class TestArticlesAPI:
    """文章API测试"""

    @patch('app.api.articles.get_db')
    def test_get_articles(self, mock_get_db):
        """测试获取文章列表"""
        # 模拟数据库会话
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        # 模拟查询结果
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = client.get("/api/articles/?skip=0&limit=20")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @patch('app.api.articles.get_db')
    def test_create_article(self, mock_get_db):
        """测试创建文章"""
        # 模拟数据库会话
        mock_db = AsyncMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_get_db.return_value = mock_db

        response = client.post("/api/articles/", json={
            "title": "测试文章",
            "content": "这是文章内容",
            "summary": "文章摘要",
            "status": "draft"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "测试文章"
        assert data["content"] == "这是文章内容"


class TestUnifiedAIAPI:
    """AI服务API测试"""

    @patch('app.api.unified_ai.ai_writer_service')
    def test_generate_titles(self, mock_service):
        """测试生成标题"""
        mock_service.generate_titles = AsyncMock(return_value=[
            {"title": "测试标题1", "click_rate": 85},
            {"title": "测试标题2", "click_rate": 80}
        ])

        response = client.post("/api/ai/generate-titles", json={
            "topic": "测试主题",
            "count": 2
        })

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "测试标题1"

    @patch('app.api.unified_ai.ai_writer_service')
    def test_generate_content(self, mock_service):
        """测试生成正文"""
        mock_service.generate_content = AsyncMock(return_value={
            "content": "生成的文章内容",
            "summary": "文章摘要",
            "quality_score": 85.0
        })

        response = client.post("/api/ai/generate-content", json={
            "topic": "测试主题",
            "title": "测试标题"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "生成的文章内容"
        assert data["quality_score"] == 85.0

    @patch('app.api.unified_ai.ai_writer_service')
    @patch('app.api.unified_ai.image_service')
    @patch('app.api.unified_ai.wechat_service')
    def test_auto_generate(self, mock_wechat, mock_image, mock_ai):
        """测试一键全自动生成"""
        # 模拟AI服务
        mock_ai.generate_titles = AsyncMock(return_value=[
            {"title": "自动生成的标题", "click_rate": 90}
        ])
        mock_ai.generate_content = AsyncMock(return_value={
            "content": "自动生成的内容",
            "summary": "自动生成的摘要",
            "quality_score": 88.0
        })

        # 模拟图片服务
        mock_image.search_image = AsyncMock(return_value="/path/to/image.jpg")

        # 模拟微信服务
        mock_wechat.get_access_token = AsyncMock(return_value="test_token")
        mock_wechat.upload_media = AsyncMock(return_value="media_id_123")
        mock_wechat.create_draft = AsyncMock(return_value="draft_id_456")

        response = client.post("/api/ai/auto-generate", json={
            "topic": "测试主题",
            "enable_wechat_publish": True
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "steps" in data
        assert "article" in data


class TestHealthAPI:
    """健康检查API测试"""

    def test_root_endpoint(self):
        """测试根端点"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data

    def test_health_endpoint(self):
        """测试健康检查端点"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @patch('app.api.health.get_db')
    def test_services_health(self, mock_get_db):
        """测试服务健康检查"""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_get_db.return_value = mock_db

        response = client.get("/api/health/services")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])