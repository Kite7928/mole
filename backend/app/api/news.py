"""
热点新闻API路由 - 简化版
支持获取热点新闻和刷新热点
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..services.news_fetcher import news_fetcher_service
from ..models.news import NewsSource, NewsItem
from ..core.database import get_db
from ..core.logger import logger

router = APIRouter()


class NewsResponse(BaseModel):
    """新闻响应模型"""
    id: int
    title: str
    summary: str | None
    url: str
    source: str
    source_name: str
    hot_score: float
    published_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class RefreshRequest(BaseModel):
    """刷新请求模型"""
    source: str = Field(default="ithome", description="新闻源：ithome 或 baidu")
    limit: int = Field(default=20, ge=1, le=50, description="获取数量")


@router.get("/", response_model=dict)
async def get_news(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    获取新闻列表

    Args:
        limit: 返回数量限制
        db: 数据库会话

    Returns:
        包含新闻列表和元数据的字典
    """
    try:
        logger.info(f"获取新闻列表，数量限制: {limit}")

        # 查询数据库中的新闻
        query = select(NewsItem).order_by(NewsItem.hot_score.desc()).limit(limit)
        result = await db.execute(query)
        news_items = result.scalars().all()

        return {
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "summary": item.summary,
                    "url": item.url,
                    "source": item.source,
                    "source_name": item.source_name,
                    "hot_score": item.hot_score,
                    "published_at": item.published_at.isoformat() if item.published_at else None,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                }
                for item in news_items
            ],
            "total": len(news_items),
            "limit": limit
        }

    except Exception as e:
        logger.error(f"获取新闻列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取新闻列表失败: {str(e)}")


@router.get("/hotspots", response_model=dict)
async def get_hotspots(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    获取热点新闻列表

    Args:
        limit: 返回数量限制
        db: 数据库会话

    Returns:
        包含新闻列表和元数据的字典
    """
    try:
        logger.info(f"获取热点新闻，数量限制: {limit}")

        # 从IT之家获取新闻
        fetched_items = await news_fetcher_service.fetch_news(
            source=NewsSource.ITHOME,
            limit=limit
        )

        # 保存到数据库（去重）
        news_items = []
        for item in fetched_items:
            # 检查是否已存在
            existing = await db.execute(
                select(NewsItem).where(NewsItem.url == item.url)
            )
            existing_item = existing.scalar_one_or_none()
            
            if not existing_item:
                db.add(item)
                await db.commit()
                await db.refresh(item)
                news_items.append(item)
            else:
                # 如果已存在，使用现有记录
                news_items.append(existing_item)

        # 转换为响应模型
        news_responses = []
        for item in news_items:
            news_responses.append(NewsResponse(
                id=item.id,
                title=item.title,
                summary=item.summary,
                url=item.url,
                source=item.source.value,
                source_name=item.source_name,
                hot_score=item.hot_score,
                published_at=item.published_at,
                created_at=item.created_at
            ))

        return {
            "success": True,
            "count": len(news_responses),
            "news_items": news_responses
        }

    except Exception as e:
        logger.error(f"获取热点新闻失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"获取热点新闻失败: {str(e)}")


@router.post("/refresh", response_model=dict)
async def refresh_news(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新热点新闻

    Args:
        request: 刷新请求参数
        db: 数据库会话

    Returns:
        刷新结果
    """
    try:
        logger.info(f"刷新热点新闻，源: {request.source}, 数量: {request.limit}")

        # 解析新闻源
        source_map = {
            "ithome": NewsSource.ITHOME,
            "baidu": NewsSource.BAIDU
        }

        source = source_map.get(request.source, NewsSource.ITHOME)

        # 获取新闻
        fetched_items = await news_fetcher_service.fetch_news(
            source=source,
            limit=request.limit
        )

        # 保存到数据库（去重）
        saved_items = []
        for item in fetched_items:
            # 检查是否已存在
            existing = await db.execute(
                select(NewsItem).where(NewsItem.url == item.url)
            )
            existing_item = existing.scalar_one_or_none()
            
            if not existing_item:
                db.add(item)
                await db.commit()
                await db.refresh(item)
                saved_items.append(item)
            else:
                # 如果已存在，使用现有记录
                saved_items.append(existing_item)

        return {
            "success": True,
            "message": f"成功获取 {len(saved_items)} 条新闻",
            "count": len(saved_items),
            "source": request.source,
            "new_items": len([item for item in saved_items if item.created_at > (datetime.now() - timedelta(minutes=5))])
        }

    except Exception as e:
        logger.error(f"刷新热点新闻失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"刷新失败: {str(e)}")