from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import feedparser
import asyncio
from ..core.config import settings
from ..core.logger import logger
from ..models.news import NewsItem, NewsSource, NewsCategory


class NewsFetcherService:
    """
    News fetching service supporting multiple sources.
    """

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.sources = {
            NewsSource.ITHOME: {
                "name": "IT之家",
                "rss_url": "https://www.ithome.com/rss/",
                "category": NewsCategory.TECH
            },
            NewsSource.KR36: {
                "name": "36氪",
                "rss_url": "https://36kr.com/feed",
                "category": NewsCategory.BUSINESS
            },
            NewsSource.BAIDU: {
                "name": "百度热搜",
                "api_url": "https://top.baidu.com/api/board?tab=realtime",
                "category": NewsCategory.OTHER
            },
            NewsSource.ZHIHU: {
                "name": "知乎热榜",
                "api_url": "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total",
                "category": NewsCategory.OTHER
            },
            NewsSource.WEIBO: {
                "name": "微博热搜",
                "api_url": "https://weibo.com/ajax/side/hotSearch",
                "category": NewsCategory.ENTERTAINMENT
            }
        }

    async def fetch_news(
        self,
        source: NewsSource,
        limit: int = 50,
        category_filter: Optional[NewsCategory] = None
    ) -> List[NewsItem]:
        """
        Fetch news from specified source.

        Args:
            source: News source to fetch from
            limit: Maximum number of items to fetch
            category_filter: Optional category filter

        Returns:
            List of NewsItem objects
        """
        try:
            if source == NewsSource.ITHOME or source == NewsSource.KR36:
                return await self._fetch_from_rss(source, limit, category_filter)
            elif source == NewsSource.BAIDU:
                return await self._fetch_from_baidu(limit, category_filter)
            elif source == NewsSource.ZHIHU:
                return await self._fetch_from_zhihu(limit, category_filter)
            elif source == NewsSource.WEIBO:
                return await self._fetch_from_weibo(limit, category_filter)
            else:
                logger.warning(f"Unsupported news source: {source}")
                return []

        except Exception as e:
            logger.error(f"Error fetching news from {source}: {str(e)}")
            return []

    async def fetch_all_news(
        self,
        limit_per_source: int = 50
    ) -> List[NewsItem]:
        """
        Fetch news from all configured sources.

        Args:
            limit_per_source: Maximum items per source

        Returns:
            List of NewsItem objects from all sources
        """
        all_news = []

        # Fetch from all sources in parallel
        tasks = [
            self.fetch_news(source, limit_per_source)
            for source in self.sources.keys()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Error in parallel fetch: {str(result)}")

        # Sort by hot score
        all_news.sort(key=lambda x: x.hot_score or 0, reverse=True)

        logger.info(f"Fetched {len(all_news)} news items from all sources")
        return all_news

    async def _fetch_from_rss(
        self,
        source: NewsSource,
        limit: int,
        category_filter: Optional[NewsCategory]
    ) -> List[NewsItem]:
        """Fetch news from RSS feed."""
        try:
            source_config = self.sources[source]
            feed = feedparser.parse(source_config["rss_url"])

            news_items = []
            for entry in feed.entries[:limit]:
                # Parse publication date
                published_at = None
                if hasattr(entry, 'published_parsed'):
                    published_at = datetime(*entry.published_parsed[:6])

                # Extract images from content
                images = []
                if hasattr(entry, 'content'):
                    for content in entry.content:
                        if hasattr(content, 'value'):
                            soup = BeautifulSoup(content.value, 'html.parser')
                            for img in soup.find_all('img'):
                                if img.get('src'):
                                    images.append(img['src'])

                # Determine category
                category = source_config.get("category")
                if category_filter and category != category_filter:
                    continue

                # Calculate hot score (simple algorithm based on freshness)
                hot_score = self._calculate_hot_score(published_at)

                news_item = NewsItem(
                    title=entry.title,
                    summary=entry.get('summary', ''),
                    url=entry.link,
                    source=source,
                    source_name=source_config["name"],
                    category=category,
                    published_at=published_at,
                    hot_score=hot_score,
                    cover_image_url=images[0] if images else None,
                    images=images if images else None
                )

                news_items.append(news_item)

            logger.info(f"Fetched {len(news_items)} items from {source.name} RSS")
            return news_items

        except Exception as e:
            logger.error(f"Error fetching RSS from {source.name}: {str(e)}")
            return []

    async def _fetch_from_baidu(
        self,
        limit: int,
        category_filter: Optional[NewsCategory]
    ) -> List[NewsItem]:
        """Fetch news from Baidu hot search."""
        try:
            response = await self.http_client.get(self.sources[NewsSource.BAIDU]["api_url"])
            response.raise_for_status()
            data = response.json()

            news_items = []
            cards = data.get("data", {}).get("cards", [])

            for card in cards[:limit]:
                for item in card.get("content", []):
                    title = item.get("word", item.get("desc", ""))
                    url = f"https://www.baidu.com/s?wd={title}"

                    # Calculate hot score based on index
                    hot_score = 100 - len(news_items) * 2

                    news_item = NewsItem(
                        title=title,
                        summary=item.get("desc", ""),
                        url=url,
                        source=NewsSource.BAIDU,
                        source_name=self.sources[NewsSource.BAIDU]["name"],
                        category=self.sources[NewsSource.BAIDU]["category"],
                        hot_score=hot_score
                    )

                    news_items.append(news_item)

            logger.info(f"Fetched {len(news_items)} items from Baidu hot search")
            return news_items

        except Exception as e:
            logger.error(f"Error fetching from Baidu: {str(e)}")
            return []

    async def _fetch_from_zhihu(
        self,
        limit: int,
        category_filter: Optional[NewsCategory]
    ) -> List[NewsItem]:
        """Fetch news from Zhihu hot list."""
        try:
            response = await self.http_client.get(
                self.sources[NewsSource.ZHIHU]["api_url"],
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            data = response.json()

            news_items = []
            for item in data.get("data", [])[:limit]:
                target = item.get("target", {})
                title = target.get("title", "")
                url = f"https://www.zhihu.com/question/{target.get('id', '')}"

                # Extract excerpt
                excerpt = target.get("excerpt", "")

                # Calculate hot score based on hot value
                hot_score = item.get("hot_value", 0) / 1000

                news_item = NewsItem(
                    title=title,
                    summary=excerpt,
                    url=url,
                    source=NewsSource.ZHIHU,
                    source_name=self.sources[NewsSource.ZHIHU]["name"],
                    category=self.sources[NewsSource.ZHIHU]["category"],
                    hot_score=hot_score
                )

                news_items.append(news_item)

            logger.info(f"Fetched {len(news_items)} items from Zhihu hot list")
            return news_items

        except Exception as e:
            logger.error(f"Error fetching from Zhihu: {str(e)}")
            return []

    async def _fetch_from_weibo(
        self,
        limit: int,
        category_filter: Optional[NewsCategory]
    ) -> List[NewsItem]:
        """Fetch news from Weibo hot search."""
        try:
            response = await self.http_client.get(
                self.sources[NewsSource.WEIBO]["api_url"],
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            data = response.json()

            news_items = []
            for item in data.get("data", {}).get("realtime", [])[:limit]:
                title = item.get("word", "")
                url = f"https://s.weibo.com/weibo?q={title}"

                # Calculate hot score based on hot value
                hot_score = item.get("num", 0) / 10000

                news_item = NewsItem(
                    title=title,
                    summary=item.get("note", ""),
                    url=url,
                    source=NewsSource.WEIBO,
                    source_name=self.sources[NewsSource.WEIBO]["name"],
                    category=self.sources[NewsSource.WEIBO]["category"],
                    hot_score=hot_score
                )

                news_items.append(news_item)

            logger.info(f"Fetched {len(news_items)} items from Weibo hot search")
            return news_items

        except Exception as e:
            logger.error(f"Error fetching from Weibo: {str(e)}")
            return []

    def _calculate_hot_score(
        self,
        published_at: Optional[datetime]
    ) -> float:
        """
        Calculate hot score based on publication time.

        Args:
            published_at: Publication datetime

        Returns:
            Hot score (0-100)
        """
        if not published_at:
            return 50.0

        time_diff = (datetime.now() - published_at).total_seconds() / 3600  # hours

        # Decay score over time
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
        elif time_diff < 72:
            return 50.0
        else:
            return max(30.0, 50.0 - (time_diff - 72) * 0.5)

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()


# Global instance
news_fetcher_service = NewsFetcherService()