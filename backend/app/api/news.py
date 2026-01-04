from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from ..core.database import get_db
from ..core.logger import logger
from ..models.news import NewsItem, NewsSource, NewsCategory
from ..services.news_fetcher import news_fetcher_service

router = APIRouter()


# Pydantic models
class NewsResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    url: str
    source: NewsSource
    source_name: str
    category: Optional[NewsCategory]
    hot_score: float
    cover_image_url: Optional[str]
    published_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class NewsFetchRequest(BaseModel):
    source: NewsSource = Field(..., description="News source")
    limit: int = Field(50, ge=1, le=100, description="Maximum items to fetch")
    category_filter: Optional[NewsCategory] = Field(None, description="Category filter")


# Endpoints
@router.post("/fetch", response_model=List[NewsResponse])
async def fetch_news(request: NewsFetchRequest):
    """Fetch news from specified source."""
    try:
        logger.info(f"Fetching news from {request.source.name}")

        news_items = await news_fetcher_service.fetch_news(
            source=request.source,
            limit=request.limit,
            category_filter=request.category_filter
        )

        return news_items

    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch/all", response_model=List[NewsResponse])
async def fetch_all_news(
    limit_per_source: int = Query(50, ge=1, le=100, description="Maximum items per source")
):
    """Fetch news from all sources."""
    try:
        logger.info("Fetching news from all sources")

        news_items = await news_fetcher_service.fetch_all_news(
            limit_per_source=limit_per_source
        )

        return news_items

    except Exception as e:
        logger.error(f"Error fetching all news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[NewsResponse])
async def list_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    source: Optional[NewsSource] = None,
    category: Optional[NewsCategory] = None,
    min_hot_score: float = Query(0.0, ge=0.0, le=100.0),
    db: AsyncSession = Depends(get_db)
):
    """List news items with filters."""
    try:
        query = select(NewsItem)

        if source:
            query = query.where(NewsItem.source == source)

        if category:
            query = query.where(NewsItem.category == category)

        if min_hot_score > 0:
            query = query.where(NewsItem.hot_score >= min_hot_score)

        query = query.order_by(NewsItem.hot_score.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        news_items = result.scalars().all()

        return news_items

    except Exception as e:
        logger.error(f"Error listing news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot", response_model=List[NewsResponse])
async def get_hot_news(
    limit: int = Query(10, ge=1, le=50, description="Number of hot news items"),
    db: AsyncSession = Depends(get_db)
):
    """Get hottest news items."""
    try:
        query = select(NewsItem).order_by(
            NewsItem.hot_score.desc(),
            NewsItem.created_at.desc()
        ).limit(limit)

        result = await db.execute(query)
        news_items = result.scalars().all()

        return news_items

    except Exception as e:
        logger.error(f"Error getting hot news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_item(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get news item by ID."""
    try:
        result = await db.execute(select(NewsItem).where(NewsItem.id == news_id))
        news_item = result.scalar_one_or_none()

        if not news_item:
            raise HTTPException(status_code=404, detail="News item not found")

        return news_item

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting news item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))