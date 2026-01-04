from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from ..core.database import get_db
from ..core.logger import logger
from ..models.article import Article, ArticleStatus
from ..models.news import NewsItem, NewsSource

router = APIRouter()


# Pydantic models
class OverviewStats(BaseModel):
    total_articles: int
    published_articles: int
    total_reads: int
    total_likes: int
    total_shares: int
    total_comments: int
    avg_read_count: float
    success_rate: float


class DailyStats(BaseModel):
    date: str
    articles: int
    reads: int
    likes: int
    shares: int


class ArticleRanking(BaseModel):
    id: int
    title: str
    read_count: int
    like_count: int
    share_count: int
    comment_count: int
    published_at: datetime


class SourceStats(BaseModel):
    source: str
    count: int
    percentage: float


class CategoryStats(BaseModel):
    category: str
    count: int
    percentage: float


# Endpoints
@router.get("/overview", response_model=OverviewStats)
async def get_overview_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get overview statistics."""
    try:
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)

        # Total articles
        total_result = await db.execute(
            select(func.count(Article.id)).where(
                and_(
                    Article.created_at >= start_date,
                    Article.status != ArticleStatus.FAILED
                )
            )
        )
        total_articles = total_result.scalar() or 0

        # Published articles
        published_result = await db.execute(
            select(func.count(Article.id)).where(
                and_(
                    Article.created_at >= start_date,
                    Article.status == ArticleStatus.PUBLISHED
                )
            )
        )
        published_articles = published_result.scalar() or 0

        # Total reads
        reads_result = await db.execute(
            select(func.sum(Article.read_count)).where(
                Article.created_at >= start_date
            )
        )
        total_reads = reads_result.scalar() or 0

        # Total likes
        likes_result = await db.execute(
            select(func.sum(Article.like_count)).where(
                Article.created_at >= start_date
            )
        )
        total_likes = likes_result.scalar() or 0

        # Total shares
        shares_result = await db.execute(
            select(func.sum(Article.share_count)).where(
                Article.created_at >= start_date
            )
        )
        total_shares = shares_result.scalar() or 0

        # Total comments
        comments_result = await db.execute(
            select(func.sum(Article.comment_count)).where(
                Article.created_at >= start_date
            )
        )
        total_comments = comments_result.scalar() or 0

        # Average read count
        avg_read_count = total_reads / published_articles if published_articles > 0 else 0

        # Success rate (published / total)
        success_rate = (published_articles / total_articles * 100) if total_articles > 0 else 0

        return OverviewStats(
            total_articles=total_articles,
            published_articles=published_articles,
            total_reads=total_reads,
            total_likes=total_likes,
            total_shares=total_shares,
            total_comments=total_comments,
            avg_read_count=round(avg_read_count, 2),
            success_rate=round(success_rate, 2)
        )

    except Exception as e:
        logger.error(f"Error getting overview stats: {str(e)}")
        raise


@router.get("/daily", response_model=List[DailyStats])
async def get_daily_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    db: AsyncSession = Depends(get_db)
):
    """Get daily statistics."""
    try:
        stats = []
        end_date = datetime.utcnow()

        for i in range(days):
            date = end_date - timedelta(days=days - i)
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)

            # Articles published on this day
            articles_result = await db.execute(
                select(func.count(Article.id)).where(
                    and_(
                        Article.published_at >= start_of_day,
                        Article.published_at < end_of_day
                    )
                )
            )
            articles_count = articles_result.scalar() or 0

            # Reads on this day
            reads_result = await db.execute(
                select(func.sum(Article.read_count)).where(
                    Article.published_at >= start_of_day
                )
            )
            reads = reads_result.scalar() or 0

            # Likes on this day
            likes_result = await db.execute(
                select(func.sum(Article.like_count)).where(
                    Article.published_at >= start_of_day
                )
            )
            likes = likes_result.scalar() or 0

            # Shares on this day
            shares_result = await db.execute(
                select(func.sum(Article.share_count)).where(
                    Article.published_at >= start_of_day
                )
            )
            shares = shares_result.scalar() or 0

            stats.append(DailyStats(
                date=date.strftime("%Y-%m-%d"),
                articles=articles_count,
                reads=reads,
                likes=likes,
                shares=shares
            ))

        return stats

    except Exception as e:
        logger.error(f"Error getting daily stats: {str(e)}")
        raise


@router.get("/top-articles", response_model=List[ArticleRanking])
async def get_top_articles(
    limit: int = Query(10, ge=1, le=50, description="Number of articles"),
    sort_by: str = Query("read_count", description="Sort by field"),
    db: AsyncSession = Depends(get_db)
):
    """Get top performing articles."""
    try:
        # Validate sort_by
        valid_sort_fields = ["read_count", "like_count", "share_count", "comment_count"]
        if sort_by not in valid_sort_fields:
            sort_by = "read_count"

        # Build query
        query = select(Article).where(
            Article.status == ArticleStatus.PUBLISHED
        ).order_by(getattr(Article, sort_by).desc()).limit(limit)

        result = await db.execute(query)
        articles = result.scalars().all()

        return [
            ArticleRanking(
                id=article.id,
                title=article.title,
                read_count=article.read_count,
                like_count=article.like_count,
                share_count=article.share_count,
                comment_count=article.comment_count,
                published_at=article.published_at
            )
            for article in articles
        ]

    except Exception as e:
        logger.error(f"Error getting top articles: {str(e)}")
        raise


@router.get("/sources", response_model=List[SourceStats])
async def get_source_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get statistics by article source."""
    try:
        # Get all articles by source
        result = await db.execute(
            select(Article.source, func.count(Article.id))
            .where(Article.status != ArticleStatus.FAILED)
            .group_by(Article.source)
        )

        source_data = result.all()

        # Calculate total
        total = sum(count for _, count in source_data)

        # Build response
        stats = []
        for source, count in source_data:
            stats.append(SourceStats(
                source=source.value if source else "unknown",
                count=count,
                percentage=round(count / total * 100, 2) if total > 0 else 0
            ))

        return sorted(stats, key=lambda x: x.count, reverse=True)

    except Exception as e:
        logger.error(f"Error getting source stats: {str(e)}")
        raise


@router.get("/news-sources", response_model=List[SourceStats])
async def get_news_source_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get statistics by news source."""
    try:
        # Get all news items by source
        result = await db.execute(
            select(NewsItem.source, func.count(NewsItem.id))
            .group_by(NewsItem.source)
        )

        source_data = result.all()

        # Calculate total
        total = sum(count for _, count in source_data)

        # Build response
        stats = []
        for source, count in source_data:
            stats.append(SourceStats(
                source=source.value if source else "unknown",
                count=count,
                percentage=round(count / total * 100, 2) if total > 0 else 0
            ))

        return sorted(stats, key=lambda x: x.count, reverse=True)

    except Exception as e:
        logger.error(f"Error getting news source stats: {str(e)}")
        raise


@router.get("/trends")
async def get_trends(
    days: int = Query(30, ge=7, le=365, description="Number of days"),
    db: AsyncSession = Depends(get_db)
):
    """Get trend analysis data."""
    try:
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get articles created over time
        result = await db.execute(
            select(
                func.date(Article.created_at).label('date'),
                func.count(Article.id).label('count')
            )
            .where(Article.created_at >= start_date)
            .group_by(func.date(Article.created_at))
            .order_by(func.date(Article.created_at))
        )

        article_trends = [{"date": str(row.date), "count": row.count} for row in result]

        # Get average quality score over time
        result = await db.execute(
            select(
                func.date(Article.created_at).label('date'),
                func.avg(Article.quality_score).label('avg_score')
            )
            .where(
                and_(
                    Article.created_at >= start_date,
                    Article.quality_score.isnot(None)
                )
            )
            .group_by(func.date(Article.created_at))
            .order_by(func.date(Article.created_at))
        )

        quality_trends = [
            {"date": str(row.date), "score": round(row.avg_score, 2) if row.avg_score else 0}
            for row in result
        ]

        return {
            "article_trends": article_trends,
            "quality_trends": quality_trends
        }

    except Exception as e:
        logger.error(f"Error getting trends: {str(e)}")
        raise


@router.get("/performance")
async def get_performance_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get performance statistics."""
    try:
        # Get articles with quality scores
        result = await db.execute(
            select(
                func.avg(Article.quality_score).label('avg_quality'),
                func.max(Article.quality_score).label('max_quality'),
                func.min(Article.quality_score).label('min_quality')
            )
            .where(Article.quality_score.isnot(None))
        )

        quality_stats = result.one()

        # Get articles with predicted click rates
        result = await db.execute(
            select(
                func.avg(Article.predicted_click_rate).label('avg_ctr'),
                func.max(Article.predicted_click_rate).label('max_ctr')
            )
            .where(Article.predicted_click_rate.isnot(None))
        )

        ctr_stats = result.one()

        return {
            "quality": {
                "average": round(quality_stats.avg_quality, 2) if quality_stats.avg_quality else 0,
                "max": round(quality_stats.max_quality, 2) if quality_stats.max_quality else 0,
                "min": round(quality_stats.min_quality, 2) if quality_stats.min_quality else 0
            },
            "click_through_rate": {
                "average": round(ctr_stats.avg_ctr, 2) if ctr_stats.avg_ctr else 0,
                "max": round(ctr_stats.max_ctr, 2) if ctr_stats.max_ctr else 0
            }
        }

    except Exception as e:
        logger.error(f"Error getting performance stats: {str(e)}")
        raise