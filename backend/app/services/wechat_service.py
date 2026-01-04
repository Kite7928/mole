from typing import Optional, Dict, Any, List
import httpx
from datetime import datetime, timedelta
from ..core.config import settings
from ..core.logger import logger


class WeChatService:
    """
    WeChat official account API service.
    """

    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None):
        self.app_id = app_id or settings.WECHAT_APP_ID
        self.app_secret = app_secret or settings.WECHAT_APP_SECRET
        self.access_token = None
        self.token_expires_at = None
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def get_access_token(self) -> str:
        """
        Get WeChat access token, caching it until expiration.
        """
        # Check if token is still valid
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        # Fetch new token
        try:
            url = "https://api.weixin.qq.com/cgi-bin/token"
            params = {
                "grant_type": "client_credential",
                "appid": self.app_id,
                "secret": self.app_secret
            }

            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "errcode" in data:
                logger.error(f"WeChat API error: {data}")
                raise Exception(f"WeChat API error: {data.get('errmsg', 'Unknown error')}")

            self.access_token = data["access_token"]
            expires_in = data.get("expires_in", 7200)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # Refresh 5 minutes before expiration

            logger.info("WeChat access token refreshed successfully")
            return self.access_token

        except Exception as e:
            logger.error(f"Error getting WeChat access token: {str(e)}")
            raise

    async def upload_media(
        self,
        file_path: str,
        media_type: str = "image"
    ) -> Dict[str, Any]:
        """
        Upload media file to WeChat server.

        Args:
            file_path: Path to the media file
            media_type: Type of media (image, video, voice, thumb)

        Returns:
            Dict containing media_id and other metadata
        """
        try:
            access_token = await self.get_access_token()
            url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type={media_type}"

            with open(file_path, "rb") as f:
                files = {"media": f}
                response = await self.http_client.post(url, files=files)
                response.raise_for_status()
                data = response.json()

            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"WeChat upload error: {data}")
                raise Exception(f"Upload failed: {data.get('errmsg', 'Unknown error')}")

            logger.info(f"Media uploaded successfully: {data.get('media_id')}")
            return data

        except Exception as e:
            logger.error(f"Error uploading media: {str(e)}")
            raise

    async def upload_image_from_url(
        self,
        image_url: str
    ) -> Dict[str, Any]:
        """
        Download image from URL and upload to WeChat.

        Args:
            image_url: URL of the image to upload

        Returns:
            Dict containing media_id
        """
        try:
            # Download image
            response = await self.http_client.get(image_url)
            response.raise_for_status()
            image_data = response.content

            # Upload to WeChat
            access_token = await self.get_access_token()
            url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"

            files = {"media": ("image.jpg", image_data, "image/jpeg")}
            response = await self.http_client.post(url, files=files)
            response.raise_for_status()
            data = response.json()

            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"WeChat upload error: {data}")
                raise Exception(f"Upload failed: {data.get('errmsg', 'Unknown error')}")

            logger.info(f"Image uploaded successfully: {data.get('media_id')}")
            return data

        except Exception as e:
            logger.error(f"Error uploading image from URL: {str(e)}")
            raise

    async def create_draft(
        self,
        articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create article draft in WeChat.

        Args:
            articles: List of article dicts with title, content, author, digest, etc.

        Returns:
            Dict containing media_id (draft_id)
        """
        try:
            access_token = await self.get_access_token()
            url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"

            payload = {
                "articles": articles
            }

            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"WeChat draft creation error: {data}")
                raise Exception(f"Draft creation failed: {data.get('errmsg', 'Unknown error')}")

            logger.info(f"Draft created successfully: {data.get('media_id')}")
            return data

        except Exception as e:
            logger.error(f"Error creating draft: {str(e)}")
            raise

    async def publish_article(
        self,
        media_id: str
    ) -> Dict[str, Any]:
        """
        Publish article from draft.

        Args:
            media_id: Draft media_id

        Returns:
            Dict containing publish_id and article_id
        """
        try:
            access_token = await self.get_access_token()
            url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"

            payload = {
                "media_id": media_id
            }

            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"WeChat publish error: {data}")
                raise Exception(f"Publish failed: {data.get('errmsg', 'Unknown error')}")

            logger.info(f"Article published successfully: {data.get('publish_id')}")
            return data

        except Exception as e:
            logger.error(f"Error publishing article: {str(e)}")
            raise

    async def get_publish_status(
        self,
        publish_id: str
    ) -> Dict[str, Any]:
        """
        Get article publish status.

        Args:
            publish_id: Publish ID returned from submit

        Returns:
            Dict containing publish status and article_id if published
        """
        try:
            access_token = await self.get_access_token()
            url = f"https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={access_token}"

            payload = {
                "publish_id": publish_id
            }

            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"WeChat get status error: {data}")
                raise Exception(f"Get status failed: {data.get('errmsg', 'Unknown error')}")

            return data

        except Exception as e:
            logger.error(f"Error getting publish status: {str(e)}")
            raise

    async def delete_draft(
        self,
        media_id: str
    ) -> Dict[str, Any]:
        """
        Delete article draft.

        Args:
            media_id: Draft media_id

        Returns:
            Dict containing result
        """
        try:
            access_token = await self.get_access_token()
            url = f"https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={access_token}"

            payload = {
                "media_id": media_id
            }

            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"WeChat delete draft error: {data}")
                raise Exception(f"Delete draft failed: {data.get('errmsg', 'Unknown error')}")

            logger.info(f"Draft deleted successfully: {media_id}")
            return data

        except Exception as e:
            logger.error(f"Error deleting draft: {str(e)}")
            raise

    async def get_user_info(self) -> Dict[str, Any]:
        """
        Get WeChat account information.
        """
        try:
            access_token = await self.get_access_token()
            url = f"https://api.weixin.qq.com/cgi-bin/account/getaccountbasicinfo?access_token={access_token}"

            response = await self.http_client.get(url)
            response.raise_for_status()
            data = response.json()

            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"WeChat get account info error: {data}")
                raise Exception(f"Get account info failed: {data.get('errmsg', 'Unknown error')}")

            return data

        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            raise

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()


# Global instance
wechat_service = WeChatService()