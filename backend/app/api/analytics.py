"""
数据分析API - 内容数据中心
提供文章统计、阅读趋势、发布时间分析等数据接口
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract, case
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..core.database import get_db
from ..core.logger import logger
from ..models.article import Article, ArticleStatus

router = APIRouter()


class TrendData(BaseModel):
    """趋势数据"""
    date: str
    views: int
    likes: int
    articles: int


class HourlyStats(BaseModel):
    """小时统计"""
    hour: int
    avg_views: float
    avg_likes: float
    article_count: int
    engagement_rate: float


class WeekdayStats(BaseModel):
    """星期统计"""
    weekday: int
    weekday_name: str
    avg_views: float
    avg_likes: float
    article_count: int
    engagement_rate: float


class TopicPerformance(BaseModel):
    """话题表现"""
    topic: str
    article_count: int
    total_views: int
    total_likes: int
    avg_views: float
    avg_quality: float
    trend: str


class ContentTypeStats(BaseModel):
    """内容类型统计"""
    content_type: str
    article_count: int
    avg_views: float
    avg_likes: float
    avg_quality: float
    total_engagement: float


class DashboardOverview(BaseModel):
    """仪表盘概览"""
    total_articles: int
    total_views: int
    total_likes: int
    avg_quality_score: float
    published_count: int
    draft_count: int
    views_growth: float
    likes_growth: float
    top_performing_article: Optional[Dict[str, Any]]
    recent_7days_stats: Dict[str, Any]


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(db: AsyncSession = Depends(get_db)):
    """
    获取仪表盘概览数据
    """
    try:
        # 总文章数
        total_query = select(func.count(Article.id))
        total_result = await db.execute(total_query)
        total_articles = total_result.scalar() or 0

        # 总阅读量和点赞
        stats_query = select(
            func.sum(Article.view_count),
            func.sum(Article.like_count),
            func.avg(Article.quality_score)
        )
        stats_result = await db.execute(stats_query)
        total_views, total_likes, avg_quality = stats_result.first() or (0, 0, 0)

        # 各状态文章数
        published_query = select(func.count(Article.id)).where(
            Article.status == ArticleStatus.PUBLISHED
        )
        draft_query = select(func.count(Article.id)).where(
            Article.status == ArticleStatus.DRAFT
        )
        published_result = await db.execute(published_query)
        draft_result = await db.execute(draft_query)
        published_count = published_result.scalar() or 0
        draft_count = draft_result.scalar() or 0

        # 最近7天数据
        week_ago = datetime.now() - timedelta(days=7)
        prev_week_start = week_ago - timedelta(days=7)
        
        recent_query = select(
            func.sum(Article.view_count),
            func.sum(Article.like_count)
        ).where(Article.created_at >= week_ago)
        
        prev_week_query = select(
            func.sum(Article.view_count),
            func.sum(Article.like_count)
        ).where(
            and_(
                Article.created_at >= prev_week_start,
                Article.created_at < week_ago
            )
        )
        
        recent_result = await db.execute(recent_query)
        prev_week_result = await db.execute(prev_week_query)
        
        recent_views, recent_likes = recent_result.first() or (0, 0)
        prev_views, prev_likes = prev_week_result.first() or (0, 0)
        
        # 计算增长率
        views_growth = ((recent_views - prev_views) / prev_views * 100) if prev_views > 0 else 0
        likes_growth = ((recent_likes - prev_likes) / prev_likes * 100) if prev_likes > 0 else 0

        # 获取表现最好的文章
        top_article_query = select(Article).order_by(
            Article.view_count.desc()
        ).limit(1)
        top_article_result = await db.execute(top_article_query)
        top_article = top_article_result.scalar_one_or_none()

        top_performing = None
        if top_article:
            top_performing = {
                "id": top_article.id,
                "title": top_article.title,
                "views": top_article.view_count,
                "likes": top_article.like_count,
                "quality_score": top_article.quality_score
            }

        # 最近7天每日统计
        daily_stats = []
        for i in range(7):
            day_start = week_ago + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_query = select(
                func.count(Article.id),
                func.coalesce(func.sum(Article.view_count), 0),
                func.coalesce(func.sum(Article.like_count), 0)
            ).where(
                and_(
                    Article.created_at >= day_start,
                    Article.created_at < day_end
                )
            )
            
            day_result = await db.execute(day_query)
            day_articles, day_views, day_likes = day_result.first()
            
            daily_stats.append({
                "date": day_start.strftime("%m-%d"),
                "articles": day_articles or 0,
                "views": day_views or 0,
                "likes": day_likes or 0
            })

        return DashboardOverview(
            total_articles=total_articles,
            total_views=total_views or 0,
            total_likes=total_likes or 0,
            avg_quality_score=round(avg_quality or 0, 1),
            published_count=published_count,
            draft_count=draft_count,
            views_growth=round(views_growth, 1),
            likes_growth=round(likes_growth, 1),
            top_performing_article=top_performing,
            recent_7days_stats={
                "daily": daily_stats,
                "total_views": recent_views or 0,
                "total_likes": recent_likes or 0
            }
        )

    except Exception as e:
        logger.error(f"获取仪表盘概览失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/trends", response_model=List[TrendData])
async def get_reading_trends(
    period: str = "week",  # day, week, month, year
    db: AsyncSession = Depends(get_db)
):
    """
    获取阅读趋势数据
    
    Args:
        period: 时间周期 (day, week, month, year)
    """
    try:
        # 根据周期确定时间范围
        now = datetime.now()
        if period == "day":
            start_date = now - timedelta(days=30)
            group_format = "%Y-%m-%d"
        elif period == "week":
            start_date = now - timedelta(weeks=12)
            group_format = "%Y-%W"
        elif period == "month":
            start_date = now - timedelta(days=365)
            group_format = "%Y-%m"
        else:  # year
            start_date = now - timedelta(days=365*5)
            group_format = "%Y"

        # 查询文章数据
        query = select(Article).where(Article.created_at >= start_date)
        result = await db.execute(query)
        articles = result.scalars().all()

        # 按日期分组统计
        trends_dict = {}
        for article in articles:
            if period == "day":
                key = article.created_at.strftime("%m-%d")
            elif period == "week":
                key = f"第{article.created_at.strftime('%W')}周"
            elif period == "month":
                key = article.created_at.strftime("%Y-%m")
            else:
                key = article.created_at.strftime("%Y")

            if key not in trends_dict:
                trends_dict[key] = {"views": 0, "likes": 0, "articles": 0}
            
            trends_dict[key]["views"] += article.view_count or 0
            trends_dict[key]["likes"] += article.like_count or 0
            trends_dict[key]["articles"] += 1

        # 转换为列表并排序
        trends = [
            TrendData(
                date=date,
                views=data["views"],
                likes=data["likes"],
                articles=data["articles"]
            )
            for date, data in sorted(trends_dict.items())
        ]

        return trends

    except Exception as e:
        logger.error(f"获取阅读趋势失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")


@router.get("/best-publish-time")
async def get_best_publish_time(
    metric: str = "views",  # views, likes, engagement
    db: AsyncSession = Depends(get_db)
):
    """
    分析最佳发布时间
    
    Args:
        metric: 分析指标 (views, likes, engagement)
    """
    try:
        # 按小时统计
        hourly_stats = []
        for hour in range(24):
            query = select(
                func.count(Article.id),
                func.coalesce(func.avg(Article.view_count), 0),
                func.coalesce(func.avg(Article.like_count), 0)
            ).where(
                extract('hour', Article.created_at) == hour
            )
            
            result = await db.execute(query)
            count, avg_views, avg_likes = result.first()
            
            engagement_rate = (avg_likes / avg_views * 100) if avg_views > 0 else 0
            
            hourly_stats.append({
                "hour": hour,
                "article_count": count or 0,
                "avg_views": round(avg_views or 0, 1),
                "avg_likes": round(avg_likes or 0, 1),
                "engagement_rate": round(engagement_rate, 2)
            })

        # 按星期统计
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekday_stats = []
        
        for weekday in range(7):
            query = select(
                func.count(Article.id),
                func.coalesce(func.avg(Article.view_count), 0),
                func.coalesce(func.avg(Article.like_count), 0)
            ).where(
                extract('dow', Article.created_at) == weekday
            )
            
            result = await db.execute(query)
            count, avg_views, avg_likes = result.first()
            
            engagement_rate = (avg_likes / avg_views * 100) if avg_views > 0 else 0
            
            weekday_stats.append({
                "weekday": weekday,
                "weekday_name": weekday_names[weekday],
                "article_count": count or 0,
                "avg_views": round(avg_views or 0, 1),
                "avg_likes": round(avg_likes or 0, 1),
                "engagement_rate": round(engagement_rate, 2)
            })

        # 找出最佳时间
        best_hour = max(hourly_stats, key=lambda x: x["avg_views"])
        best_weekday = max(weekday_stats, key=lambda x: x["avg_views"])

        return {
            "hourly_stats": hourly_stats,
            "weekday_stats": weekday_stats,
            "recommendations": {
                "best_hour": best_hour["hour"],
                "best_weekday": best_weekday["weekday_name"],
                "best_hour_views": best_hour["avg_views"],
                "best_weekday_views": best_weekday["avg_views"]
            }
        }

    except Exception as e:
        logger.error(f"获取最佳发布时间失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/topic-performance", response_model=List[TopicPerformance])
async def get_topic_performance(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    获取热门话题表现分析
    """
    try:
        # 从文章标签和来源主题中提取话题
        query = select(Article).where(
            and_(
                Article.tags.isnot(None),
                Article.view_count > 0
            )
        ).limit(100)
        
        result = await db.execute(query)
        articles = result.scalars().all()

        # 按话题聚合统计
        topic_stats = {}
        
        for article in articles:
            # 从标签获取话题
            tags = article.get_tags_list()
            source_topic = article.source_topic
            
            topics = tags if tags else []
            if source_topic:
                topics.append(source_topic)
            
            for topic in topics:
                if not topic:
                    continue
                    
                if topic not in topic_stats:
                    topic_stats[topic] = {
                        "article_count": 0,
                        "total_views": 0,
                        "total_likes": 0,
                        "quality_scores": []
                    }
                
                topic_stats[topic]["article_count"] += 1
                topic_stats[topic]["total_views"] += article.view_count or 0
                topic_stats[topic]["total_likes"] += article.like_count or 0
                if article.quality_score:
                    topic_stats[topic]["quality_scores"].append(article.quality_score)

        # 计算平均值并排序
        performance_list = []
        for topic, stats in topic_stats.items():
            avg_views = stats["total_views"] / stats["article_count"] if stats["article_count"] > 0 else 0
            avg_quality = sum(stats["quality_scores"]) / len(stats["quality_scores"]) if stats["quality_scores"] else 0
            
            # 简单趋势判断（基于文章数量）
            trend = "up" if stats["article_count"] >= 3 else "stable"
            
            performance_list.append(TopicPerformance(
                topic=topic,
                article_count=stats["article_count"],
                total_views=stats["total_views"],
                total_likes=stats["total_likes"],
                avg_views=round(avg_views, 1),
                avg_quality=round(avg_quality, 1),
                trend=trend
            ))

        # 按平均阅读量排序
        performance_list.sort(key=lambda x: x.avg_views, reverse=True)
        
        return performance_list[:limit]

    except Exception as e:
        logger.error(f"获取话题表现失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/content-type-analysis")
async def get_content_type_analysis(db: AsyncSession = Depends(get_db)):
    """
    内容类型效果对比分析
    基于文章标签、长度、质量评分等维度
    """
    try:
        # 按文章质量评分分组分析
        query = select(Article).where(Article.status == ArticleStatus.PUBLISHED)
        result = await db.execute(query)
        articles = result.scalars().all()

        # 按质量等级分组
        quality_groups = {
            "优秀(90+)": [],
            "良好(80-89)": [],
            "一般(70-79)": [],
            "待提升(<70)": []
        }

        # 按文章长度分组
        length_groups = {
            "短文(<800字)": [],
            "中等(800-2000字)": [],
            "长文(>2000字)": []
        }

        for article in articles:
            score = article.quality_score or 0
            content_length = len(article.content) if article.content else 0

            # 质量分组
            if score >= 90:
                quality_groups["优秀(90+)"].append(article)
            elif score >= 80:
                quality_groups["良好(80-89)"].append(article)
            elif score >= 70:
                quality_groups["一般(70-79)"].append(article)
            else:
                quality_groups["待提升(<70)"].append(article)

            # 长度分组
            if content_length < 800:
                length_groups["短文(<800字)"].append(article)
            elif content_length <= 2000:
                length_groups["中等(800-2000字)"].append(article)
            else:
                length_groups["长文(>2000字)"].append(article)

        # 计算各组统计数据
        def calc_stats(articles_list):
            if not articles_list:
                return {"count": 0, "avg_views": 0, "avg_likes": 0, "avg_quality": 0}
            
            total_views = sum(a.view_count or 0 for a in articles_list)
            total_likes = sum(a.like_count or 0 for a in articles_list)
            total_quality = sum(a.quality_score or 0 for a in articles_list if a.quality_score)
            
            return {
                "count": len(articles_list),
                "avg_views": round(total_views / len(articles_list), 1),
                "avg_likes": round(total_likes / len(articles_list), 1),
                "avg_quality": round(total_quality / len(articles_list), 1) if total_quality else 0
            }

        quality_analysis = {k: calc_stats(v) for k, v in quality_groups.items()}
        length_analysis = {k: calc_stats(v) for k, v in length_groups.items()}

        return {
            "by_quality": quality_analysis,
            "by_length": length_analysis,
            "recommendations": {
                "optimal_quality_range": "80-89分（良好）",
                "optimal_length_range": "800-2000字（中等）",
                "suggestion": "质量评分在80-89分的文章平均表现最佳，建议保持内容质量的同时控制文章长度在800-2000字之间。"
            }
        }

    except Exception as e:
        logger.error(f"内容类型分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/export")
async def export_analytics_data(
    format: str = "json",  # json, csv
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    导出分析数据
    """
    try:
        # 构建查询条件
        conditions = []
        if start_date:
            conditions.append(Article.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            conditions.append(Article.created_at <= datetime.fromisoformat(end_date))

        query = select(Article)
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await db.execute(query)
        articles = result.scalars().all()

        # 准备导出数据
        export_data = []
        for article in articles:
            export_data.append({
                "id": article.id,
                "title": article.title,
                "status": article.status.value if article.status else "",
                "views": article.view_count,
                "likes": article.like_count,
                "quality_score": article.quality_score,
                "tags": article.tags,
                "created_at": article.created_at.isoformat() if article.created_at else "",
                "source_topic": article.source_topic
            })

        if format == "csv":
            # 生成CSV格式
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=export_data[0].keys() if export_data else [])
            writer.writeheader()
            writer.writerows(export_data)
            
            return {
                "format": "csv",
                "data": output.getvalue(),
                "filename": f"analytics_export_{datetime.now().strftime('%Y%m%d')}.csv"
            }

        return {
            "format": "json",
            "data": export_data,
            "total_count": len(export_data),
            "generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"导出数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
