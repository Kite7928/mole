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
            verify=True,  # 启用SSL证书验证（安全）
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

    async def upload_article_image(self, access_token: str, file_path: str) -> str:
        """上传正文图片并返回微信可访问URL。"""
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}"

            with open(file_path, 'rb') as file_obj:
                files = {"media": file_obj}
                response = await self.http_client.post(url, files=files)
                response.raise_for_status()
                data = response.json()

            if "url" not in data:
                errcode = data.get('errcode', 'unknown')
                errmsg = data.get('errmsg', '未知错误')
                raise ValueError(f"上传正文图片失败: 错误码={errcode}, 消息={errmsg}")

            return data["url"]
        except Exception as e:
            logger.error(f"上传正文图片失败: {str(e)}")
            raise ValueError(f"上传正文图片失败: {str(e)}")

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
            import os
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise ValueError(f"文件不存在: {file_path}")
            
            # 检查文件大小（微信限制10MB）
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:
                raise ValueError(f"文件过大: {file_size}字节，微信限制10MB")
            
            logger.info(f"上传永久素材: {file_path}, 大小: {file_size}字节, 类型: {media_type}")
            
            with open(file_path, 'rb') as f:
                files = {"media": f}

                if description:
                    files["description"] = (None, json.dumps(description, ensure_ascii=False), 'application/json')

                response = await self.http_client.post(url, files=files)
            
            # 记录响应状态
            logger.info(f"微信API响应状态: {response.status_code}")
            
            # 尝试解析错误信息
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"微信API返回错误: {response.status_code}, 响应: {error_text}")
                raise ValueError(f"微信API错误 {response.status_code}: {error_text}")
            
            data = response.json()
            logger.info(f"微信API响应数据: {data}")

            if "media_id" not in data:
                errcode = data.get('errcode', 'unknown')
                errmsg = data.get('errmsg', '未知错误')
                raise ValueError(f"上传永久素材失败: 错误码={errcode}, 消息={errmsg}")

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
            # 微信字段限制（按字符数）
            # 标题：限制64字符
            if len(title) > 64:
                logger.warning(f"标题过长({len(title)}字符)，截断为64字符")
                title = title[:64]
            
            # 作者：限制8字符
            if len(author) > 8:
                logger.warning(f"作者过长({len(author)}字符)，截断为8字符")
                author = author[:8]
            
            # 摘要：限制120字符
            if len(digest) > 120:
                logger.warning(f"摘要过长({len(digest)}字符)，截断为120字符")
                digest = digest[:117] + "..."
            
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
            logger.info(f"标题长度: {len(title)} 字符, 内容: {repr(title)}")

            # 使用与成功脚本相同的编码方式
            import json
            headers = {"Content-Type": "application/json; charset=utf-8"}
            json_data = json.dumps(data, ensure_ascii=False)
            response = await self.http_client.post(url, content=json_data.encode('utf-8'), headers=headers)
            
            # 记录响应状态
            logger.info(f"微信草稿API响应状态: {response.status_code}")
            
            # 尝试解析错误信息
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"微信草稿API返回错误: {response.status_code}, 响应: {error_text}")
                raise ValueError(f"微信草稿API错误 {response.status_code}: {error_text}")
            
            result = response.json()
            logger.info(f"创建草稿响应: {result}")

            if "media_id" not in result:
                errcode = result.get('errcode', 'unknown')
                errmsg = result.get('errmsg', '未知错误')
                logger.error(f"创建草稿失败: 错误码={errcode}, 消息={errmsg}")
                raise ValueError(f"创建草稿失败: 错误码={errcode}, 消息={errmsg}")

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

    def _simple_markdown_to_html(self, markdown_content: str) -> str:
        """简单的 Markdown 转 HTML（基于成功脚本的逻辑）"""
        import re
        
        html = markdown_content
        
        # 转换标题
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # 转换粗体
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # 转换列表
        html = re.sub(r'^\* (.*?)$', r'<p>\1</p>', html, flags=re.MULTILINE)
        html = re.sub(r'^- (.*?)$', r'<p>\1</p>', html, flags=re.MULTILINE)
        
        # 转换段落
        html = re.sub(r'\n\n', '</p><p>', html)
        
        # 包装在 section 标签中
        html = f'<section><p>{html}</p></section>'
        
        return html
    
    async def publish_from_markdown_simple(
        self,
        app_id: str,
        app_secret: str,
        title: str,
        author: str,
        markdown_content: str,
        summary: str = "",
        cover_image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        从 Markdown 发布文章（使用简单转换逻辑）
        
        Args:
            app_id: 公众号AppID
            app_secret: 公众号AppSecret
            title: 标题
            author: 作者
            markdown_content: Markdown内容
            summary: 摘要（可选）
            cover_image_path: 封面图片路径（可选）
            
        Returns:
            发布结果
        """
        try:
            logger.info(f"开始发布文章到微信（简单转换）: {title}")
            
            # 1. 获取access_token
            access_token = await self.get_access_token(app_id, app_secret)
            logger.info("获取access_token成功")
            
            # 2. 处理封面图
            cover_media_id = ""
            if cover_image_path and Path(cover_image_path).exists():
                try:
                    cover_media_id = await self.upload_permanent_material(
                        access_token=access_token,
                        media_type="thumb",
                        file_path=cover_image_path,
                        description={"introduction": summary or title}
                    )
                    logger.info(f"封面图上传成功: {cover_media_id}")
                except Exception as img_error:
                    logger.warning(f"上传封面图失败: {img_error}")
            
            # 3. 如果没有封面图，生成默认封面
            if not cover_media_id:
                from PIL import Image, ImageDraw, ImageFont
                import uuid
                
                img = Image.new('RGB', (900, 500), color='#4A90E2')
                draw = ImageDraw.Draw(img)
                
                try:
                    font = ImageFont.load_default()
                    title_text = title[:20] if title else "文章封面"
                    text_bbox = draw.textbbox((0, 0), title_text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    x = (900 - text_width) / 2
                    y = 250
                    draw.text((x, y), title_text, fill='white', font=font)
                except:
                    pass
                
                temp_image_path = f"./uploads/temp_cover_{uuid.uuid4().hex[:8]}.jpg"
                Path("./uploads").mkdir(exist_ok=True)
                img.save(temp_image_path, 'JPEG')
                
                cover_media_id = await self.upload_permanent_material(
                    access_token=access_token,
                    media_type="thumb",
                    file_path=temp_image_path,
                    description={"introduction": summary or title}
                )
                logger.info(f"默认封面图上传成功: {cover_media_id}")
            
            # 4. 转换Markdown为HTML（使用简单转换）
            html_content = self._simple_markdown_to_html(markdown_content)
            logger.info(f"内容已转换为HTML，长度: {len(html_content)}")
            
            # 5. 处理摘要（限制120字）
            digest = summary if summary else markdown_content[:120].replace("\n", " ").strip()
            if len(digest) > 120:
                digest = digest[:117] + '...'
            
            # 6. 创建草稿
            draft_id = await self.create_draft(
                access_token=access_token,
                title=title,
                author=author,
                digest=digest,
                content=html_content,
                cover_media_id=cover_media_id
            )
            
            logger.info(f"微信草稿创建成功: {draft_id}")
            
            return {
                "success": True,
                "draft_id": draft_id,
                "message": "发布到微信公众号草稿箱成功"
            }
            
        except Exception as e:
            logger.error(f"发布失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def close(self):
        """关闭HTTP客户端"""
        await self.http_client.aclose()


# 全局实例
wechat_service = WeChatPublishService()
