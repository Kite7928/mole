"""
微信发布服务（增强版）
支持自动发布到微信公众号，包括图文消息、草稿、定时发布等
"""

from typing import Optional, Dict, Any, List
import httpx
from datetime import datetime
from ..core.config import settings
from ..core.logger import logger
from ..models.wechat import WeChatConfig
from .markdown_converter import markdown_converter


class WeChatPublishService:
    """微信发布服务 - 增强版"""

    def __init__(self):
        # 增强HTTP客户端配置
        # 明确禁用代理，避免代理配置问题
        self.http_client = httpx.AsyncClient(
            verify=False,  # 避免SSL证书验证问题
            timeout=httpx.Timeout(120.0, connect=10.0, read=60.0, write=60.0),
            follow_redirects=True,
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10,
                keepalive_expiry=30.0
            ),
            # 明确禁用代理
            trust_env=False
        )

    async def get_access_token(self, app_id: str, app_secret: str) -> str:
        """
        获取微信access_token

        Args:
            app_id: 公众号AppID
            app_secret: 公众号AppSecret

        Returns:
            access_token
        """
        try:
            # 使用域名连接，不要使用IP地址（SSL证书需要域名验证）
            url = "https://api.weixin.qq.com/cgi-bin/token"
            params = {
                "grant_type": "client_credential",
                "appid": app_id,
                "secret": app_secret
            }

            logger.info(f"开始获取微信access_token: {url}")
            logger.info(f"AppID: {app_id}")

            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            logger.info(f"获取access_token响应: {data}")

            if "access_token" not in data:
                raise ValueError(f"获取access_token失败: {data}")

            logger.info(f"获取access_token成功")
            return data["access_token"]

        except httpx.ConnectError as e:
            logger.error(f"连接微信API失败: {str(e)}")
            logger.error(f"请检查网络连接和代理配置")
            raise ValueError(f"无法连接到微信API服务器: {str(e)}")
        except httpx.TimeoutException as e:
            logger.error(f"连接微信API超时: {str(e)}")
            raise ValueError(f"连接微信API超时，请重试: {str(e)}")
        except Exception as e:
            logger.error(f"获取access_token失败: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"请检查微信公众号AppID和AppSecret配置是否正确")
            raise ValueError(f"获取微信access_token失败: {str(e)}")

    async def upload_media(
        self,
        access_token: str,
        media_type: str,
        file_path: str
    ) -> str:
        """
        上传临时素材

        Args:
            access_token: access_token
            media_type: 媒体类型（image/voice/video/thumb）
            file_path: 文件路径

        Returns:
            media_id
        """
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type={media_type}"

            with open(file_path, 'rb') as f:
                files = {"media": f}
                response = await self.http_client.post(url, files=files)
                response.raise_for_status()
                data = response.json()

            if "media_id" not in data:
                raise ValueError(f"上传素材失败: {data}")

            return data["media_id"]

        except Exception as e:
            logger.error(f"上传素材失败: {str(e)}")
            logger.error(f"文件路径: {file_path}, 媒体类型: {media_type}")
            logger.error(f"错误类型: {type(e).__name__}")
            raise ValueError(f"上传微信素材失败: {str(e)}")

    async def upload_permanent_material(
        self,
        access_token: str,
        media_type: str,
        file_path: str,
        description: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        上传永久素材

        Args:
            access_token: access_token
            media_type: 媒体类型
            file_path: 文件路径
            description: 描述信息

        Returns:
            media_id
        """
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type={media_type}"

            import json
            files = {
                "media": open(file_path, 'rb')
            }

            if description:
                files["description"] = (None, json.dumps(description), 'application/json')

            response = await self.http_client.post(url, files=files)
            response.raise_for_status()
            data = response.json()

            if "media_id" not in data:
                raise ValueError(f"上传永久素材失败: {data}")

            return data["media_id"]

        except Exception as e:
            logger.error(f"上传永久素材失败: {str(e)}")
            logger.error(f"文件路径: {file_path}, 媒体类型: {media_type}")
            logger.error(f"错误类型: {type(e).__name__}")
            raise ValueError(f"上传微信永久素材失败: {str(e)}")

    async def create_draft(
        self,
        access_token: str,
        title: str,
        author: str,
        digest: str,
        content: str,
        cover_media_id: str,
        content_source_url: str = "",
        need_open_comment: int = 0,
        only_fans_can_comment: int = 0
    ) -> str:
        """
        创建草稿

        Args:
            access_token: access_token
            title: 标题
            author: 作者
            digest: 摘要
            content: 正文内容（HTML格式）
            cover_media_id: 封面图media_id
            content_source_url: 原文链接
            need_open_comment: 是否开启评论
            only_fans_can_comment: 是否仅粉丝可评论

        Returns:
            draft_id (media_id)
        """
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"

            articles = [{
                "title": title,
                "author": author,
                "digest": digest,
                "content": content,
                "content_source_url": content_source_url,
                "thumb_media_id": cover_media_id,
                "show_cover_pic": 1,
                "need_open_comment": need_open_comment,
                "only_fans_can_comment": only_fans_can_comment
            }]

            data = {"articles": articles}
            
            logger.info(f"开始创建微信草稿: {title}")
            logger.info(f"草稿URL: {url}")
            logger.info(f"封面图media_id: {cover_media_id}")
            logger.info(f"内容长度: {len(content)} 字符")

            response = await self.http_client.post(url, json=data)
            response.raise_for_status()
            result = response.json()

            logger.info(f"创建草稿响应: {result}")

            if "media_id" not in result:
                raise ValueError(f"创建草稿失败: {result}")

            logger.info(f"创建草稿成功: {result['media_id']}")
            return result["media_id"]

        except httpx.ConnectError as e:
            logger.error(f"连接微信API失败: {str(e)}")
            logger.error(f"请检查网络连接和代理配置")
            raise ValueError(f"无法连接到微信API服务器: {str(e)}")
        except httpx.TimeoutException as e:
            logger.error(f"连接微信API超时: {str(e)}")
            raise ValueError(f"连接微信API超时，请重试: {str(e)}")
        except Exception as e:
            logger.error(f"创建草稿失败: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"请检查微信API配置和草稿内容格式")
            raise ValueError(f"创建微信草稿失败: {str(e)}")

    async def publish_article(
        self,
        access_token: str,
        draft_id: str,
        is_to_all: bool = False,
        tag_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发布文章（从草稿）

        Args:
            access_token: access_token
            draft_id: 草稿ID
            is_to_all: 是否群发给所有人
            tag_id: 标签ID（用于分组发送）

        Returns:
            发布结果
        """
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"

            data = {
                "media_id": draft_id
            }

            # 如果不是群发给所有人，需要设置标签
            if not is_to_all:
                if tag_id is None:
                    raise ValueError("非群发需要指定tag_id")
                data["send_ignore_reprint"] = 0

            response = await self.http_client.post(url, json=data)
            response.raise_for_status()
            result = response.json()

            if "msg_id" not in result:
                raise ValueError(f"发布文章失败: {result}")

            return result

        except Exception as e:
            logger.error(f"发布文章失败: {str(e)}")
            logger.error(f"草稿ID: {draft_id}, 错误类型: {type(e).__name__}")
            raise ValueError(f"发布微信文章失败: {str(e)}")

    async def get_publish_status(
        self,
        access_token: str,
        publish_id: str
    ) -> Dict[str, Any]:
        """
        获取发布状态

        Args:
            access_token: access_token
            publish_id: 发布ID

        Returns:
            发布状态
        """
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={access_token}"

            data = {"publish_id": publish_id}
            response = await self.http_client.post(url, json=data)
            response.raise_for_status()
            result = response.json()

            return result

        except Exception as e:
            logger.error(f"获取发布状态失败: {str(e)}")
            logger.error(f"发布ID: {publish_id}, 错误类型: {type(e).__name__}")
            raise ValueError(f"获取微信文章发布状态失败: {str(e)}")

    async def delete_draft(
        self,
        access_token: str,
        draft_id: str
    ) -> bool:
        """
        删除草稿

        Args:
            access_token: access_token
            draft_id: 草稿ID

        Returns:
            是否成功
        """
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={access_token}"

            data = {"media_id": draft_id}
            response = await self.http_client.post(url, json=data)
            response.raise_for_status()
            result = response.json()

            return result.get("errcode") == 0

        except Exception as e:
            logger.error(f"删除草稿失败: {str(e)}")
            logger.error(f"草稿ID: {draft_id}, 错误类型: {type(e).__name__}")
            raise ValueError(f"删除微信草稿失败: {str(e)}")

    async def auto_publish(
        self,
        app_id: str,
        app_secret: str,
        title: str,
        author: str,
        digest: str,
        content: str,
        cover_image_path: str,
        is_to_all: bool = False,
        tag_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        自动发布文章（完整流程）

        Args:
            app_id: 公众号AppID
            app_secret: 公众号AppSecret
            title: 标题
            author: 作者
            digest: 摘要
            content: 正文内容（HTML格式）
            cover_image_path: 封面图片路径
            is_to_all: 是否群发给所有人
            tag_id: 标签ID

        Returns:
            发布结果
        """
        try:
            logger.info(f"开始自动发布文章: {title}")

            # 1. 获取access_token
            access_token = await self.get_access_token(app_id, app_secret)
            logger.info("获取access_token成功")

            # 2. 上传封面图
            cover_media_id = await self.upload_permanent_material(
                access_token,
                "image",
                cover_image_path,
                {"introduction": digest}
            )
            logger.info(f"上传封面图成功: {cover_media_id}")

            # 3. 创建草稿
            draft_id = await self.create_draft(
                access_token,
                title,
                author,
                digest,
                content,
                cover_media_id
            )
            logger.info(f"创建草稿成功: {draft_id}")

            # 4. 发布文章
            publish_result = await self.publish_article(
                access_token,
                draft_id,
                is_to_all=is_to_all,
                tag_id=tag_id
            )
            logger.info(f"发布文章成功: {publish_result.get('msg_id')}")

            return {
                "success": True,
                "draft_id": draft_id,
                "publish_id": publish_result.get("publish_id"),
                "msg_id": publish_result.get("msg_id"),
                "msg_data_id": publish_result.get("msg_data_id")
            }

        except Exception as e:
            logger.error(f"自动发布失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def auto_publish_from_markdown(
        self,
        app_id: str,
        app_secret: str,
        title: str,
        author: str,
        markdown_content: str,
        cover_image_path: str,
        is_to_all: bool = False,
        tag_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        从Markdown自动发布文章

        Args:
            app_id: 公众号AppID
            app_secret: 公众号AppSecret
            title: 标题
            author: 作者
            markdown_content: Markdown内容
            cover_image_path: 封面图片路径
            is_to_all: 是否群发给所有人
            tag_id: 标签ID

        Returns:
            发布结果
        """
        try:
            # 1. 转换Markdown为HTML（使用微信样式）
            html_content = await markdown_converter.convert_to_wechat_html(markdown_content)

            # 2. 生成摘要
            digest = markdown_content[:120].replace("\n", " ").strip()

            # 3. 自动发布
            result = await self.auto_publish(
                app_id,
                app_secret,
                title,
                author,
                digest,
                html_content,
                cover_image_path,
                is_to_all,
                tag_id
            )

            return result

        except Exception as e:
            logger.error(f"从Markdown自动发布失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def close(self):
        """关闭HTTP客户端"""
        await self.http_client.aclose()


# 全局实例
wechat_service = WeChatPublishService()
