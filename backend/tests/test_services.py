"""
服务层测试
测试热点抓取服务、微信服务、图片服务
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.news_fetcher import NewsFetcherService
from app.services.wechat_service import WeChatPublishService
from app.services.image_generation_service import ImageGenerationService
from app.models.news import NewsSource


class TestNewsFetcherService:
    """热点抓取服务测试"""
    
    @pytest.fixture
    def service(self):
        """创建热点抓取服务实例"""
        return NewsFetcherService()
    
    @pytest.mark.asyncio
    async def test_fetch_news(self, service):
        """测试抓取新闻"""
        # 模拟HTTP响应
        mock_response = MagicMock()
        mock_response.text = '''<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
          <channel>
            <item>
              <title>测试新闻标题</title>
              <description>新闻摘要</description>
              <link>https://example.com/news</link>
            </item>
          </channel>
        </rss>'''
        
        with patch.object(service.http_client, 'get', return_value=mock_response):
            news_items = await service.fetch_news(NewsSource.ITHOME, limit=10)
            
            assert len(news_items) > 0
            assert news_items[0].title == "测试新闻标题"
            assert news_items[0].url == "https://example.com/news"


class TestWeChatService:
    """微信服务测试"""

    @pytest.fixture
    def service(self):
        """创建微信服务实例"""
        return WeChatPublishService()
    
    @pytest.mark.asyncio
    async def test_get_access_token(self, service):
        """测试获取access_token"""
        # 模拟微信API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_token_12345",
            "expires_in": 7200
        }
        
        with patch.object(service.http_client, 'get', return_value=mock_response):
            token = await service.get_access_token("wx123456", "secret123")
            
            assert token == "test_token_12345"
    
    @pytest.mark.asyncio
    async def test_create_draft(self, service):
        """测试创建草稿"""
        # 模拟微信API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "media_id": "draft_id_12345"
        }
        
        with patch.object(service.http_client, 'post', return_value=mock_response):
            draft_id = await service.create_draft(
                access_token="test_token",
                title="测试文章",
                author="作者",
                digest="摘要",
                content="<p>内容</p>",
                cover_media_id="media_id"
            )
            
            assert draft_id == "draft_id_12345"


class TestImageService:
    """图片服务测试"""

    @pytest.fixture
    def service(self):
        """创建图片服务实例"""
        return ImageGenerationService()
    
    @pytest.mark.asyncio
    async def test_download_image(self, service):
        """测试下载图片"""
        # 模拟HTTP响应
        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(service.http_client, 'get', return_value=mock_response):
            with patch('aiofiles.open', create=True) as mock_open:
                mock_file = AsyncMock()
                mock_open.return_value.__aenter__.return_value = mock_file
                
                path = await service.download_image("https://example.com/image.jpg")
                
                assert path is not None
                mock_file.write.assert_called_once()
    
    def test_calculate_hot_score(self, service):
        """测试计算热度分数"""
        from datetime import datetime, timedelta
        
        # 测试最新新闻
        now = datetime.now()
        score = service._calculate_hot_score(now)
        assert score >= 90
        
        # 测试旧新闻
        old_time = now - timedelta(hours=100)
        score = service._calculate_hot_score(old_time)
        assert score < 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])