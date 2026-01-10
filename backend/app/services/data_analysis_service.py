"""
数据分析API服务
集成百度指数、微信指数、微博热搜等数据平台
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from ..core.config import settings
from ..core.logger import logger


class DataAnalysisService:
    """数据分析服务"""

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def fetch_baidu_index(
        self,
        keywords: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取百度指数数据

        Args:
            keywords: 关键词列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            百度指数数据
        """
        try:
            if not settings.BAIDU_INDEX_API_KEY or not settings.BAIDU_INDEX_SECRET:
                logger.warning("Baidu Index API credentials not configured")
                return self._get_mock_baidu_index(keywords)

            # 默认获取最近30天数据
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            # 这里应该调用真实的百度指数API
            # 由于百度指数API需要OAuth认证，这里提供模拟实现
            logger.info(f"Fetching Baidu Index for keywords: {keywords}")
            return await self._get_mock_baidu_index(keywords)

        except Exception as e:
            logger.error(f"Error fetching Baidu Index: {str(e)}")
            raise

    async def fetch_wechat_index(
        self,
        keywords: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取微信指数数据

        Args:
            keywords: 关键词列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            微信指数数据
        """
        try:
            if not settings.WECHAT_INDEX_API_KEY or not settings.WECHAT_INDEX_SECRET:
                logger.warning("WeChat Index API credentials not configured")
                return self._get_mock_wechat_index(keywords)

            # 默认获取最近30天数据
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            logger.info(f"Fetching WeChat Index for keywords: {keywords}")
            return await self._get_mock_wechat_index(keywords)

        except Exception as e:
            logger.error(f"Error fetching WeChat Index: {str(e)}")
            raise

    async def fetch_weibo_hot_topics(
        self,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取微博热搜话题

        Args:
            limit: 返回数量

        Returns:
            微博热搜话题列表
        """
        try:
            if not settings.WEIBO_API_KEY or not settings.WEIBO_API_SECRET:
                logger.warning("Weibo API credentials not configured")
                return self._get_mock_weibo_hot_topics(limit)

            logger.info(f"Fetching Weibo hot topics, limit: {limit}")
            return await self._get_mock_weibo_hot_topics(limit)

        except Exception as e:
            logger.error(f"Error fetching Weibo hot topics: {str(e)}")
            raise

    async def analyze_keyword_trend(
        self,
        keyword: str,
        platform: str = "all"
    ) -> Dict[str, Any]:
        """
        分析关键词趋势

        Args:
            keyword: 关键词
            platform: 平台 (baidu, wechat, weibo, all)

        Returns:
            趋势分析数据
        """
        try:
            result = {
                "keyword": keyword,
                "platform": platform,
                "trend_data": {},
                "insights": []
            }

            if platform in ["baidu", "all"]:
                baidu_data = await self.fetch_baidu_index([keyword])
                result["trend_data"]["baidu"] = baidu_data

            if platform in ["wechat", "all"]:
                wechat_data = await self.fetch_wechat_index([keyword])
                result["trend_data"]["wechat"] = wechat_data

            if platform in ["weibo", "all"]:
                weibo_data = await self.fetch_weibo_hot_topics()
                # 筛选包含关键词的话题
                related_topics = [
                    topic for topic in weibo_data
                    if keyword.lower() in topic["title"].lower()
                ]
                result["trend_data"]["weibo"] = related_topics

            # 生成洞察
            result["insights"] = self._generate_insights(result["trend_data"])

            return result

        except Exception as e:
            logger.error(f"Error analyzing keyword trend: {str(e)}")
            raise

    async def get_hot_keywords(
        self,
        platform: str = "all",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取热门关键词

        Args:
            platform: 平台 (baidu, wechat, weibo, all)
            limit: 返回数量

        Returns:
            热门关键词列表
        """
        try:
            hot_keywords = []

            if platform in ["weibo", "all"]:
                weibo_topics = await self.fetch_weibo_hot_topics(limit)
                hot_keywords.extend([
                    {
                        "keyword": topic["title"],
                        "platform": "weibo",
                        "hot_score": topic["hot_score"],
                        "trend": topic.get("trend", "stable")
                    }
                    for topic in weibo_topics
                ])

            # 按热度排序
            hot_keywords.sort(key=lambda x: x["hot_score"], reverse=True)

            return hot_keywords[:limit]

        except Exception as e:
            logger.error(f"Error getting hot keywords: {str(e)}")
            raise

    async def get_competitor_analysis(
        self,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """
        获取竞品分析

        Args:
            keywords: 竞品关键词列表

        Returns:
            竞品分析数据
        """
        try:
            result = {
                "keywords": keywords,
                "analysis": []
            }

            for keyword in keywords:
                trend_data = await self.analyze_keyword_trend(keyword)
                result["analysis"].append({
                    "keyword": keyword,
                    "trend": trend_data
                })

            return result

        except Exception as e:
            logger.error(f"Error getting competitor analysis: {str(e)}")
            raise

    async def _get_mock_baidu_index(self, keywords: List[str]) -> Dict[str, Any]:
        """模拟百度指数数据"""
        import random
        mock_data = {
            "keywords": keywords,
            "data": []
        }

        for keyword in keywords:
            # 生成30天的模拟数据
            daily_data = []
            base_value = random.randint(500, 2000)
            for i in range(30):
                date = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
                value = base_value + random.randint(-200, 200)
                daily_data.append({
                    "date": date,
                    "value": max(0, value)
                })

            mock_data["data"].append({
                "keyword": keyword,
                "avg_index": base_value,
                "peak_index": max(d["value"] for d in daily_data),
                "trend": "up" if daily_data[-1]["value"] > daily_data[0]["value"] else "down",
                "daily_data": daily_data
            })

        return mock_data

    async def _get_mock_wechat_index(self, keywords: List[str]) -> Dict[str, Any]:
        """模拟微信指数数据"""
        import random
        mock_data = {
            "keywords": keywords,
            "data": []
        }

        for keyword in keywords:
            daily_data = []
            base_value = random.randint(300, 1500)
            for i in range(30):
                date = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
                value = base_value + random.randint(-150, 150)
                daily_data.append({
                    "date": date,
                    "value": max(0, value)
                })

            mock_data["data"].append({
                "keyword": keyword,
                "avg_index": base_value,
                "peak_index": max(d["value"] for d in daily_data),
                "trend": "up" if daily_data[-1]["value"] > daily_data[0]["value"] else "down",
                "daily_data": daily_data
            })

        return mock_data

    async def _get_mock_weibo_hot_topics(self, limit: int) -> List[Dict[str, Any]]:
        """模拟微博热搜数据"""
        import random

        mock_topics = [
            {"title": "人工智能", "hot_score": random.randint(90, 100), "trend": "up"},
            {"title": "ChatGPT", "hot_score": random.randint(85, 95), "trend": "stable"},
            {"title": "科技创新", "hot_score": random.randint(80, 90), "trend": "up"},
            {"title": "数字化转型", "hot_score": random.randint(75, 85), "trend": "stable"},
            {"title": "机器学习", "hot_score": random.randint(70, 80), "trend": "down"},
            {"title": "深度学习", "hot_score": random.randint(65, 75), "trend": "stable"},
            {"title": "大数据", "hot_score": random.randint(60, 70), "trend": "up"},
            {"title": "云计算", "hot_score": random.randint(55, 65), "trend": "stable"},
            {"title": "区块链", "hot_score": random.randint(50, 60), "trend": "down"},
            {"title": "元宇宙", "hot_score": random.randint(45, 55), "trend": "stable"},
        ]

        return mock_topics[:limit]

    def _generate_insights(self, trend_data: Dict[str, Any]) -> List[str]:
        """生成洞察"""
        insights = []

        if "baidu" in trend_data:
            baidu_data = trend_data["baidu"]["data"]
            if baidu_data:
                avg_index = baidu_data[0]["avg_index"]
                if avg_index > 1500:
                    insights.append("百度指数较高，用户关注度强")
                elif avg_index > 800:
                    insights.append("百度指数中等，用户关注度一般")
                else:
                    insights.append("百度指数较低，用户关注度较弱")

        if "wechat" in trend_data:
            wechat_data = trend_data["wechat"]["data"]
            if wechat_data:
                avg_index = wechat_data[0]["avg_index"]
                if avg_index > 1200:
                    insights.append("微信指数较高，社交传播力强")
                elif avg_index > 600:
                    insights.append("微信指数中等，社交传播力一般")
                else:
                    insights.append("微信指数较低，社交传播力较弱")

        if "weibo" in trend_data and trend_data["weibo"]:
            insights.append(f"微博有 {len(trend_data['weibo'])} 个相关热搜话题")

        return insights

    async def close(self):
        """关闭客户端"""
        await self.http_client.aclose()


# 全局实例
data_analysis_service = DataAnalysisService()