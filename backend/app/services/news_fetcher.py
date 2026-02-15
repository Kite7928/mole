from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

import httpx
import feedparser
from bs4 import BeautifulSoup
from sqlalchemy import select

from ..core.config import settings
from ..core.logger import logger
from ..core.database import async_session_maker
from ..models.news import NewsItem, NewsSource
from ..models.rss_source import RssSource as RssSourceModel


class NewsFetcherService:
    """热点新闻抓取服务 - 扩展版（官方源 + RSSHub + 自定义源）"""

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.rss_fetch_retries = max(1, int(settings.RSS_FETCH_RETRIES))
        self.rss_fetch_retry_delay = max(0.2, float(settings.RSS_FETCH_RETRY_DELAY))
        self.rsshub_base_url = (settings.RSSHUB_BASE_URL or "").strip().rstrip("/")

        # 官方 RSS 源（优先直连，失败后可回退 RSSHub）
        self.sources = {
            NewsSource.ITHOME: {
                "name": "IT之家",
                "rss_url": "https://www.ithome.com/rss/",
                "rsshub_route": "/ithome/rss",
                "type": "rss"
            },
            NewsSource.KR36: {
                "name": "36氪",
                "rss_url": "https://36kr.com/feed",
                "rsshub_route": "/36kr/newsflashes",
                "type": "rss"
            },
            NewsSource.SSPAI: {
                "name": "少数派",
                "rss_url": "https://sspai.com/feed",
                "rsshub_route": "/sspai/index",
                "type": "rss"
            },
            NewsSource.HUXIU: {
                "name": "虎嗅",
                "rss_url": "https://www.huxiu.com/rss/0.xml",
                "rsshub_route": "/huxiu/channel/0",
                "type": "rss"
            },
            NewsSource.INFOQ: {
                "name": "InfoQ",
                "rss_url": "https://www.infoq.cn/feed",
                "rsshub_route": "/infoq/topic/12",
                "type": "rss"
            },
            NewsSource.OSCHINA: {
                "name": "开源中国",
                "rss_url": "https://www.oschina.net/news/rss",
                "rsshub_route": "/oschina/news",
                "type": "rss"
            },
        }

        # 扩展源（可配置原生 RSS URL 或 RSSHub 路由）
        self.extended_sources: Dict[str, Dict[str, Any]] = {}

    def _resolve_rss_url(self, raw_url: str) -> str:
        """解析 RSS 地址，支持 http(s) URL、rsshub:// 路由、/path 路由。"""
        url = (raw_url or "").strip()
        if not url:
            return ""

        if url.startswith("rsshub://"):
            if not self.rsshub_base_url:
                raise ValueError("RSSHUB_BASE_URL 未配置，无法解析 rsshub:// 路由")
            path = url.replace("rsshub://", "", 1)
            return f"{self.rsshub_base_url}/{path.lstrip('/')}"

        if url.startswith("/"):
            if not self.rsshub_base_url:
                raise ValueError("RSSHUB_BASE_URL 未配置，无法解析相对 RSSHub 路由")
            return f"{self.rsshub_base_url}{url}"

        return url

    async def _fetch_feed_with_retry(self, rss_url: str, source_name: str) -> Optional[Any]:
        """抓取并解析 RSS，带重试能力。"""
        resolved_url = self._resolve_rss_url(rss_url)
        if not resolved_url:
            return None

        last_error = "未知错误"
        for attempt in range(1, self.rss_fetch_retries + 1):
            try:
                response = await self.http_client.get(resolved_url)
                response.raise_for_status()

                feed = feedparser.parse(response.content)
                entries = getattr(feed, "entries", None) or []

                if entries:
                    return feed

                last_error = "RSS返回0条内容"

            except Exception as e:
                last_error = str(e)

            if attempt < self.rss_fetch_retries:
                await asyncio.sleep(self.rss_fetch_retry_delay * attempt)

        logger.warning(
            f"RSS抓取失败 source={source_name} url={resolved_url} retries={self.rss_fetch_retries} error={last_error}"
        )
        return None

    def _extract_cover_image(self, entry: Any) -> Optional[str]:
        """从 RSS entry 中提取封面图。"""
        if hasattr(entry, "content"):
            for content in entry.content:
                if hasattr(content, "value"):
                    soup = BeautifulSoup(content.value, "html.parser")
                    img = soup.find("img")
                    if img and img.get("src"):
                        return img["src"]

        if hasattr(entry, "enclosures"):
            for enclosure in entry.enclosures:
                if enclosure.get("type", "").startswith("image/"):
                    return enclosure.get("href")

        return None

    def _extract_news_items_from_feed(
        self,
        feed: Any,
        source: NewsSource,
        source_name: str,
        limit: int,
        summary_limit: int = 300,
    ) -> List[NewsItem]:
        """将 feed 解析为 NewsItem 列表。"""
        news_items: List[NewsItem] = []

        for entry in (getattr(feed, "entries", None) or [])[:limit]:
            # 解析发布时间
            published_at = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])

            # 提取封面图
            cover_image = self._extract_cover_image(entry)

            # 清理摘要
            summary = entry.get("summary", "")
            if summary:
                soup = BeautifulSoup(summary, "html.parser")
                summary = soup.get_text(strip=True)
                if summary_limit > 0:
                    summary = summary[:summary_limit]

            title = (entry.get("title") or "无标题")[:500]
            link = (entry.get("link") or "").strip()
            if not link:
                continue

            # 计算热度
            hot_score = self._calculate_hot_score(published_at)

            news_items.append(
                NewsItem(
                    title=title,
                    summary=summary,
                    url=link,
                    source=source,
                    source_name=source_name,
                    published_at=published_at,
                    hot_score=hot_score,
                    cover_image_url=cover_image,
                )
            )

        return news_items

    async def fetch_news(self, source: NewsSource, limit: int = 20) -> List[NewsItem]:
        """
        从指定源抓取新闻

        Args:
            source: 新闻源
            limit: 最大数量

        Returns:
            NewsItem列表
        """
        try:
            source_info = self.sources.get(source)
            if not source_info:
                logger.warning(f"不支持的新闻源: {source}")
                return []

            source_type = source_info.get("type")

            if source_type == "rss":
                return await self._fetch_from_rss(source, limit)

            logger.warning(f"不支持的新闻源类型: {source_type}")
            return []

        except Exception as e:
            logger.error(f"从 {source} 抓取新闻失败: {str(e)}")
            return []

    async def fetch_all_news(self, limit_per_source: int = 10) -> List[NewsItem]:
        """
        从所有源抓取新闻

        Args:
            limit_per_source: 每个源的最大数量

        Returns:
            所有源的NewsItem列表
        """
        all_news: List[NewsItem] = []

        tasks = [self.fetch_news(source, limit_per_source) for source in self.sources.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"抓取任务失败: {str(result)}")

        # 按热度排序
        all_news.sort(key=lambda x: x.hot_score or 0, reverse=True)

        logger.info(f"从所有源抓取了 {len(all_news)} 条新闻")
        return all_news

    async def _fetch_from_rss(self, source: NewsSource, limit: int) -> List[NewsItem]:
        """从官方 RSS 源抓取新闻（带 RSSHub 回退）"""
        try:
            source_info = self.sources[source]

            candidate_urls: List[str] = []
            if source_info.get("rss_url"):
                candidate_urls.append(source_info["rss_url"])

            # 失败时回退 RSSHub 路由
            rsshub_route = source_info.get("rsshub_route")
            if rsshub_route and self.rsshub_base_url:
                candidate_urls.append(rsshub_route)

            for index, candidate_url in enumerate(candidate_urls):
                feed = await self._fetch_feed_with_retry(candidate_url, source_info["name"])
                if not feed:
                    continue

                news_items = self._extract_news_items_from_feed(
                    feed=feed,
                    source=source,
                    source_name=source_info["name"],
                    limit=limit,
                    summary_limit=300,
                )

                if news_items:
                    if index > 0:
                        resolved_url = self._resolve_rss_url(candidate_url)
                        logger.info(f"源 {source_info['name']} 已启用RSSHub回退: {resolved_url}")

                    logger.info(f"从 {source_info['name']} 抓取了 {len(news_items)} 条新闻")
                    return news_items

            logger.warning(f"源 {source_info['name']} 抓取失败，直连与回退均未命中有效内容")
            return []

        except Exception as e:
            logger.error(f"从 {source} RSS抓取失败: {str(e)}")
            return []

    def _calculate_hot_score(self, published_at: datetime) -> float:
        """
        根据发布时间计算热度分数

        Args:
            published_at: 发布时间

        Returns:
            热度分数 (0-100)
        """
        if not published_at:
            return 70.0

        time_diff = (datetime.now() - published_at).total_seconds() / 3600

        if time_diff < 1:
            return 100.0
        if time_diff < 6:
            return 90.0
        if time_diff < 12:
            return 80.0
        if time_diff < 24:
            return 70.0
        if time_diff < 48:
            return 60.0
        return 50.0

    def get_all_sources(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有可用的新闻源（包括官方源、扩展源）

        Returns:
            所有源的字典
        """
        all_sources: Dict[str, Dict[str, Any]] = {}

        # 添加官方源
        for source_enum, source_info in self.sources.items():
            all_sources[source_enum.value] = {
                **source_info,
                "value": source_enum.value,
                "is_official": True,
            }

        # 添加扩展源
        for source_id, source_info in self.extended_sources.items():
            all_sources[source_id] = {
                **source_info,
                "value": source_id,
                "is_official": True,
                "is_extended": True,
            }

        return all_sources

    async def get_custom_sources_from_db(self) -> List[RssSourceModel]:
        """
        从数据库获取启用的自定义RSS源

        Returns:
            自定义RSS源列表
        """
        try:
            async with async_session_maker() as session:
                result = await session.execute(
                    select(RssSourceModel).where(RssSourceModel.is_active == True)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"获取自定义RSS源失败: {str(e)}")
            return []

    async def fetch_from_extended_source(self, source_id: str, limit: int = 20) -> List[NewsItem]:
        """
        从扩展源抓取新闻

        Args:
            source_id: 源ID
            limit: 最大数量

        Returns:
            NewsItem列表
        """
        try:
            source_info = self.extended_sources.get(source_id)
            if not source_info:
                logger.warning(f"不支持的扩展源: {source_id}")
                return []

            rss_url = source_info.get("rss_url")
            if not rss_url:
                logger.warning(f"扩展源 {source_id} 没有配置RSS地址")
                return []

            feed = await self._fetch_feed_with_retry(rss_url, source_info["name"])
            if not feed:
                return []

            news_items = self._extract_news_items_from_feed(
                feed=feed,
                source=NewsSource.OTHER,
                source_name=source_info["name"],
                limit=limit,
                summary_limit=300,
            )

            logger.info(f"从扩展源 {source_info['name']} 抓取了 {len(news_items)} 条新闻")
            return news_items

        except Exception as e:
            logger.error(f"从扩展源 {source_id} 抓取失败: {str(e)}")
            return []

    async def fetch_from_custom_source(self, custom_source: RssSourceModel, limit: int = 20) -> List[NewsItem]:
        """
        从自定义RSS源抓取新闻

        Args:
            custom_source: 自定义RSS源模型
            limit: 最大数量

        Returns:
            NewsItem列表
        """
        try:
            feed = await self._fetch_feed_with_retry(custom_source.url, custom_source.name)
            if not feed:
                custom_source.last_error = "抓取失败或无可用条目"
                return []

            news_items = self._extract_news_items_from_feed(
                feed=feed,
                source=NewsSource.OTHER,
                source_name=custom_source.name,
                limit=limit,
                summary_limit=300,
            )

            if news_items:
                custom_source.last_error = None
            else:
                custom_source.last_error = "抓取成功但无有效条目"

            logger.info(f"从自定义源 {custom_source.name} 抓取了 {len(news_items)} 条新闻")
            return news_items

        except Exception as e:
            logger.error(f"从自定义源 {custom_source.name} 抓取失败: {str(e)}")
            custom_source.last_error = str(e)[:500]
            return []

    async def fetch_all_news_extended(self, limit_per_source: int = 10, include_custom: bool = True) -> List[NewsItem]:
        """
        从所有源抓取新闻（包括官方源、扩展源和自定义源）

        Args:
            limit_per_source: 每个源的最大数量
            include_custom: 是否包含自定义源

        Returns:
            所有源的NewsItem列表
        """
        all_news: List[NewsItem] = []
        tasks = []

        # 1. 官方源任务
        for source in self.sources.keys():
            tasks.append(("official", source, self.fetch_news(source, limit_per_source)))

        # 2. 扩展源任务
        for source_id in self.extended_sources.keys():
            tasks.append(("extended", source_id, self.fetch_from_extended_source(source_id, limit_per_source)))

        # 3. 自定义源任务
        if include_custom:
            custom_sources = await self.get_custom_sources_from_db()
            for custom_source in custom_sources:
                tasks.append(("custom", custom_source.id, self.fetch_from_custom_source(custom_source, limit_per_source)))

        if not tasks:
            return []

        # 执行所有任务
        results = await asyncio.gather(*[task[2] for task in tasks], return_exceptions=True)

        # 处理结果
        for i, result in enumerate(results):
            source_type, source_id, _ = tasks[i]
            if isinstance(result, list):
                all_news.extend(result)
                logger.info(f"{source_type} 源 {source_id} 抓取成功，获取 {len(result)} 条")
            elif isinstance(result, Exception):
                logger.error(f"{source_type} 源 {source_id} 抓取失败: {str(result)}")

        # 按热度排序
        all_news.sort(key=lambda x: x.hot_score or 0, reverse=True)

        logger.info(f"从所有源共抓取了 {len(all_news)} 条新闻")
        return all_news

    async def close(self):
        """关闭HTTP客户端"""
        await self.http_client.aclose()


# 全局实例
news_fetcher_service = NewsFetcherService()

