"""
热门话题获取服务
支持多平台热门话题抓取（微博、知乎、抖音、今日头条等）
实时更新话题列表，话题分类和标签管理，话题热度评分
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from functools import partial
import httpx
from bs4 import BeautifulSoup
import feedparser
from ..core.logger import logger
from ..core.config import settings
from ..core.exceptions import HotspotFetchError


class HotspotSource(str, Enum):
    """热门话题来源枚举"""
    WEIBO = "weibo"
    ZHIHU = "zhihu"
    DOUYIN = "douyin"
    TOUTIAO = "toutiao"
    BILIBILI = "bilibili"
    KR36 = "kr36"        # 36氪
    SSPAI = "sspai"      # 少数派


class HotspotCategory(str, Enum):
    """热门话题分类枚举"""
    TECH = "tech"              # 科技
    SOCIAL = "social"          # 社交
    ENTERTAINMENT = "entertainment"  # 娱乐
    KNOWLEDGE = "knowledge"    # 知识
    NEWS = "news"              # 新闻
    BUSINESS = "business"      # 商业
    LIFE = "life"              # 生活
    EDUCATION = "education"    # 教育
    FINANCE = "finance"        # 财经
    GENERAL = "general"        # 综合


class HotspotService:
    """热门话题获取服务"""

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.cache = {}
        self.cache_duration = 3600  # 缓存1小时
        # 用于执行同步 RSS 解析的线程池
        self._executor = None

    def _get_executor(self):
        """懒加载线程池"""
        if self._executor is None:
            from concurrent.futures import ThreadPoolExecutor
            self._executor = ThreadPoolExecutor(max_workers=3)
        return self._executor

    async def _parse_feed_with_timeout(self, url: str, timeout: float = 5.0):
        """使用线程池和超时解析 RSS Feed"""
        loop = asyncio.get_event_loop()
        try:
            # 在线程池中执行同步的 feedparser.parse
            parse_func = partial(feedparser.parse, url)
            return await asyncio.wait_for(
                loop.run_in_executor(self._get_executor(), parse_func),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"RSS 解析超时: {url}")
            return None
        except Exception as e:
            logger.warning(f"RSS 解析失败: {url} - {str(e)}")
            return None

    async def fetch_weibo_hotspots(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        获取微博热搜话题

        Args:
            count: 获取数量

        Returns:
            话题列表
        """
        try:
            # 使用微博热搜API（需要处理反爬虫）
            url = "https://s.weibo.com/top/summary"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            hotspots = []

            # 解析热搜列表
            items = soup.select('#pl_top_realtimehot table tbody tr')
            for i, item in enumerate(items[:count]):
                try:
                    rank = i + 1
                    title_elem = item.select_one('td a')
                    heat_elem = item.select_one('td span')

                    if title_elem:
                        title = title_elem.text.strip()
                        url = "https://s.weibo.com" + title_elem.get('href', '')
                        heat = heat_elem.text.strip() if heat_elem else "0"

                        hotspots.append({
                            "rank": rank,
                            "title": title,
                            "url": url,
                            "heat": self._parse_heat(heat),
                            "source": HotspotSource.WEIBO.value,
                            "category": "social",
                            "tags": [],
                            "created_at": datetime.utcnow().isoformat()
                        })
                except Exception as e:
                    logger.warning(f"解析微博热搜项失败: {str(e)}")
                    continue

            logger.info(f"成功获取微博热搜话题 {len(hotspots)} 条")
            return hotspots

        except Exception as e:
            logger.error(f"获取微博热搜失败: {str(e)}")
            raise HotspotFetchError(f"获取微博热搜失败: {str(e)}") from e

    async def fetch_zhihu_hotspots(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        获取知乎热榜话题

        Args:
            count: 获取数量

        Returns:
            话题列表
        """
        try:
            # 使用知乎热榜API
            url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            hotspots = []

            for i, item in enumerate(data.get('data', [])[:count]):
                try:
                    target = item.get('target', {})
                    title = target.get('title', '')
                    url = f"https://www.zhihu.com/question/{target.get('id', '')}"
                    heat = item.get('detail_text', '0')

                    hotspots.append({
                        "rank": i + 1,
                        "title": title,
                        "url": url,
                        "heat": self._parse_heat(heat),
                        "source": HotspotSource.ZHIHU.value,
                        "category": "knowledge",
                        "tags": [],
                        "created_at": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"解析知乎热榜项失败: {str(e)}")
                    continue

            logger.info(f"成功获取知乎热榜话题 {len(hotspots)} 条")
            return hotspots

        except Exception as e:
            logger.error(f"获取知乎热榜失败: {str(e)}")
            raise HotspotFetchError(f"获取知乎热榜失败: {str(e)}") from e

    async def fetch_bilibili_hotspots(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        获取B站热门话题

        Args:
            count: 获取数量

        Returns:
            话题列表
        """
        try:
            # 使用B站热门API
            url = "https://api.bilibili.com/x/web-interface/popular"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            hotspots = []

            for i, item in enumerate(data.get('data', {}).get('list', [])[:count]):
                try:
                    title = item.get('title', '')
                    url = f"https://www.bilibili.com/video/{item.get('bvid', '')}"
                    heat = item.get('stat', {}).get('view', 0)

                    hotspots.append({
                        "rank": i + 1,
                        "title": title,
                        "url": url,
                        "heat": heat,
                        "source": HotspotSource.BILIBILI.value,
                        "category": "entertainment",
                        "tags": [],
                        "created_at": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"解析B站热门项失败: {str(e)}")
                    continue

            logger.info(f"成功获取B站热门话题 {len(hotspots)} 条")
            return hotspots

        except Exception as e:
            logger.error(f"获取B站热门失败: {str(e)}")
            raise HotspotFetchError(f"获取B站热门失败: {str(e)}") from e

    async def fetch_weibo_hotspots_rsshub(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        通过 RSSHub 获取微博热搜（备用方案）

        Args:
            count: 获取数量

        Returns:
            话题列表
        """
        try:
            # RSSHub 公共实例
            url = "https://rsshub.app/weibo/search/hot"

            feed = await self._parse_feed_with_timeout(url, timeout=5.0)
            if feed is None:
                return []
            hotspots = []

            for i, entry in enumerate(feed.entries[:count]):
                try:
                    title = entry.title
                    url = entry.link
                    # RSSHub 可能没有提供热度，使用排名作为热度
                    heat = (count - i) * 10000

                    hotspots.append({
                        "rank": i + 1,
                        "title": title,
                        "url": url,
                        "heat": heat,
                        "source": HotspotSource.WEIBO.value,
                        "category": HotspotCategory.SOCIAL.value,
                        "tags": [],
                        "created_at": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"解析微博热搜(RSSHub)项失败: {str(e)}")
                    continue

            logger.info(f"成功获取微博热搜话题(RSSHub) {len(hotspots)} 条")
            return hotspots

        except Exception as e:
            logger.error(f"通过 RSSHub 获取微博热搜失败: {str(e)}")
            # 降级到直接抓取
            return await self.fetch_weibo_hotspots(count)

    async def fetch_zhihu_hotspots_rsshub(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        通过 RSSHub 获取知乎热榜（备用方案）

        Args:
            count: 获取数量

        Returns:
            话题列表
        """
        try:
            # RSSHub 公共实例
            url = "https://rsshub.app/zhihu/hot-list"

            feed = await self._parse_feed_with_timeout(url, timeout=5.0)
            if feed is None:
                return []
            hotspots = []

            for i, entry in enumerate(feed.entries[:count]):
                try:
                    title = entry.title
                    url = entry.link
                    heat = (count - i) * 10000

                    hotspots.append({
                        "rank": i + 1,
                        "title": title,
                        "url": url,
                        "heat": heat,
                        "source": HotspotSource.ZHIHU.value,
                        "category": HotspotCategory.KNOWLEDGE.value,
                        "tags": [],
                        "created_at": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"解析知乎热榜(RSSHub)项失败: {str(e)}")
                    continue

            logger.info(f"成功获取知乎热榜话题(RSSHub) {len(hotspots)} 条")
            return hotspots

        except Exception as e:
            logger.error(f"通过 RSSHub 获取知乎热榜失败: {str(e)}")
            # 降级到直接抓取
            return await self.fetch_zhihu_hotspots(count)

    async def fetch_bilibili_hotspots_rsshub(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        通过 RSSHub 获取B站热门（备用方案）

        Args:
            count: 获取数量

        Returns:
            话题列表
        """
        try:
            # RSSHub 公共实例
            url = "https://rsshub.app/bilibili/popular"

            feed = await self._parse_feed_with_timeout(url, timeout=5.0)
            if feed is None:
                return []
            hotspots = []

            for i, entry in enumerate(feed.entries[:count]):
                try:
                    title = entry.title
                    url = entry.link
                    heat = (count - i) * 10000

                    hotspots.append({
                        "rank": i + 1,
                        "title": title,
                        "url": url,
                        "heat": heat,
                        "source": HotspotSource.BILIBILI.value,
                        "category": HotspotCategory.ENTERTAINMENT.value,
                        "tags": [],
                        "created_at": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"解析B站热门(RSSHub)项失败: {str(e)}")
                    continue

            logger.info(f"成功获取B站热门话题(RSSHub) {len(hotspots)} 条")
            return hotspots

        except Exception as e:
            logger.error(f"通过 RSSHub 获取B站热门失败: {str(e)}")
            # 降级到直接抓取
            return await self.fetch_bilibili_hotspots(count)

    async def fetch_kr36_hotspots(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        获取36氪热点（通过 RSSHub）

        Args:
            count: 获取数量

        Returns:
            话题列表
        """
        try:
            # 使用 RSSHub 获取 36氪 最新文章
            url = "https://rsshub.app/36kr/latest"

            feed = await self._parse_feed_with_timeout(url, timeout=5.0)
            if feed is None:
                return []
            hotspots = []

            for i, entry in enumerate(feed.entries[:count]):
                try:
                    title = entry.title
                    url = entry.link
                    heat = (count - i) * 5000

                    hotspots.append({
                        "rank": i + 1,
                        "title": title,
                        "url": url,
                        "heat": heat,
                        "source": HotspotSource.KR36.value,
                        "category": HotspotCategory.TECH.value,
                        "tags": [],
                        "created_at": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"解析36氪热点项失败: {str(e)}")
                    continue

            logger.info(f"成功获取36氪热点话题 {len(hotspots)} 条")
            return hotspots

        except Exception as e:
            logger.error(f"获取36氪热点失败: {str(e)}")
            raise HotspotFetchError(f"获取36氪热点失败: {str(e)}") from e

    async def fetch_sspai_hotspots(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        获取少数派热点（通过 RSSHub）

        Args:
            count: 获取数量

        Returns:
            话题列表
        """
        try:
            # 使用 RSSHub 获取少数派最新文章
            url = "https://rsshub.app/sspai/latest"

            feed = await self._parse_feed_with_timeout(url, timeout=5.0)
            if feed is None:
                return []
            hotspots = []

            for i, entry in enumerate(feed.entries[:count]):
                try:
                    title = entry.title
                    url = entry.link
                    heat = (count - i) * 5000

                    hotspots.append({
                        "rank": i + 1,
                        "title": title,
                        "url": url,
                        "heat": heat,
                        "source": HotspotSource.SSPAI.value,
                        "category": HotspotCategory.TECH.value,
                        "tags": [],
                        "created_at": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"解析少数派热点项失败: {str(e)}")
                    continue

            logger.info(f"成功获取少数派热点话题 {len(hotspots)} 条")
            return hotspots

        except Exception as e:
            logger.error(f"获取少数派热点失败: {str(e)}")
            raise HotspotFetchError(f"获取少数派热点失败: {str(e)}") from e

    async def fetch_all_hotspots(
        self,
        sources: Optional[List[HotspotSource]] = None,
        count: int = 20
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有来源的热门话题

        Args:
            sources: 来源列表（不指定则获取所有）
            count: 每个来源获取数量

        Returns:
            按来源分类的话题列表
        """
        if sources is None:
            sources = [
                HotspotSource.WEIBO,
                HotspotSource.ZHIHU,
                HotspotSource.BILIBILI,
                HotspotSource.KR36,
                HotspotSource.SSPAI
            ]

        results = {}

        # 并发获取各来源话题，使用 gather 和 return_exceptions 确保部分失败不影响整体
        tasks = []
        source_names = []
        for source in sources:
            if source == HotspotSource.WEIBO:
                tasks.append(self.fetch_weibo_hotspots_rsshub(count))
                source_names.append("weibo")
            elif source == HotspotSource.ZHIHU:
                tasks.append(self.fetch_zhihu_hotspots_rsshub(count))
                source_names.append("zhihu")
            elif source == HotspotSource.BILIBILI:
                tasks.append(self.fetch_bilibili_hotspots_rsshub(count))
                source_names.append("bilibili")
            elif source == HotspotSource.KR36:
                tasks.append(self.fetch_kr36_hotspots(count))
                source_names.append("kr36")
            elif source == HotspotSource.SSPAI:
                tasks.append(self.fetch_sspai_hotspots(count))
                source_names.append("sspai")

        # 使用 gather 并行执行，设置总超时 15 秒
        try:
            completed_tasks = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=15.0
            )
            
            for source_name, result in zip(source_names, completed_tasks):
                if isinstance(result, Exception):
                    logger.error(f"获取 {source_name} 话题失败: {str(result)}")
                    results[source_name] = []
                else:
                    results[source_name] = result
        except asyncio.TimeoutError:
            logger.warning("获取热点数据总超时，返回已有结果")
            # 为未完成的数据源填充空结果
            for source_name in source_names:
                if source_name not in results:
                    results[source_name] = []

        # 更新缓存
        self._update_cache(results)

        return results

    async def get_merged_hotspots(
        self,
        sources: Optional[List[HotspotSource]] = None,
        count: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取合并后的热门话题列表（按热度排序）

        Args:
            sources: 来源列表
            count: 总数量

        Returns:
            合并后的话题列表
        """
        all_hotspots = await self.fetch_all_hotspots(sources)

        # 合并所有话题
        merged = []
        for source_name, hotspots in all_hotspots.items():
            merged.extend(hotspots)

        # 按热度排序
        merged.sort(key=lambda x: x.get('heat', 0), reverse=True)

        # 去重（根据标题相似度）
        unique_hotspots = []
        seen_titles = set()

        for hotspot in merged:
            title = hotspot.get('title', '')
            # 简单去重：标题相似度>80%
            is_duplicate = False
            for seen_title in seen_titles:
                if self._similarity(title, seen_title) > 0.8:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_hotspots.append(hotspot)
                seen_titles.add(title)

            if len(unique_hotspots) >= count:
                break

        return unique_hotspots

    def _parse_heat(self, heat_str: str) -> int:
        """解析热度字符串为数字"""
        try:
            if '万' in heat_str:
                return int(float(heat_str.replace('万', '')) * 10000)
            elif '亿' in heat_str:
                return int(float(heat_str.replace('亿', '')) * 100000000)
            else:
                return int(heat_str.replace(',', ''))
        except:
            return 0

    def _similarity(self, str1: str, str2: str) -> float:
        """计算字符串相似度（简化版）"""
        if not str1 or not str2:
            return 0.0

        set1 = set(str1)
        set2 = set(str2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def _update_cache(self, data: Dict[str, List[Dict[str, Any]]]):
        """更新缓存"""
        self.cache = {
            "data": data,
            "timestamp": datetime.utcnow()
        }

    def _get_cache(self) -> Optional[Dict[str, Any]]:
        """获取缓存"""
        if not self.cache:
            return None

        timestamp = self.cache.get("timestamp")
        if datetime.utcnow() - timestamp > timedelta(seconds=self.cache_duration):
            return None

        return self.cache.get("data")

    async def generate_topic_suggestions(
        self,
        sources: Optional[List[HotspotSource]] = None,
        count: int = 10,
        suggestion_count: int = 5
    ) -> Dict[str, Any]:
        """
        基于热点生成 AI 选题建议

        Args:
            sources: 热点来源列表
            count: 每个来源获取的热点数量
            suggestion_count: 生成的选题建议数量

        Returns:
            选题建议列表
        """
        try:
            # 获取热点数据
            hotspots = await self.get_merged_hotspots(sources, count)

            if not hotspots:
                return {
                    "success": False,
                    "message": "未获取到热点数据",
                    "suggestions": []
                }

            # 取前 15 个热点进行分析
            top_hotspots = hotspots[:15]
            hotspot_list = "\n".join([
                f"{i+1}. {h['title']} (热度: {h['heat']}, 来源: {h['source']})"
                for i, h in enumerate(top_hotspots)
            ])

            # 构建提示词
            prompt = f"""你是一个资深的内容策划专家，擅长从热点中挖掘有价值的选题。

请分析以下热点列表，找出 {suggestion_count} 个适合作为自媒体文章选题的主题。

热点列表：
{hotspot_list}

请输出 {suggestion_count} 个选题建议，每个建议包含：
1. 选题标题（吸引眼球，18-28字）
2. 热度评分（0-100，基于热点热度）
3. 推荐理由（为什么这个选题有价值）
4. 适合的风格（专业/轻松/幽默）
5. 目标读者群
6. 关键词标签（3-5个）

请以JSON格式返回，格式如下：
[
  {{
    "title": "选题标题",
    "heat_score": 85,
    "reason": "推荐理由",
    "style": "专业",
    "target_audience": "目标读者群",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "related_hotspots": ["相关热点1", "相关热点2"]
  }}
]

确保选题标题有吸引力，符合微信生态特点。"""

            # 调用 AI 服务
            from .unified_ai_service import unified_ai_service

            messages = [
                {"role": "system", "content": "你是一个专业的自媒体内容策划专家，擅长从热点中挖掘有价值的选题。"},
                {"role": "user", "content": prompt}
            ]

            response = await unified_ai_service.generate(
                messages=messages,
                temperature=0.7,
                max_tokens=3000
            )

            # 解析 AI 响应
            import json
            import re

            content = response.content

            # 提取 JSON
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                try:
                    suggestions = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    logger.warning("AI 返回的 JSON 解析失败，使用备用解析")
                    suggestions = self._parse_suggestions_fallback(content, suggestion_count)
            else:
                suggestions = self._parse_suggestions_fallback(content, suggestion_count)

            logger.info(f"成功生成 {len(suggestions)} 个选题建议")
            return {
                "success": True,
                "suggestions": suggestions,
                "hotspots_used": len(top_hotspots)
            }

        except Exception as e:
            logger.error(f"生成选题建议失败: {str(e)}")
            return {
                "success": False,
                "message": f"生成选题建议失败: {str(e)}",
                "suggestions": []
            }

    def _parse_suggestions_fallback(self, content: str, count: int) -> List[Dict[str, Any]]:
        """备用选题解析方法"""
        import re

        suggestions = []

        # 尝试提取标题
        title_pattern = r'(?:标题|title)[:：]\s*["\']([^"\']+)["\']'
        titles = re.findall(title_pattern, content, re.IGNORECASE)

        for i, title in enumerate(titles[:count]):
            suggestions.append({
                "title": title,
                "heat_score": max(60, 90 - i * 5),
                "reason": "基于热点分析推荐",
                "style": "专业",
                "target_audience": "科技爱好者",
                "keywords": ["科技", "热点"],
                "related_hotspots": []
            })

        return suggestions

    async def close(self):
        """关闭HTTP客户端"""
        await self.http_client.aclose()


# 全局实例
hotspot_service = HotspotService()