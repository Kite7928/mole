from typing import List
import httpx
from datetime import datetime
from bs4 import BeautifulSoup
import feedparser
from ..core.config import settings
from ..core.logger import logger
from ..models.news import NewsItem, NewsSource


class NewsFetcherService:
    """热点新闻抓取服务 - 简化版（仅IT之家和百度资讯）"""

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.sources = {
            NewsSource.ITHOME: {
                "name": "IT之家",
                "rss_url": "https://www.ithome.com/rss/",
            },
            NewsSource.BAIDU: {
                "name": "百度资讯",
                "rss_url": "http://news.baidu.com/ns?word=AI&tn=news&rtt=1&bsst=1&cl=2&wd=&ie=utf-8",
            }
        }

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
            if source == NewsSource.ITHOME:
                return await self._fetch_from_ithome(limit)
            elif source == NewsSource.BAIDU:
                return await self._fetch_from_baidu(limit)
            else:
                logger.warning(f"不支持的新闻源: {source}")
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
        all_news = []

        # 并行抓取所有源
        tasks = [
            self.fetch_news(source, limit_per_source)
            for source in [NewsSource.ITHOME, NewsSource.BAIDU]
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_news.extend(result)

        # 按热度排序
        all_news.sort(key=lambda x: x.hot_score or 0, reverse=True)

        logger.info(f"从所有源抓取了 {len(all_news)} 条新闻")
        return all_news

    async def _fetch_from_ithome(self, limit: int) -> List[NewsItem]:
        """从IT之家RSS抓取"""
        try:
            feed = feedparser.parse(self.sources[NewsSource.ITHOME]["rss_url"])

            news_items = []
            for entry in feed.entries[:limit]:
                # 解析发布时间
                published_at = None
                if hasattr(entry, 'published_parsed'):
                    published_at = datetime(*entry.published_parsed[:6])

                # 提取封面图
                cover_image = None
                if hasattr(entry, 'content'):
                    for content in entry.content:
                        if hasattr(content, 'value'):
                            soup = BeautifulSoup(content.value, 'html.parser')
                            img = soup.find('img')
                            if img and img.get('src'):
                                cover_image = img['src']
                                break

                # 计算热度
                hot_score = self._calculate_hot_score(published_at)

                news_item = NewsItem(
                    title=entry.title,
                    summary=entry.get('summary', ''),
                    url=entry.link,
                    source=NewsSource.ITHOME,
                    source_name=self.sources[NewsSource.ITHOME]["name"],
                    published_at=published_at,
                    hot_score=hot_score,
                    cover_image_url=cover_image
                )

                news_items.append(news_item)

            logger.info(f"从IT之家抓取了 {len(news_items)} 条新闻")
            return news_items

        except Exception as e:
            logger.error(f"从IT之家抓取失败: {str(e)}")
            return []

    async def _fetch_from_baidu(self, limit: int) -> List[NewsItem]:
        """从百度资讯抓取"""
        try:
            # 使用百度资讯的API
            url = "https://www.baidu.com/s"
            params = {
                "wd": "AI人工智能",
                "tn": "news",
                "rtt": "1",
                "bsst": "1",
                "cl": "2",
                "ie": "utf-8"
            }

            response = await self.http_client.get(url, params=params)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []

            # 解析百度新闻列表
            for item in soup.select('.result')[:limit]:
                title_elem = item.select_one('.t a')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')

                # 摘要
                summary_elem = item.select_one('.c-abstract')
                summary = summary_elem.get_text(strip=True) if summary_elem else ''

                # 来源和时间
                info_elem = item.select_one('.c-color-gray')
                info = info_elem.get_text(strip=True) if info_elem else ''

                # 计算热度（简化算法）
                hot_score = 70.0

                news_item = NewsItem(
                    title=title,
                    summary=summary,
                    url=url,
                    source=NewsSource.BAIDU,
                    source_name=self.sources[NewsSource.BAIDU]["name"],
                    hot_score=hot_score
                )

                news_items.append(news_item)

            logger.info(f"从百度资讯抓取了 {len(news_items)} 条新闻")
            return news_items

        except Exception as e:
            logger.error(f"从百度资讯抓取失败: {str(e)}")
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

        time_diff = (datetime.now() - published_at).total_seconds() / 3600  # 小时

        # 随时间衰减
        if time_diff < 1:
            return 100.0
        elif time_diff < 6:
            return 90.0
        elif time_diff < 12:
            return 80.0
        elif time_diff < 24:
            return 70.0
        elif time_diff < 48:
            return 60.0
        else:
            return 50.0

    async def close(self):
        """关闭HTTP客户端"""
        await self.http_client.aclose()


# 全局实例
news_fetcher_service = NewsFetcherService()