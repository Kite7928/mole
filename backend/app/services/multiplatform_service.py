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
from pathlib import Path
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
            
        return article
    
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


class MultiPlatformPublisher:
    """多平台发布管理器 - Mixpost 核心逻辑"""
    
    def __init__(self):
        self.publishers: Dict[PlatformType, BasePublisher] = {}
        self.publisher_map = {
            PlatformType.ZHIHU: ZhihuPublisher,
            PlatformType.JUEJIN: JuejinPublisher,
            PlatformType.TOUTIAO: ToutiaoPublisher,
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
                    
            logger.info(f"已加载 {len(self.publishers)} 个平台发布器")
            
        except Exception as e:
            logger.error(f"加载发布器配置失败: {e}")
    
    async def publish_to_platform(
        self, 
        platform: PlatformType, 
        article: ArticleContent,
        article_id: int,
        db: AsyncSession
    ) -> PublishResult:
        """发布到单个平台"""
        publisher = self.get_publisher(platform)
        if not publisher:
            return PublishResult(
                success=False,
                platform=platform,
                message=f"未找到平台 {platform.value} 的发布器"
            )
        
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
            logger.error(f"{platform.value} 发布异常: {e}")
            record.status = PublishStatus.FAILED
            record.error_message = str(e)
            await db.commit()
            
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
            platforms.append({
                "type": platform_type.value,
                "name": info.get("name"),
                "icon": info.get("icon"),
                "description": info.get("description"),
                "configured": publisher is not None,
                "support_markdown": info.get("support_markdown"),
                "support_html": info.get("support_html"),
            })
        return platforms
    
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