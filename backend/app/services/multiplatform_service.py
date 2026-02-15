"""
多平台发布服务 - 增强版
基于 Mixpost 核心逻辑，支持知乎、掘金、头条等多平台文章发布
集成数据库持久化、错误重试、内容转换等功能
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from datetime import timedelta
import json
import asyncio
import hashlib
import os
import tempfile
from pathlib import Path
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import func

from ..core.logger import logger
from ..core.exceptions import NotImplementedError
from ..models.publish_platform import (
    PlatformType, PublishStatus, PlatformConfig,
    PublishRecord, PublishTask, PLATFORM_INFO
)
from ..models.article import Article
from ..types import PublishResult, ArticleContent, PlatformStats
from .async_task_queue import task_queue
from .markdown_converter import markdown_converter


class BasePublisher(ABC):
    """发布器基类 - Mixpost 核心架构"""
    
    def __init__(self, platform: PlatformType, config: PlatformConfig):
        self.platform = platform
        self.config = config
        self.platform_info = PLATFORM_INFO.get(platform, {})
        self.max_retries = 3
        self.retry_delay = 5  # 秒
        
    @abstractmethod
    async def login(self, credentials: Optional[Dict[str, str]] = None) -> bool:
        """登录平台"""
        pass
    
    @abstractmethod
    async def publish(self, article: ArticleContent, db: AsyncSession) -> PublishResult:
        """发布文章"""
        pass
    
    @abstractmethod
    async def check_login_status(self) -> bool:
        """检查登录状态"""
        pass
    
    @abstractmethod
    async def fetch_stats(self, platform_article_id: str) -> Optional[PlatformStats]:
        """获取文章统计数据"""
        pass
    
    async def validate_content(self, article: ArticleContent) -> tuple[bool, str]:
        """验证内容是否符合平台要求"""
        # 基础验证
        if not article.title or len(article.title) < 5:
            return False, "标题不能为空且至少5个字符"
        
        if not article.content or len(article.content) < 100:
            return False, "内容不能为空且至少100个字符"
            
        # 平台特定验证
        max_title_length = self.platform_info.get('max_title_length', 100)
        if len(article.title) > max_title_length:
            return False, f"标题超过{max_title_length}字符限制"
            
        return True, ""
    
    def convert_content(self, article: ArticleContent) -> ArticleContent:
        """转换内容格式以适应平台要求"""
        support_markdown = self.platform_info.get('support_markdown', False)
        support_html = self.platform_info.get('support_html', False)
        
        # 根据平台支持格式转换内容
        if not support_html and support_markdown:
            # 需要将HTML转为Markdown
            article.content = self._html_to_markdown(article.content)
        elif support_html and not support_markdown:
            # 需要将Markdown转为HTML
            article.content = self._markdown_to_html(article.content)
        
        # 处理内容中的图片
        article.content = self._process_content_images(article.content)
            
        return article
    
    def _process_content_images(self, content: str) -> str:
        """
        处理内容中的图片标签
        可以根据平台要求调整图片尺寸、格式等
        """
        import re
        from pathlib import Path
        
        # 查找所有图片标签
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        
        def process_img_tag(match):
            img_tag = match.group(0)
            src = match.group(1)
            
            # 如果图片路径是相对路径，转换为绝对路径
            if src and not src.startswith(('http://', 'https://', 'data:')):
                if src.startswith('/uploads/'):
                    # 已经是正确的格式
                    return img_tag
                elif src.startswith('uploads/'):
                    # 添加前导斜杠
                    new_src = f"/{src}"
                    return img_tag.replace(src, new_src)
            
            return img_tag
        
        return re.sub(img_pattern, process_img_tag, content)
    
    def _html_to_markdown(self, html_content: str) -> str:
        """HTML转Markdown"""
        try:
            import html2text
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.body_width = 0  # 不自动换行
            return h.handle(html_content)
        except ImportError:
            logger.warning("html2text库未安装，使用简单转换")
            # 简单替换
            content = html_content
            content = content.replace('<h1>', '# ').replace('</h1>', '\n\n')
            content = content.replace('<h2>', '## ').replace('</h2>', '\n\n')
            content = content.replace('<h3>', '### ').replace('</h3>', '\n\n')
            content = content.replace('<p>', '').replace('</p>', '\n\n')
            content = content.replace('<strong>', '**').replace('</strong>', '**')
            content = content.replace('<em>', '*').replace('</em>', '*')
            content = content.replace('<br>', '\n')
            return content
    
    def _markdown_to_html(self, md_content: str) -> str:
        """Markdown转HTML"""
        try:
            import markdown
            return markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'nl2br'])
        except ImportError:
            logger.warning("markdown库未安装，返回原始内容")
            return md_content
    
    async def publish_with_retry(
        self, 
        article: ArticleContent, 
        db: AsyncSession,
        max_retries: Optional[int] = None
    ) -> PublishResult:
        """带重试的发布"""
        retries = max_retries or self.max_retries
        
        for attempt in range(retries):
            try:
                # 检查登录状态
                if not await self.check_login_status():
                    await self.login()
                
                # 验证内容
                valid, error = await self.validate_content(article)
                if not valid:
                    return PublishResult(
                        success=False,
                        platform=self.platform,
                        message=error
                    )
                
                # 转换内容
                article = self.convert_content(article)
                
                # 发布
                result = await self.publish(article, db)
                
                # 如果成功或不需要重试，直接返回
                if result.success or not result.need_retry:
                    return result
                
                # 需要重试
                if attempt < retries - 1:
                    delay = result.retry_after or self.retry_delay
                    logger.warning(f"{self.platform.value} 发布失败，{delay}秒后重试 ({attempt + 1}/{retries})")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{self.platform.value} 发布失败，已达最大重试次数")
                    return result
                    
            except Exception as e:
                logger.error(f"{self.platform.value} 发布异常: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    return PublishResult(
                        success=False,
                        platform=self.platform,
                        message=f"发布异常: {str(e)}",
                        need_retry=False
                    )
        
        return PublishResult(
            success=False,
            platform=self.platform,
            message="发布失败，已达最大重试次数"
        )


class ZhihuPublisher(BasePublisher):
    """知乎发布器"""
    
    def __init__(self, config: PlatformConfig):
        super().__init__(PlatformType.ZHIHU, config)
        self.base_url = "https://www.zhihu.com"
        
    async def login(self, credentials: Optional[Dict[str, str]] = None) -> bool:
        """知乎登录"""
        logger.info("开始知乎登录流程")
        # 使用Cookie登录
        cookies = json.loads(self.config.cookies) if self.config.cookies else {}
        if cookies:
            logger.info("使用Cookie登录知乎")
            return True
        
        # 支持扫码登录或账号密码登录（需要实现Selenium或API集成）
        logger.warning("知乎未配置Cookie，无法自动登录。请配置Cookie或实现扫码登录功能")
        logger.warning("提示：可通过Selenium + WebDriver实现扫码登录，保存Cookie到配置中")
        return False
    
    async def check_login_status(self) -> bool:
        """检查知乎登录状态"""
        try:
            cookies = json.loads(self.config.cookies) if self.config.cookies else {}
            if not cookies:
                return False
            
            # 验证Cookie有效性
            # 通过检查关键Cookie字段来验证登录状态
            z_c0_cookie = cookies.get('z_c0')
            if not z_c0_cookie:
                logger.warning("知乎Cookie中缺少z_c0字段，可能已失效")
                return False
            
            # 可以通过请求知乎API来进一步验证Cookie有效性
            # 这里简单检查Cookie是否存在
            logger.debug("知乎登录状态检查完成")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"解析知乎Cookie失败: {e}")
            return False
        except Exception as e:
            logger.error(f"检查知乎登录状态失败: {e}")
            return False
    
    async def publish(self, article: ArticleContent, db: AsyncSession) -> PublishResult:
        """发布文章到知乎"""
        try:
            logger.info(f"开始发布文章到知乎: {article.title}")

            # 真实发布功能尚未实现
            # 需要集成以下功能之一：
            # 1. 使用Selenium + WebDriver模拟浏览器操作
            # 2. 使用知乎API（需要申请API权限）
            # 3. 使用requests + BeautifulSoup模拟表单提交
            raise NotImplementedError(
                message="知乎真实发布功能尚未实现",
                feature="zhihu_publish"
            )

        except NotImplementedError:
            raise
        except Exception as e:
            logger.error(f"知乎发布失败: {e}", exc_info=True)
            return PublishResult(
                success=False,
                platform=self.platform,
                message=f"发布失败: {str(e)}",
                need_retry=True,
                error_code=str(type(e).__name__)
            )
            
        except Exception as e:
            logger.error(f"知乎发布失败: {e}")
            return PublishResult(
                success=False,
                platform=self.platform,
                message=f"发布失败: {str(e)}",
                need_retry=True
            )
    
    async def fetch_stats(self, platform_article_id: str) -> Optional[PlatformStats]:
        """获取知乎文章统计数据"""
        try:
            # 真实统计数据获取功能尚未实现
            # 需要集成以下功能之一：
            # 1. 使用Selenium爬取知乎文章页面的统计信息
            # 2. 使用知乎API获取统计数据
            # 3. 需要解析页面HTML或API返回的JSON数据
            raise NotImplementedError(
                message="知乎真实统计数据获取功能尚未实现",
                feature="zhihu_fetch_stats"
            )

        except NotImplementedError:
            raise
        except Exception as e:
            logger.error(f"获取知乎统计数据失败: {e}", exc_info=True)
            return None


class JuejinPublisher(BasePublisher):
    """掘金发布器"""
    
    def __init__(self, config: PlatformConfig):
        super().__init__(PlatformType.JUEJIN, config)
        self.base_url = "https://juejin.cn"
        
    async def login(self, credentials: Optional[Dict[str, str]] = None) -> bool:
        """掘金登录"""
        logger.info("开始掘金登录流程")
        cookies = json.loads(self.config.cookies) if self.config.cookies else {}
        if cookies:
            logger.info("使用Cookie登录掘金")
            return True
        return False
    
    async def check_login_status(self) -> bool:
        """检查掘金登录状态"""
        cookies = json.loads(self.config.cookies) if self.config.cookies else {}
        return bool(cookies.get('sessionid'))
    
    async def publish(self, article: ArticleContent, db: AsyncSession) -> PublishResult:
        """发布文章到掘金"""
        try:
            logger.info(f"开始发布文章到掘金: {article.title}")

            # 真实发布功能尚未实现
            # 需要集成以下功能之一：
            # 1. 使用掘金API（需要申请API权限）
            # 2. 使用Selenium + WebDriver模拟浏览器操作
            # 3. 需要处理Markdown格式转换、图片上传等
            raise NotImplementedError(
                message="掘金真实发布功能尚未实现",
                feature="juejin_publish"
            )

        except NotImplementedError:
            raise
        except Exception as e:
            logger.error(f"掘金发布失败: {e}", exc_info=True)
            return PublishResult(
                success=False,
                platform=self.platform,
                message=f"发布失败: {str(e)}",
                need_retry=True,
                error_code=str(type(e).__name__)
            )
    
    async def fetch_stats(self, platform_article_id: str) -> Optional[PlatformStats]:
        """获取掘金文章统计数据"""
        try:
            # 真实统计数据获取功能尚未实现
            # 需要集成以下功能之一：
            # 1. 使用掘金API获取文章统计数据
            # 2. 使用Selenium爬取掘金文章页面的统计信息
            # 3. 需要解析API返回的JSON数据或页面HTML
            raise NotImplementedError(
                message="掘金真实统计数据获取功能尚未实现",
                feature="juejin_fetch_stats"
            )

        except NotImplementedError:
            raise
        except Exception as e:
            logger.error(f"获取掘金统计数据失败: {e}", exc_info=True)
            return None


class ToutiaoPublisher(BasePublisher):
    """今日头条发布器"""
    
    def __init__(self, config: PlatformConfig):
        super().__init__(PlatformType.TOUTIAO, config)
        self.base_url = "https://mp.toutiao.com"
        
    async def login(self, credentials: Optional[Dict[str, str]] = None) -> bool:
        """头条登录"""
        logger.info("开始头条登录流程")
        cookies = json.loads(self.config.cookies) if self.config.cookies else {}
        if cookies:
            logger.info("使用Cookie登录头条")
            return True
        return False
    
    async def check_login_status(self) -> bool:
        """检查头条登录状态"""
        cookies = json.loads(self.config.cookies) if self.config.cookies else {}
        return bool(cookies.get('sessionid'))
    
    async def publish(self, article: ArticleContent, db: AsyncSession) -> PublishResult:
        """发布文章到今日头条"""
        try:
            logger.info(f"开始发布文章到头条: {article.title}")

            # 真实发布功能尚未实现
            # 需要集成以下功能之一：
            # 1. 使用今日头条API（需要申请API权限）
            # 2. 使用Selenium + WebDriver模拟浏览器操作
            # 3. 需要处理Markdown格式转换、图片上传、封面图等
            raise NotImplementedError(
                message="头条真实发布功能尚未实现",
                feature="toutiao_publish"
            )

        except NotImplementedError:
            raise
        except Exception as e:
            logger.error(f"头条发布失败: {e}", exc_info=True)
            return PublishResult(
                success=False,
                platform=self.platform,
                message=f"发布失败: {str(e)}",
                need_retry=True,
                error_code=str(type(e).__name__)
            )
    
    async def fetch_stats(self, platform_article_id: str) -> Optional[PlatformStats]:
        """获取今日头条文章统计数据"""
        try:
            # 真实统计数据获取功能尚未实现
            # 需要集成以下功能之一：
            # 1. 使用今日头条API获取文章统计数据
            # 2. 使用Selenium爬取头条文章页面的统计信息
            # 3. 需要解析API返回的JSON数据或页面HTML
            raise NotImplementedError(
                message="头条真实统计数据获取功能尚未实现",
                feature="toutiao_fetch_stats"
            )

        except NotImplementedError:
            raise
        except Exception as e:
            logger.error(f"获取头条统计数据失败: {e}", exc_info=True)
            return None


class WeChatPublisher(BasePublisher):
    """微信公众号发布器"""
    
    def __init__(self, config: PlatformConfig):
        super().__init__(PlatformType.WECHAT, config)
        self.base_url = "https://api.weixin.qq.com"
        
    async def login(self, credentials: Optional[Dict[str, str]] = None) -> bool:
        """微信登录（验证配置）"""
        logger.info("开始验证微信配置")
        # 微信使用 AppID 和 AppSecret，不需要登录流程
        # 从数据库配置中读取
        if self.config and self.config.token:
            logger.info("微信配置已设置")
            return True
        return False
    
    async def check_login_status(self) -> bool:
        """检查微信配置状态"""
        # 检查是否配置了AppID和AppSecret
        if not self.config or not self.config.token:
            return False
        # 尝试获取access_token验证配置有效性
        try:
            from ..services.wechat_service import wechat_service
            from ..core.config import settings
            
            # 从数据库或配置中获取AppID和AppSecret
            app_id = settings.WECHAT_APP_ID
            app_secret = settings.WECHAT_APP_SECRET
            
            if not app_id or not app_secret:
                return False
                
            access_token = await wechat_service.get_access_token(app_id, app_secret)
            return bool(access_token)
        except Exception as e:
            logger.warning(f"微信配置检查失败: {e}")
            return False
    
    def convert_content(self, article: ArticleContent) -> ArticleContent:
        """微信场景仅做标题规范化，内容转换在发布阶段处理。"""
        # 微信标题限制64字符
        original_len = len(article.title)
        if original_len > 64:
            article.title = article.title[:64]
            logger.info(f"convert_content: 标题截断 {original_len} -> 64 字符")
        else:
            logger.info(f"convert_content: 标题无需截断 ({original_len} 字符)")
        return article

    async def _convert_markdown_to_wechat_html(self, markdown_text: str) -> tuple[str, str]:
        """优先高级转换器，失败时回退简单转换。"""
        from ..services.wechat_service import wechat_service

        try:
            html = await markdown_converter.convert_to_wechat_html(markdown_text, inline_css=True)
            return html, "advanced"
        except Exception as conversion_error:
            logger.warning(f"微信高级转换失败，回退简单转换: {conversion_error}")
            return wechat_service._simple_markdown_to_html(markdown_text), "simple"

    async def _rewrite_html_images_for_wechat(
        self,
        html_content: str,
        access_token: str,
        trace_id: str,
    ) -> tuple[str, dict]:
        """将正文中的图片上传到微信并替换为微信URL。"""
        from bs4 import BeautifulSoup
        from ..services.wechat_service import wechat_service
        from ..core.config import settings

        soup = BeautifulSoup(html_content, "html.parser")
        images = soup.find_all("img")
        stats = {"total": len(images), "replaced": 0, "failed": 0, "skipped": 0}
        logger.info(f"[{trace_id}] 多平台-微信正文图片重写开始: total={len(images)}")

        for index, img in enumerate(images, start=1):
            src = (img.get("src") or "").strip()
            if not src:
                stats["skipped"] += 1
                logger.info(f"[{trace_id}] 多平台-微信正文图片跳过(index={index}): src 为空")
                continue
            if src.startswith("data:"):
                stats["skipped"] += 1
                logger.info(f"[{trace_id}] 多平台-微信正文图片跳过(index={index}): data URI")
                continue

            temp_path = None
            try:
                if src.startswith("http://") or src.startswith("https://"):
                    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                        response = await client.get(src)
                        response.raise_for_status()
                        suffix = ".jpg"
                        content_type = response.headers.get("content-type", "")
                        if "png" in content_type:
                            suffix = ".png"
                        elif "gif" in content_type:
                            suffix = ".gif"
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                            temp_file.write(response.content)
                            temp_path = temp_file.name
                else:
                    normalized = src.replace("\\", "/")
                    if normalized.startswith("/uploads/"):
                        temp_path = str(Path(settings.UPLOAD_DIR) / normalized.replace("/uploads/", "", 1))
                    elif normalized.startswith("uploads/"):
                        temp_path = str(Path(settings.UPLOAD_DIR) / normalized.replace("uploads/", "", 1))
                    else:
                        path_obj = Path(normalized)
                        temp_path = str(path_obj if path_obj.is_absolute() else (Path(settings.UPLOAD_DIR) / normalized))

                if not temp_path or not Path(temp_path).exists():
                    raise ValueError(f"图片文件不存在: {src}")

                wechat_url = await wechat_service.upload_article_image(access_token=access_token, file_path=temp_path)
                img["src"] = wechat_url
                stats["replaced"] += 1
                logger.info(f"[{trace_id}] 多平台-微信正文图片已替换(index={index}): {src} -> {wechat_url}")
            except Exception as image_error:
                stats["failed"] += 1
                logger.warning(f"[{trace_id}] 多平台-微信正文图片替换失败(index={index}): src={src}, error={image_error}")
            finally:
                if temp_path and os.path.exists(temp_path):
                    try:
                        if src.startswith("http://") or src.startswith("https://"):
                            os.remove(temp_path)
                    except Exception:
                        pass

        logger.info(
            f"[{trace_id}] 多平台-微信正文图片重写结束: total={stats['total']}, replaced={stats['replaced']}, "
            f"failed={stats['failed']}, skipped={stats['skipped']}"
        )
        return str(soup), stats
    
    async def publish(self, article: ArticleContent, db: AsyncSession) -> PublishResult:
        """发布文章到微信公众号草稿箱"""
        try:
            trace_id = f"wxmp-{hashlib.md5(f'{article.title}-{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"
            logger.info(f"开始发布文章到微信公众号: {article.title[:30]}... (长度: {len(article.title)})")
            
            from ..services.wechat_service import wechat_service
            from ..core.config import settings
            from sqlalchemy import select
            from ..models.config import AppConfig
            
            # 1. 从数据库获取微信配置
            result = await db.execute(select(AppConfig))
            config = result.scalar_one_or_none()
            
            if not config or not config.wechat_app_id or not config.wechat_app_secret:
                logger.error("微信配置未找到或未完成")
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    message="未配置微信公众号AppID和AppSecret",
                    need_retry=False
                )
            
            app_id = config.wechat_app_id
            app_secret = config.wechat_app_secret
            logger.info(f"获取到微信配置: AppID={app_id[:6]}...")
            
            # 2. 获取access_token
            try:
                access_token = await wechat_service.get_access_token(app_id, app_secret)
                logger.info("获取微信access_token成功")
            except Exception as token_error:
                logger.error(f"获取access_token失败: {token_error}")
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    message=f"获取微信access_token失败: {str(token_error)}",
                    need_retry=False
                )
            
            # 3. 内容转换 + 正文图片重写
            html_content, format_engine = await self._convert_markdown_to_wechat_html(article.content)
            logger.info(f"[{trace_id}] 多平台-微信内容转换完成: engine={format_engine}, length={len(html_content)}")

            html_content, image_stats = await self._rewrite_html_images_for_wechat(
                html_content=html_content,
                access_token=access_token,
                trace_id=trace_id,
            )
            
            # 4. 处理封面图
            cover_media_id = ""
            if article.cover_image:
                try:
                    from pathlib import Path
                    cover_path = article.cover_image
                    logger.info(f"文章封面图路径: {cover_path}")
                    
                    # 处理网络图片URL
                    if cover_path.startswith('http://') or cover_path.startswith('https://'):
                        logger.info(f"封面图是URL，开始下载: {cover_path}")
                        try:
                            import httpx
                            import hashlib
                            
                            async with httpx.AsyncClient() as client:
                                response = await client.get(cover_path, timeout=30.0)
                                response.raise_for_status()
                                
                                # 生成文件名
                                filename = f"cover_downloaded_{hashlib.md5(cover_path.encode()).hexdigest()[:8]}.jpg"
                                download_dir = Path(settings.UPLOAD_DIR)
                                download_dir.mkdir(parents=True, exist_ok=True)
                                cover_path = str(download_dir / filename)
                                
                                # 保存图片
                                with open(cover_path, 'wb') as f:
                                    f.write(response.content)
                                
                                logger.info(f"封面图下载成功: {cover_path}")
                        except Exception as download_error:
                            logger.error(f"下载封面图失败: {download_error}")
                            cover_path = None
                    elif not Path(cover_path).is_absolute():
                        # 本地相对路径处理
                        # 如果路径已经包含 uploads/ 前缀，直接使用项目根目录作为基准
                        if cover_path.startswith('uploads/'):
                            # 从项目根目录开始 (backend/app/services -> backend)
                            project_root = Path(__file__).parent.parent.parent
                            cover_path = str(project_root / cover_path)
                        else:
                            # 其他相对路径，使用 UPLOAD_DIR 作为基准
                            cover_path = str(Path(settings.UPLOAD_DIR) / cover_path)
                        
                        logger.info(f"转换后的封面图绝对路径: {cover_path}")
                    
                    # 检查文件是否存在并上传
                    if cover_path and Path(cover_path).exists():
                        cover_media_id = await wechat_service.upload_permanent_material(
                            access_token=access_token,
                            media_type="thumb",
                            file_path=cover_path,
                            description={"introduction": article.summary or article.title}
                        )
                        logger.info(f"封面图上传成功: {cover_media_id}")
                    else:
                        logger.warning(f"封面图文件不存在: {cover_path}")
                except Exception as img_error:
                    logger.warning(f"上传封面图失败: {img_error}")
            
            if not cover_media_id:
                logger.error(f"[{trace_id}] 封面图缺失或上传失败，终止发布")
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    message="封面图上传失败：请先为文章设置可用封面图（JPG/PNG）后重试",
                    need_retry=False,
                )
            
            # 6. 创建微信草稿
            try:
                # 标题已在 convert_content 中处理，直接使用
                title = article.title
                logger.info(f"使用标题: {title} ({len(title.encode('utf-8'))} 字节)")
                
                digest = article.summary[:120] if article.summary and len(article.summary) > 120 else (article.summary or "")
                logger.info(
                    f"[{trace_id}] 准备创建微信草稿: 标题={title[:30]}..., 封面ID={cover_media_id}, "
                    f"内容长度={len(html_content)}, image_rewrite={image_stats['replaced']}/{image_stats['total']}"
                )
                
                draft_id = await wechat_service.create_draft(
                    access_token=access_token,
                    title=title,
                    author=article.author or "拾贝猫",
                    digest=digest,
                    content=html_content,
                    cover_media_id=cover_media_id
                )
                
                logger.info(f"微信草稿创建成功: {draft_id}")
                
                return PublishResult(
                    success=True,
                    platform=self.platform,
                    message=(
                        f"发布到微信公众号草稿箱成功（排版:{format_engine}，"
                        f"正文图片:{image_stats['replaced']}/{image_stats['total']}，trace:{trace_id}）"
                    ),
                    article_id=draft_id,
                    article_url="https://mp.weixin.qq.com/"
                )
            except Exception as draft_error:
                logger.error(f"创建微信草稿失败: {draft_error}")
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    message=f"创建微信草稿失败: {str(draft_error)}",
                    need_retry=True
                )
            
        except Exception as e:
            logger.error(f"微信公众号发布失败: {e}", exc_info=True)
            return PublishResult(
                success=False,
                platform=self.platform,
                message=f"发布失败: {str(e)}",
                need_retry=True,
                error_code=str(type(e).__name__)
            )
    
    async def fetch_stats(self, platform_article_id: str) -> Optional[PlatformStats]:
        """获取微信公众号文章统计数据"""
        try:
            # 微信统计数据需要通过微信公众平台获取
            # 这里返回空，表示不支持自动获取
            logger.info("微信统计数据获取需要通过公众平台手动查看")
            return None
        except Exception as e:
            logger.error(f"获取微信统计数据失败: {e}")
            return None


class MultiPlatformPublisher:
    """多平台发布管理器 - Mixpost 核心逻辑"""
    
    def __init__(self):
        self.publishers: Dict[PlatformType, BasePublisher] = {}
        self.publisher_map = {
            PlatformType.ZHIHU: ZhihuPublisher,
            PlatformType.JUEJIN: JuejinPublisher,
            PlatformType.TOUTIAO: ToutiaoPublisher,
            PlatformType.WECHAT: WeChatPublisher,
        }
        self.platform_implementation = {
            PlatformType.WECHAT: {
                "implemented": True,
                "reason": ""
            },
            PlatformType.ZHIHU: {
                "implemented": False,
                "reason": "知乎发布器仍为占位实现，暂未接入真实发布流程"
            },
            PlatformType.JUEJIN: {
                "implemented": False,
                "reason": "掘金发布器仍为占位实现，暂未接入真实发布流程"
            },
            PlatformType.TOUTIAO: {
                "implemented": False,
                "reason": "头条发布器仍为占位实现，暂未接入真实发布流程"
            },
        }
        
    def register_publisher(self, platform: PlatformType, publisher: BasePublisher):
        """注册发布器"""
        self.publishers[platform] = publisher
        logger.info(f"已注册发布器: {platform.value}")
        
    def get_publisher(self, platform: PlatformType) -> Optional[BasePublisher]:
        """获取发布器"""
        return self.publishers.get(platform)
        
    async def load_publishers(self, db: AsyncSession):
        """从数据库加载发布器配置"""
        try:
            query = select(PlatformConfig).where(PlatformConfig.is_enabled == True)
            result = await db.execute(query)
            configs = result.scalars().all()
            
            for config in configs:
                publisher_class = self.publisher_map.get(config.platform)
                if publisher_class:
                    publisher = publisher_class(config)
                    self.register_publisher(config.platform, publisher)
            
            # 检查微信配置（存储在 AppConfig 表中）
            from ..models.config import AppConfig
            app_config_result = await db.execute(select(AppConfig))
            app_config = app_config_result.scalar_one_or_none()
            
            if app_config and app_config.wechat_app_id and app_config.wechat_app_secret:
                # 如果配置了微信，但还没有加载微信发布器，则创建一个临时配置
                if PlatformType.WECHAT not in self.publishers:
                    # 创建临时 PlatformConfig 用于微信发布器
                    wechat_config = PlatformConfig(
                        platform=PlatformType.WECHAT,
                        is_enabled=True,
                        is_configured=True,
                        token=f"{app_config.wechat_app_id}:{app_config.wechat_app_secret}"
                    )
                    wechat_publisher = WeChatPublisher(wechat_config)
                    self.register_publisher(PlatformType.WECHAT, wechat_publisher)
                    logger.info("已自动加载微信发布器（基于 AppConfig 配置）")
                    
            logger.info(f"已加载 {len(self.publishers)} 个平台发布器")
            
        except Exception as e:
            logger.error(f"加载发布器配置失败: {e}")
    
    async def adapt_article_images(
        self,
        article: ArticleContent,
        platform: PlatformType,
        db: AsyncSession
    ) -> ArticleContent:
        """
        适配文章图片到目标平台要求
        
        Args:
            article: 文章内容
            platform: 目标平台
            db: 数据库会话
        
        Returns:
            处理后的文章内容
        """
        from ..services.image_processor import image_processor
        from ..core.platform_image_specs import get_platform_spec, ImageType
        
        try:
            platform_name = platform.value
            
            # 处理封面图
            if article.cover_image:
                spec = get_platform_spec(platform_name, "cover")
                if spec:
                    result = await image_processor.adapt_for_platform(
                        article.cover_image,
                        platform_name,
                        "cover"
                    )
                    if result.get("success"):
                        article.cover_image = result.get("output_path", article.cover_image)
                        logger.info(f"封面图已适配到 {platform_name}: {article.cover_image}")
            
            # 处理行内配图（解析HTML中的img标签）
            import re
            from pathlib import Path
            
            img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
            inline_images = re.findall(img_pattern, article.content)
            
            for img_src in inline_images:
                # 只处理本地图片
                if img_src.startswith('/uploads/') or img_src.startswith('uploads/'):
                    img_path = img_src.lstrip('/')
                    full_path = Path(settings.UPLOAD_DIR) / img_path.replace('uploads/', '')
                    
                    if full_path.exists():
                        result = await image_processor.adapt_for_platform(
                            str(full_path),
                            platform_name,
                            "inline"
                        )
                        if result.get("success"):
                            new_src = result.get("output_path", img_src)
                            # 更新内容中的图片路径
                            article.content = article.content.replace(img_src, new_src)
                            logger.info(f"行内配图已适配: {img_src} -> {new_src}")
            
            return article
            
        except Exception as e:
            logger.error(f"适配文章图片失败: {e}", exc_info=True)
            return article
    
    async def publish_to_platform(
        self, 
        platform: PlatformType, 
        article: ArticleContent,
        article_id: int,
        db: AsyncSession,
        adapt_images: bool = True
    ) -> PublishResult:
        """发布到单个平台"""
        publisher = self.get_publisher(platform)
        
        # 如果找不到发布器且是微信平台，尝试自动加载
        if not publisher and platform == PlatformType.WECHAT:
            from ..models.config import AppConfig
            app_config_result = await db.execute(select(AppConfig))
            app_config = app_config_result.scalar_one_or_none()
            
            if app_config and app_config.wechat_app_id and app_config.wechat_app_secret:
                wechat_config = PlatformConfig(
                    platform=PlatformType.WECHAT,
                    is_enabled=True,
                    is_configured=True,
                    token=f"{app_config.wechat_app_id}:{app_config.wechat_app_secret}"
                )
                wechat_publisher = WeChatPublisher(wechat_config)
                self.register_publisher(PlatformType.WECHAT, wechat_publisher)
                publisher = wechat_publisher
                logger.info("已自动加载微信发布器")
        
        if not publisher:
            return PublishResult(
                success=False,
                platform=platform,
                message=f"未找到平台 {platform.value} 的发布器"
            )
        
        # 适配图片到目标平台（如果启用）
        if adapt_images:
            try:
                article = await self.adapt_article_images(article, platform, db)
                logger.info(f"文章图片已适配到平台 {platform.value}")
            except Exception as img_error:
                logger.warning(f"图片适配失败，继续发布: {img_error}")
        
        # 创建发布记录（待发布）
        record = PublishRecord(
            article_id=article_id,
            platform=platform,
            status=PublishStatus.PUBLISHING,
            title_snapshot=article.title,
            content_snapshot=article.content[:1000]
        )
        db.add(record)
        await db.commit()
        
        # 发布文章
        try:
            result = await publisher.publish_with_retry(article, db)
            
            # 更新发布记录
            if result.success:
                record.status = PublishStatus.SUCCESS
                record.platform_article_id = result.article_id
                record.platform_article_url = result.article_url
                record.published_at = datetime.now()
            else:
                record.status = PublishStatus.FAILED
                record.error_message = result.message
            
            await db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"{platform.value} 发布异常: {e}", exc_info=True)
            await db.rollback()  # 先回滚
            record.status = PublishStatus.FAILED
            record.error_message = str(e)
            await db.commit()  # 再提交记录更新
            
            return PublishResult(
                success=False,
                platform=platform,
                message=f"发布异常: {str(e)}",
                need_retry=True
            )
    
    async def publish_to_multiple_platforms(
        self,
        platforms: List[PlatformType],
        article: ArticleContent,
        article_id: int,
        db: AsyncSession
    ) -> Dict[PlatformType, PublishResult]:
        """批量发布到多个平台"""
        results = {}
        
        # 创建批量任务
        task = PublishTask(
            name=f"批量发布文章 {article_id}",
            article_id=article_id,
            target_platforms=json.dumps([p.value for p in platforms]),
            status=PublishStatus.PUBLISHING,
            total_count=len(platforms)
        )
        db.add(task)
        await db.commit()
        
        # 并行发布
        tasks = []
        for platform in platforms:
            task_coro = self.publish_to_platform(platform, article, article_id, db)
            tasks.append(task_coro)
        
        publish_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        success_count = 0
        failed_count = 0
        
        for i, result in enumerate(publish_results):
            platform = platforms[i]
            
            if isinstance(result, Exception):
                results[platform] = PublishResult(
                    success=False,
                    platform=platform,
                    message=f"发布异常: {str(result)}"
                )
                failed_count += 1
            else:
                results[platform] = result
                if result.success:
                    success_count += 1
                else:
                    failed_count += 1
        
        # 更新任务状态
        task.success_count = success_count
        task.failed_count = failed_count
        task.status = PublishStatus.SUCCESS if failed_count == 0 else PublishStatus.PARTIAL
        if failed_count > 0:
            task.status = PublishStatus.FAILED if success_count == 0 else PublishStatus.PARTIAL
        task.completed_at = datetime.now()
        await db.commit()
        
        logger.info(f"批量发布完成: 成功 {success_count}, 失败 {failed_count}")
        
        return results
    
    async def schedule_publish(
        self,
        platforms: List[PlatformType],
        article: ArticleContent,
        article_id: int,
        publish_at: datetime,
        db: AsyncSession
    ) -> str:
        """定时发布"""
        # 创建定时任务
        task_id = f"schedule_{article_id}_{int(publish_at.timestamp())}"
        
        # 使用异步任务队列
        await task_queue.add_task(
            task_id=task_id,
            task_type="publish",
            params={
                "platforms": [p.value for p in platforms],
                "article_id": article_id,
                "article_data": {
                    "title": article.title,
                    "content": article.content,
                    "summary": article.summary,
                    "cover_image": article.cover_image,
                    "tags": article.tags,
                    "category": article.category,
                }
            },
            scheduled_at=publish_at
        )
        
        logger.info(f"已创建定时发布任务: {task_id}, 计划时间: {publish_at}")
        
        return task_id
    
    def get_supported_platforms(self) -> List[Dict[str, Any]]:
        """获取支持的平台列表"""
        platforms = []
        for platform_type, info in PLATFORM_INFO.items():
            publisher = self.publishers.get(platform_type)
            runtime_status = self._get_platform_runtime_status(platform_type, publisher)
            platforms.append({
                "type": platform_type.value,
                "name": info.get("name"),
                "icon": info.get("icon"),
                "description": info.get("description"),
                "configured": runtime_status["configured"],
                "implemented": runtime_status["implemented"],
                "ready": runtime_status["ready"],
                "reason": runtime_status["reason"],
                "support_markdown": info.get("support_markdown"),
                "support_html": info.get("support_html"),
            })
        return platforms

    def _get_platform_runtime_status(
        self,
        platform_type: PlatformType,
        publisher: Optional[BasePublisher],
    ) -> Dict[str, Any]:
        """计算平台可用状态，避免前端误判为“可发布”"""
        implementation_info = self.platform_implementation.get(
            platform_type,
            {
                "implemented": False,
                "reason": "平台发布器尚未接入"
            }
        )

        implemented = bool(implementation_info.get("implemented"))
        configured = bool(
            publisher and getattr(getattr(publisher, "config", None), "is_configured", False)
        )

        if not implemented:
            return {
                "implemented": False,
                "configured": configured,
                "ready": False,
                "reason": implementation_info.get("reason") or "平台尚未实现真实发布能力",
            }

        if not configured:
            if platform_type == PlatformType.WECHAT:
                reason = "未配置微信公众号 AppID/AppSecret"
            else:
                reason = "未完成平台登录凭据配置"

            return {
                "implemented": True,
                "configured": False,
                "ready": False,
                "reason": reason,
            }

        return {
            "implemented": True,
            "configured": True,
            "ready": True,
            "reason": "可发布",
        }
    
    async def get_publish_history(
        self, 
        article_id: int, 
        db: AsyncSession
    ) -> List[PublishRecord]:
        """获取发布历史"""
        query = select(PublishRecord).where(
            PublishRecord.article_id == article_id
        ).order_by(PublishRecord.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def sync_stats_for_record(
        self,
        record: PublishRecord,
        db: AsyncSession
    ) -> bool:
        """同步单个发布记录的统计数据"""
        try:
            # 检查是否已有平台文章ID
            if not record.platform_article_id:
                logger.warning(f"发布记录 {record.id} 没有平台文章ID，跳过同步")
                return False
            
            # 获取发布器
            publisher = self.get_publisher(record.platform)
            if not publisher:
                logger.warning(f"未找到平台 {record.platform.value} 的发布器")
                return False
            
            # 获取统计数据
            stats = await publisher.fetch_stats(record.platform_article_id)
            if not stats:
                logger.warning(f"无法获取 {record.platform.value} 的统计数据")
                return False
            
            # 更新发布记录
            record.view_count = stats.view_count
            record.like_count = stats.like_count
            record.comment_count = stats.comment_count
            # 保存额外数据到metadata（如果有的话）
            if stats.extra_data:
                # 可以将额外数据保存到其他字段或扩展模型
                pass
            
            await db.commit()
            
            logger.info(f"发布记录 {record.id} 统计数据已同步: 阅读={stats.view_count}, 点赞={stats.like_count}")
            
            return True
            
        except Exception as e:
            logger.error(f"同步统计数据失败: {e}")
            await db.rollback()
            return False
    
    async def sync_stats_for_article(
        self,
        article_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """同步文章的所有平台统计数据"""
        try:
            # 查询文章的所有发布记录
            query = select(PublishRecord).where(
                PublishRecord.article_id == article_id,
                PublishRecord.status == PublishStatus.SUCCESS,
                PublishRecord.platform_article_id.isnot(None)
            )
            result = await db.execute(query)
            records = result.scalars().all()
            
            if not records:
                return {
                    "success": False,
                    "message": "没有找到已发布的记录"
                }
            
            # 并行同步所有平台的统计数据
            sync_results = []
            for record in records:
                sync_result = await self.sync_stats_for_record(record, db)
                sync_results.append({
                    "platform": record.platform.value,
                    "success": sync_result,
                    "record_id": record.id
                })
            
            # 统计结果
            success_count = sum(1 for r in sync_results if r["success"])
            
            return {
                "success": True,
                "total": len(records),
                "success_count": success_count,
                "failed_count": len(records) - success_count,
                "details": sync_results
            }
            
        except Exception as e:
            logger.error(f"同步文章统计数据失败: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def sync_stats_for_platform(
        self,
        platform: PlatformType,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """同步指定平台的所有统计数据"""
        try:
            # 查询平台的所有发布记录
            query = select(PublishRecord).where(
                PublishRecord.platform == platform,
                PublishRecord.status == PublishStatus.SUCCESS,
                PublishRecord.platform_article_id.isnot(None)
            )
            result = await db.execute(query)
            records = result.scalars().all()
            
            if not records:
                return {
                    "success": False,
                    "message": f"没有找到 {platform.value} 的已发布记录"
                }
            
            # 同步所有记录
            sync_results = []
            for record in records:
                sync_result = await self.sync_stats_for_record(record, db)
                sync_results.append({
                    "article_id": record.article_id,
                    "success": sync_result,
                    "record_id": record.id
                })
            
            # 统计结果
            success_count = sum(1 for r in sync_results if r["success"])
            
            return {
                "success": True,
                "total": len(records),
                "success_count": success_count,
                "failed_count": len(records) - success_count,
                "details": sync_results
            }
            
        except Exception as e:
            logger.error(f"同步平台统计数据失败: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def sync_all_stats(
        self,
        db: AsyncSession,
        days: int = 7
    ) -> Dict[str, Any]:
        """同步所有平台的统计数据"""
        try:
            # 查询最近N天的发布记录
            cutoff_date = datetime.now() - timedelta(days=days)
            
            query = select(PublishRecord).where(
                PublishRecord.status == PublishStatus.SUCCESS,
                PublishRecord.platform_article_id.isnot(None),
                PublishRecord.published_at >= cutoff_date
            )
            result = await db.execute(query)
            records = result.scalars().all()
            
            if not records:
                return {
                    "success": False,
                    "message": f"最近{days}天没有找到已发布的记录"
                }
            
            # 同步所有记录
            sync_results = []
            for record in records:
                sync_result = await self.sync_stats_for_record(record, db)
                sync_results.append({
                    "platform": record.platform.value,
                    "article_id": record.article_id,
                    "success": sync_result
                })
            
            # 统计结果
            success_count = sum(1 for r in sync_results if r["success"])
            
            return {
                "success": True,
                "total": len(records),
                "success_count": success_count,
                "failed_count": len(records) - success_count,
                "details": sync_results
            }
            
        except Exception as e:
            logger.error(f"同步所有统计数据失败: {e}")
            return {
                "success": False,
                "message": str(e)
            }


# 全局发布管理器实例
multiplatform_publisher = MultiPlatformPublisher()
