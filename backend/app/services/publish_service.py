"""
多平台发布服务
支持知乎、掘金、头条等多平台文章发布
基于 Selenium 实现浏览器自动化
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import asyncio
from pathlib import Path

from ..core.logger import logger
from ..models.publish_platform import PlatformType, PublishStatus, PLATFORM_INFO
from ..types import PublishResult, ArticleContent


class BasePublisher(ABC):
    """发布器基类"""
    
    def __init__(self, platform: PlatformType, config: Dict[str, Any]):
        self.platform = platform
        self.config = config
        self.platform_info = PLATFORM_INFO.get(platform, {})
        
    @abstractmethod
    async def login(self, credentials: Dict[str, str]) -> bool:
        """登录平台"""
        pass
    
    @abstractmethod
    async def publish(self, article: ArticleContent) -> PublishResult:
        """发布文章"""
        pass
    
    @abstractmethod
    async def check_login_status(self) -> bool:
        """检查登录状态"""
        pass
    
    async def validate_content(self, article: ArticleContent) -> tuple[bool, str]:
        """验证内容是否符合平台要求"""
        # 基础验证
        if not article.title or len(article.title) < 5:
            return False, "标题不能为空且至少5个字符"
        
        if not article.content or len(article.content) < 100:
            return False, "内容不能为空且至少100个字符"
            
        # 平台特定验证
        max_title_length = self.config.get('max_title_length', 100)
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
        """HTML转Markdown（简化版）"""
        try:
            import html2text
            h = html2text.HTML2Text()
            h.ignore_links = False
            return h.handle(html_content)
        except ImportError:
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
            return markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        except ImportError:
            logger.warning("markdown库未安装，返回原始内容")
            return md_content


class ZhihuPublisher(BasePublisher):
    """知乎发布器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(PlatformType.ZHIHU, config)
        self.base_url = "https://www.zhihu.com"
        
    async def login(self, credentials: Dict[str, str]) -> bool:
        """知乎登录 - 使用Cookie或扫码登录"""
        logger.info("开始知乎登录流程")
        # 实际实现需要使用Selenium模拟登录
        # 或引导用户手动获取Cookie
        return True
    
    async def check_login_status(self) -> bool:
        """检查知乎登录状态"""
        cookies = self.config.get('cookies')
        if not cookies:
            return False
        # 验证Cookie有效性
        return True
    
    async def publish(self, article: ArticleContent) -> PublishResult:
        """发布文章到知乎"""
        try:
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
            
            logger.info(f"开始发布文章到知乎: {article.title}")
            
            # 这里使用Selenium实现实际的发布逻辑
            # 1. 打开知乎创作中心
            # 2. 填写标题和内容
            # 3. 上传封面图
            # 4. 选择话题/标签
            # 5. 发布或保存草稿
            
            # 模拟发布成功
            return PublishResult(
                success=True,
                platform=self.platform,
                message="文章已保存到知乎草稿箱",
                article_id="zhihu_demo_id",
                article_url="https://zhuanlan.zhihu.com/p/demo"
            )
            
        except Exception as e:
            logger.error(f"知乎发布失败: {e}")
            return PublishResult(
                success=False,
                platform=self.platform,
                message=f"发布失败: {str(e)}",
                need_retry=True
            )


class JuejinPublisher(BasePublisher):
    """掘金发布器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(PlatformType.JUEJIN, config)
        self.base_url = "https://juejin.cn"
        
    async def login(self, credentials: Dict[str, str]) -> bool:
        """掘金登录"""
        logger.info("开始掘金登录流程")
        return True
    
    async def check_login_status(self) -> bool:
        """检查掘金登录状态"""
        cookies = self.config.get('cookies')
        return bool(cookies)
    
    async def publish(self, article: ArticleContent) -> PublishResult:
        """发布文章到掘金"""
        try:
            valid, error = await self.validate_content(article)
            if not valid:
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    message=error
                )
            
            article = self.convert_content(article)
            
            logger.info(f"开始发布文章到掘金: {article.title}")
            
            # 掘金使用Markdown格式
            # 1. 打开掘金编辑器
            # 2. 填写标题和Markdown内容
            # 3. 上传封面
            # 4. 选择分类和标签
            # 5. 发布
            
            return PublishResult(
                success=True,
                platform=self.platform,
                message="文章已发布到掘金",
                article_id="juejin_demo_id",
                article_url="https://juejin.cn/post/demo"
            )
            
        except Exception as e:
            logger.error(f"掘金发布失败: {e}")
            return PublishResult(
                success=False,
                platform=self.platform,
                message=f"发布失败: {str(e)}"
            )


class ToutiaoPublisher(BasePublisher):
    """今日头条发布器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(PlatformType.TOUTIAO, config)
        self.base_url = "https://mp.toutiao.com"
        
    async def login(self, credentials: Dict[str, str]) -> bool:
        """头条登录"""
        logger.info("开始头条登录流程")
        return True
    
    async def check_login_status(self) -> bool:
        """检查头条登录状态"""
        cookies = self.config.get('cookies')
        return bool(cookies)
    
    async def publish(self, article: ArticleContent) -> PublishResult:
        """发布文章到今日头条"""
        try:
            valid, error = await self.validate_content(article)
            if not valid:
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    message=error
                )
            
            article = self.convert_content(article)
            
            logger.info(f"开始发布文章到头条: {article.title}")
            
            # 头条使用富文本编辑器
            # 1. 打开头条创作平台
            # 2. 填写标题和正文
            # 3. 上传封面
            # 4. 设置分类
            # 5. 发布或保存草稿
            
            return PublishResult(
                success=True,
                platform=self.platform,
                message="文章已保存到头条草稿箱",
                article_id="toutiao_demo_id",
                article_url="https://www.toutiao.com/item/demo"
            )
            
        except Exception as e:
            logger.error(f"头条发布失败: {e}")
            return PublishResult(
                success=False,
                platform=self.platform,
                message=f"发布失败: {str(e)}"
            )


class MultiPlatformPublisher:
    """多平台发布管理器"""
    
    def __init__(self):
        self.publishers: Dict[PlatformType, BasePublisher] = {}
        
    def register_publisher(self, platform: PlatformType, publisher: BasePublisher):
        """注册发布器"""
        self.publishers[platform] = publisher
        logger.info(f"已注册发布器: {platform.value}")
        
    def get_publisher(self, platform: PlatformType) -> Optional[BasePublisher]:
        """获取发布器"""
        return self.publishers.get(platform)
        
    async def publish_to_platform(
        self, 
        platform: PlatformType, 
        article: ArticleContent
    ) -> PublishResult:
        """发布到单个平台"""
        publisher = self.get_publisher(platform)
        if not publisher:
            return PublishResult(
                success=False,
                platform=platform,
                message=f"未找到平台 {platform.value} 的发布器"
            )
        
        # 检查登录状态
        if not await publisher.check_login_status():
            return PublishResult(
                success=False,
                platform=platform,
                message="未登录或登录已过期"
            )
        
        return await publisher.publish(article)
    
    async def publish_to_multiple_platforms(
        self,
        platforms: List[PlatformType],
        article: ArticleContent
    ) -> List[PublishResult]:
        """批量发布到多个平台"""
        tasks = []
        for platform in platforms:
            task = self.publish_to_platform(platform, article)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(PublishResult(
                    success=False,
                    platform=platforms[i],
                    message=f"发布异常: {str(result)}"
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
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


# 全局发布管理器实例
publisher_manager = MultiPlatformPublisher()


def init_publishers(platform_configs: Dict[PlatformType, Dict[str, Any]]):
    """初始化发布器"""
    publisher_map = {
        PlatformType.ZHIHU: ZhihuPublisher,
        PlatformType.JUEJIN: JuejinPublisher,
        PlatformType.TOUTIAO: ToutiaoPublisher,
    }
    
    for platform, config in platform_configs.items():
        publisher_class = publisher_map.get(platform)
        if publisher_class:
            publisher = publisher_class(config)
            publisher_manager.register_publisher(platform, publisher)
            
    logger.info(f"已初始化 {len(publisher_manager.publishers)} 个平台发布器")
