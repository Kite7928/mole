"""
Unit tests for WeChat Service.
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
from app.services.wechat_service import WeChatService


@pytest.fixture
def wechat_service():
    """Create WeChat service instance for testing."""
    with patch('app.services.wechat_service.settings') as mock_settings:
        mock_settings.WECHAT_APP_ID = "test_app_id"
        mock_settings.WECHAT_APP_SECRET = "test_app_secret"

        service = WeChatService()
        yield service


@pytest.fixture
def mock_token_response():
    """Mock WeChat access token response."""
    return {
        "access_token": "test_access_token_12345",
        "expires_in": 7200
    }


@pytest.fixture
def mock_upload_response():
    """Mock media upload response."""
    return {
        "media_id": "test_media_id_12345",
        "url": "https://example.com/media.jpg"
    }


@pytest.fixture
def mock_draft_response():
    """Mock draft creation response."""
    return {
        "media_id": "draft_media_id_12345"
    }


@pytest.fixture
def mock_publish_response():
    """Mock publish response."""
    return {
        "publish_id": "publish_id_12345",
        "msg_data_id": "msg_data_id_12345"
    }


class TestWeChatService:
    """Test cases for WeChatService."""

    def test_initialization(self, wechat_service):
        """Test service initialization."""
        assert wechat_service.app_id == "test_app_id"
        assert wechat_service.app_secret == "test_app_secret"
        assert wechat_service.access_token is None
        assert wechat_service.token_expires_at is None

    @pytest.mark.asyncio
    async def test_get_access_token_success(self, wechat_service, mock_token_response):
        """Test successful access token retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = mock_token_response
        mock_response.raise_for_status = Mock()

        wechat_service.http_client.get = AsyncMock(return_value=mock_response)

        token = await wechat_service.get_access_token()

        assert token == "test_access_token_12345"
        assert wechat_service.access_token == "test_access_token_12345"
        assert wechat_service.token_expires_at is not None

    @pytest.mark.asyncio
    async def test_get_access_token_uses_cache(self, wechat_service):
        """Test that cached token is used when still valid."""
        # Set token with future expiration
        wechat_service.access_token = "cached_token"
        wechat_service.token_expires_at = datetime.now() + timedelta(hours=1)

        token = await wechat_service.get_access_token()

        assert token == "cached_token"
        # Should not call HTTP client
        wechat_service.http_client.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_access_token_refreshes_expired(self, wechat_service, mock_token_response):
        """Test that expired token is refreshed."""
        # Set expired token
        wechat_service.access_token = "expired_token"
        wechat_service.token_expires_at = datetime.now() - timedelta(hours=1)

        mock_response = Mock()
        mock_response.json.return_value = mock_token_response
        mock_response.raise_for_status = Mock()
        wechat_service.http_client.get = AsyncMock(return_value=mock_response)

        token = await wechat_service.get_access_token()

        assert token == "test_access_token_12345"
        assert wechat_service.access_token == "test_access_token_12345"

    @pytest.mark.asyncio
    async def test_get_access_token_api_error(self, wechat_service):
        """Test handling of WeChat API error."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "errcode": 40001,
            "errmsg": "invalid credential"
        }
        mock_response.raise_for_status = Mock()

        wechat_service.http_client.get = AsyncMock(return_value=mock_response)

        with pytest.raises(Exception, match="WeChat API error"):
            await wechat_service.get_access_token()

    @pytest.mark.asyncio
    async def test_upload_media(self, wechat_service, mock_token_response, mock_upload_response, tmp_path):
        """Test uploading media file."""
        # Setup token
        wechat_service.access_token = "test_token"

        # Create test image file
        test_file = tmp_path / "test.jpg"
        test_file.write_bytes(b"fake image data")

        # Mock upload response
        mock_response = Mock()
        mock_response.json.return_value = mock_upload_response
        mock_response.raise_for_status = Mock()
        wechat_service.http_client.post = AsyncMock(return_value=mock_response)

        result = await wechat_service.upload_media(str(test_file), media_type="image")

        assert result["media_id"] == "test_media_id_12345"
        assert "url" in result

    @pytest.mark.asyncio
    async def test_upload_media_error(self, wechat_service):
        """Test handling upload error."""
        wechat_service.access_token = "test_token"

        mock_response = Mock()
        mock_response.json.return_value = {
            "errcode": 40004,
            "errmsg": "invalid media type"
        }
        mock_response.raise_for_status = Mock()
        wechat_service.http_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(Exception, match="Upload failed"):
            await wechat_service.upload_media("nonexistent.jpg")

    @pytest.mark.asyncio
    async def test_upload_image_from_url(self, wechat_service, mock_token_response, mock_upload_response):
        """Test uploading image from URL."""
        wechat_service.access_token = "test_token"

        # Mock image download
        download_response = Mock()
        download_response.content = b"image data"
        download_response.raise_for_status = Mock()

        # Mock upload response
        upload_response = Mock()
        upload_response.json.return_value = mock_upload_response
        upload_response.raise_for_status = Mock()

        wechat_service.http_client.get = AsyncMock(return_value=download_response)
        wechat_service.http_client.post = AsyncMock(return_value=upload_response)

        result = await wechat_service.upload_image_from_url("https://example.com/image.jpg")

        assert result["media_id"] == "test_media_id_12345"

    @pytest.mark.asyncio
    async def test_create_draft(self, wechat_service, mock_token_response, mock_draft_response):
        """Test creating article draft."""
        wechat_service.access_token = "test_token"

        articles = [
            {
                "title": "测试文章",
                "content": "文章内容",
                "author": "作者",
                "digest": "摘要"
            }
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_draft_response
        mock_response.raise_for_status = Mock()
        wechat_service.http_client.post = AsyncMock(return_value=mock_response)

        result = await wechat_service.create_draft(articles)

        assert result["media_id"] == "draft_media_id_12345"

    @pytest.mark.asyncio
    async def test_create_draft_multiple_articles(self, wechat_service, mock_draft_response):
        """Test creating draft with multiple articles."""
        wechat_service.access_token = "test_token"

        articles = [
            {
                "title": f"文章{i}",
                "content": f"内容{i}",
                "author": "作者",
                "digest": f"摘要{i}"
            }
            for i in range(3)
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_draft_response
        mock_response.raise_for_status = Mock()
        wechat_service.http_client.post = AsyncMock(return_value=mock_response)

        result = await wechat_service.create_draft(articles)

        assert result["media_id"] == "draft_media_id_12345"

    @pytest.mark.asyncio
    async def test_publish_article(self, wechat_service, mock_publish_response):
        """Test publishing article."""
        wechat_service.access_token = "test_token"

        mock_response = Mock()
        mock_response.json.return_value = mock_publish_response
        mock_response.raise_for_status = Mock()
        wechat_service.http_client.post = AsyncMock(return_value=mock_response)

        result = await wechat_service.publish_article("draft_media_id")

        assert result["publish_id"] == "publish_id_12345"
        assert result["msg_data_id"] == "msg_data_id_12345"

    @pytest.mark.asyncio
    async def test_get_publish_status(self, wechat_service):
        """Test getting publish status."""
        wechat_service.access_token = "test_token"

        mock_response = Mock()
        mock_response.json.return_value = {
            "publish_id": "publish_id_12345",
            "publish_status": 0,
            "article_id": "article_id_12345",
            "article_detail": {
                "articles": [
                    {
                        "title": "测试文章",
                        "url": "https://mp.weixin.qq.com/s/xxx"
                    }
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        wechat_service.http_client.post = AsyncMock(return_value=mock_response)

        result = await wechat_service.get_publish_status("publish_id_12345")

        assert result["publish_id"] == "publish_id_12345"
        assert result["publish_status"] == 0

    @pytest.mark.asyncio
    async def test_delete_draft(self, wechat_service):
        """Test deleting draft."""
        wechat_service.access_token = "test_token"

        mock_response = Mock()
        mock_response.json.return_value = {"errcode": 0}
        mock_response.raise_for_status = Mock()
        wechat_service.http_client.post = AsyncMock(return_value=mock_response)

        result = await wechat_service.delete_draft("draft_media_id")

        assert result["errcode"] == 0

    @pytest.mark.asyncio
    async def test_get_user_info(self, wechat_service):
        """Test getting account information."""
        wechat_service.access_token = "test_token"

        mock_response = Mock()
        mock_response.json.return_value = {
            "appid": "test_app_id",
            "account_type": 1,
            "principal_type": 1,
            "principal_name": "测试公众号",
            "signature": "公众号简介",
            "nickname": "测试公众号"
        }
        mock_response.raise_for_status = Mock()
        wechat_service.http_client.get = AsyncMock(return_value=mock_response)

        result = await wechat_service.get_user_info()

        assert result["appid"] == "test_app_id"
        assert result["nickname"] == "测试公众号"

    @pytest.mark.asyncio
    async def test_get_access_token_before_expiration(self, wechat_service, mock_token_response):
        """Test token refresh 5 minutes before expiration."""
        # Set token that will expire in 4 minutes
        wechat_service.access_token = "old_token"
        wechat_service.token_expires_at = datetime.now() + timedelta(minutes=4)

        mock_response = Mock()
        mock_response.json.return_value = mock_token_response
        mock_response.raise_for_status = Mock()
        wechat_service.http_client.get = AsyncMock(return_value=mock_response)

        token = await wechat_service.get_access_token()

        assert token == "test_access_token_12345"
        # Should have refreshed the token
        wechat_service.http_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self, wechat_service):
        """Test closing the service."""
        wechat_service.http_client.aclose = AsyncMock()

        await wechat_service.close()

        wechat_service.http_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_media_video(self, wechat_service, mock_upload_response, tmp_path):
        """Test uploading video media."""
        wechat_service.access_token = "test_token"

        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"fake video data")

        mock_response = Mock()
        mock_response.json.return_value = mock_upload_response
        mock_response.raise_for_status = Mock()
        wechat_service.http_client.post = AsyncMock(return_value=mock_response)

        result = await wechat_service.upload_media(str(test_file), media_type="video")

        assert result["media_id"] == "test_media_id_12345"

    @pytest.mark.asyncio
    async def test_create_draft_with_cover(self, wechat_service, mock_draft_response):
        """Test creating draft with cover image."""
        wechat_service.access_token = "test_token"

        articles = [
            {
                "title": "测试文章",
                "content": "文章内容",
                "author": "作者",
                "digest": "摘要",
                "thumb_media_id": "cover_media_id",
                "show_cover_pic": 1
            }
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_draft_response
        mock_response.raise_for_status = Mock()
        wechat_service.http_client.post = AsyncMock(return_value=mock_response)

        result = await wechat_service.create_draft(articles)

        assert result["media_id"] == "draft_media_id_12345"