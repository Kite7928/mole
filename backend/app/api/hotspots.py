"""
热门话题API路由 - 增强版
支持趋势分析、热度历史、多维度筛选
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json

from ..core.database import get_db
from ..core.logger import logger
from ..services.hotspot_service import hotspot_service, HotspotSource
from ..models.hotspot import Hotspot, HotspotTrend

router = APIRouter()


class HotspotResponse(BaseModel):
    """热门话题响应模型"""
    id: Optional[int]
    rank: int
    title: str
    url: Optional[str]
    source: str
    category: Optional[str]
    heat: int
    heat_trend: Optional[float]
    view_count: Optional[int]
    discuss_count: Optional[int]
    summary: Optional[str]
    keywords: Optional[List[str]]
    tags: Optional[List[str]]
    is_processed: Optional[bool]
    created_at: str

    class Config:
        from_attributes = True


class HotspotTrendResponse(BaseModel):
    """热点趋势响应"""
    source: str
    hour: str
    total_hotspots: int
    avg_heat: float
    max_heat: int
    category_distribution: Dict[str, int]


class HotspotFilterRequest(BaseModel):
    """热点筛选请求"""
    sources: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    min_heat: Optional[int] = None
    max_heat: Optional[int] = None
    keyword: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    order_by: str = "heat"  # heat, created_at, rank
    order_desc: bool = True
    page: int = 1
    page_size: int = 20


@router.get("/", response_model=dict)
async def get_hotspots(
    limit: int = 20
):
    """
    获取热门话题列表

    Args:
        limit: 返回数量限制

    Returns:
        热门话题列表
    """
    try:
        logger.info(f"获取热门话题，数量限制: {limit}")
        
        # 获取热点数据
        hotspots = await hotspot_service.fetch_all_hotspots(count=limit)
        
        # 合并所有来源的热点
        all_hotspots = []
        for source, items in hotspots.items():
            for item in items:
                all_hotspots.append({
                    "rank": item.get("rank", 0),
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "source": source,
                    "category": item.get("category", ""),
                    "heat": item.get("heat", 0),
                    "created_at": item.get("created_at", "")
                })
        
        # 按热度排序
        all_hotspots.sort(key=lambda x: x["heat"], reverse=True)
        
        return {
            "items": all_hotspots[:limit],
            "total": len(all_hotspots),
            "limit": limit
        }

    except Exception as e:
        logger.error(f"获取热门话题失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热门话题失败: {str(e)}")


@router.get("/all", response_model=dict)
async def get_all_hotspots(
    sources: Optional[str] = None,
    count: int = 20
):
    """
    获取所有来源的热门话题

    Args:
        sources: 来源列表（逗号分隔，如：weibo,zhihu）
        count: 每个来源获取数量

    Returns:
        按来源分类的话题列表
    """
    try:
        source_list = None
        if sources:
            source_list = [HotspotSource(s.strip()) for s in sources.split(",")]

        hotspots = await hotspot_service.fetch_all_hotspots(source_list, count)
        return hotspots

    except Exception as e:
        logger.error(f"获取热门话题失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热门话题失败: {str(e)}")


@router.get("/merged", response_model=List[HotspotResponse])
async def get_merged_hotspots(
    sources: Optional[str] = None,
    count: int = 50
):
    """
    获取合并后的热门话题列表

    Args:
        sources: 来源列表（逗号分隔）
        count: 总数量

    Returns:
        合并后的话题列表
    """
    try:
        source_list = None
        if sources:
            source_list = [HotspotSource(s.strip()) for s in sources.split(",")]

        hotspots = await hotspot_service.get_merged_hotspots(source_list, count)
        return hotspots

    except Exception as e:
        logger.error(f"获取合并热门话题失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取合并热门话题失败: {str(e)}")


@router.post("/refresh", response_model=dict)
async def refresh_hotspots():
    """刷新热门话题"""
    try:
        hotspots = await hotspot_service.fetch_all_hotspots()
        return {
            "success": True,
            "message": "热门话题刷新成功",
            "data": hotspots
        }
    except Exception as e:
        logger.error(f"刷新热门话题失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"刷新热门话题失败: {str(e)}")


@router.get("/sources", response_model=dict)
async def get_hotspot_sources():
    """获取支持的热源列表"""
    try:
        from ..services.hotspot_service import HotspotSource, HotspotCategory

        sources = [
            {
                "value": source.value,
                "name": source.value.upper(),
                "description": {
                    "weibo": "微博热搜",
                    "zhihu": "知乎热榜",
                    "bilibili": "B站热门",
                    "douyin": "抖音热点",
                    "toutiao": "今日头条",
                    "kr36": "36氪",
                    "sspai": "少数派"
                }.get(source.value, source.value)
            }
            for source in HotspotSource
        ]

        categories = [
            {
                "value": category.value,
                "name": {
                    "tech": "科技",
                    "social": "社交",
                    "entertainment": "娱乐",
                    "knowledge": "知识",
                    "news": "新闻",
                    "business": "商业",
                    "life": "生活",
                    "education": "教育",
                    "finance": "财经",
                    "general": "综合"
                }.get(category.value, category.value)
            }
            for category in HotspotCategory
        ]

        return {
            "sources": sources,
            "categories": categories
        }
    except Exception as e:
        logger.error(f"获取热源列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热源列表失败: {str(e)}")


@router.post("/topic-suggestions", response_model=dict)
async def get_topic_suggestions(
    sources: Optional[str] = None,
    count: int = 10,
    suggestion_count: int = 5
):
    """
    基于热点生成 AI 选题建议

    Args:
        sources: 热点来源列表（逗号分隔）
        count: 每个来源获取的热点数量
        suggestion_count: 生成的选题建议数量

    Returns:
        选题建议列表
    """
    try:
        from ..services.hotspot_service import HotspotSource

        source_list = None
        if sources:
            source_list = [HotspotSource(s.strip()) for s in sources.split(",")]

        result = await hotspot_service.generate_topic_suggestions(
            sources=source_list,
            count=count,
            suggestion_count=suggestion_count
        )

        return result
    except Exception as e:
        logger.error(f"生成选题建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成选题建议失败: {str(e)}")


@router.post("/filter", response_model=dict)
async def filter_hotspots(
    request: HotspotFilterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    多维度筛选热点话题
    
    Args:
        request: 筛选条件
        db: 数据库会话
        
    Returns:
        筛选后的热点列表
    """
    try:
        query = select(Hotspot).where(Hotspot.is_active == True)
        
        # 来源筛选
        if request.sources:
            query = query.where(Hotspot.source.in_(request.sources))
        
        # 分类筛选
        if request.categories:
            query = query.where(Hotspot.category.in_(request.categories))
        
        # 热度范围筛选
        if request.min_heat is not None:
            query = query.where(Hotspot.heat >= request.min_heat)
        if request.max_heat is not None:
            query = query.where(Hotspot.heat <= request.max_heat)
        
        # 关键词搜索
        if request.keyword:
            keyword_filter = f"%{request.keyword}%"
            query = query.where(
                or_(
                    Hotspot.title.ilike(keyword_filter),
                    Hotspot.keywords.ilike(keyword_filter),
                    Hotspot.summary.ilike(keyword_filter)
                )
            )
        
        # 时间范围筛选
        if request.date_from:
            try:
                date_from = datetime.fromisoformat(request.date_from)
                query = query.where(Hotspot.created_at >= date_from)
            except:
                pass
        
        if request.date_to:
            try:
                date_to = datetime.fromisoformat(request.date_to)
                query = query.where(Hotspot.created_at <= date_to)
            except:
                pass
        
        # 排序
        order_column = getattr(Hotspot, request.order_by, Hotspot.heat)
        if request.order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(order_column)
        
        # 分页
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar()
        
        query = query.offset((request.page - 1) * request.page_size).limit(request.page_size)
        
        result = await db.execute(query)
        hotspots = result.scalars().all()
        
        return {
            "success": True,
            "total": total,
            "page": request.page,
            "page_size": request.page_size,
            "total_pages": (total + request.page_size - 1) // request.page_size,
            "items": [h.to_dict(include_history=False) for h in hotspots]
        }
        
    except Exception as e:
        logger.error(f"筛选热点失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"筛选热点失败: {str(e)}")


@router.get("/trends", response_model=dict)
async def get_hotspot_trends(
    source: str = Query(..., description="数据来源"),
    hours: int = Query(24, ge=1, le=168, description="查询小时数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取热点趋势统计
    
    Args:
        source: 数据来源
        hours: 查询最近多少小时
        db: 数据库会话
        
    Returns:
        趋势统计数据
    """
    try:
        # 计算时间范围
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # 查询趋势数据
        query = select(HotspotTrend).where(
            and_(
                HotspotTrend.source == source,
                HotspotTrend.hour >= start_time,
                HotspotTrend.hour <= end_time
            )
        ).order_by(HotspotTrend.hour)
        
        result = await db.execute(query)
        trends = result.scalars().all()
        
        # 如果没有趋势数据，从热点数据中实时计算
        if not trends:
            # 获取时间范围内的热点
            hotspots_query = select(Hotspot).where(
                and_(
                    Hotspot.source == source,
                    Hotspot.created_at >= start_time,
                    Hotspot.created_at <= end_time
                )
            )
            
            hotspots_result = await db.execute(hotspots_query)
            hotspots = hotspots_result.scalars().all()
            
            # 按小时聚合
            hourly_data = {}
            for h in hotspots:
                hour_key = h.created_at.replace(minute=0, second=0, microsecond=0)
                if hour_key not in hourly_data:
                    hourly_data[hour_key] = []
                hourly_data[hour_key].append(h)
            
            # 构建趋势数据
            trends = []
            for hour, hour_hotspots in sorted(hourly_data.items()):
                heats = [h.heat for h in hour_hotspots]
                trends.append({
                    "hour": hour.isoformat(),
                    "total_hotspots": len(hour_hotspots),
                    "avg_heat": sum(heats) / len(heats) if heats else 0,
                    "max_heat": max(heats) if heats else 0,
                    "min_heat": min(heats) if heats else 0
                })
        else:
            trends = [{
                "hour": t.hour.isoformat(),
                "total_hotspots": t.total_hotspots,
                "avg_heat": t.avg_heat,
                "max_heat": t.max_heat,
                "min_heat": t.min_heat,
                "category_distribution": json.loads(t.category_distribution) if t.category_distribution else {}
            } for t in trends]
        
        return {
            "success": True,
            "source": source,
            "hours": hours,
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"获取热点趋势失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热点趋势失败: {str(e)}")


@router.get("/{hotspot_id}/history", response_model=dict)
async def get_hotspot_history(
    hotspot_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个热点的热度历史
    
    Args:
        hotspot_id: 热点ID
        db: 数据库会话
        
    Returns:
        热度历史数据
    """
    try:
        query = select(Hotspot).where(Hotspot.id == hotspot_id)
        result = await db.execute(query)
        hotspot = result.scalar_one_or_none()
        
        if not hotspot:
            raise HTTPException(status_code=404, detail="热点不存在")
        
        history = []
        if hotspot.heat_history:
            try:
                history = json.loads(hotspot.heat_history)
            except:
                history = []
        
        return {
            "success": True,
            "hotspot": hotspot.to_dict(include_history=False),
            "history": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取热点历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热点历史失败: {str(e)}")


@router.get("/stats/overview", response_model=dict)
async def get_hotspot_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取热点统计概览
    
    Args:
        db: 数据库会话
        
    Returns:
        统计数据
    """
    try:
        # 总热点数
        total_query = select(func.count()).select_from(Hotspot)
        total_result = await db.execute(total_query)
        total = total_result.scalar()
        
        # 今日新增
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_query = select(func.count()).where(Hotspot.created_at >= today_start)
        today_result = await db.execute(today_query)
        today_count = today_result.scalar()
        
        # 来源分布
        source_query = select(
            Hotspot.source,
            func.count().label("count")
        ).group_by(Hotspot.source)
        source_result = await db.execute(source_query)
        source_distribution = {row[0]: row[1] for row in source_result.all()}
        
        # 分类分布
        category_query = select(
            Hotspot.category,
            func.count().label("count")
        ).where(Hotspot.category.isnot(None)).group_by(Hotspot.category)
        category_result = await db.execute(category_query)
        category_distribution = {row[0]: row[1] for row in category_result.all()}
        
        # 热度范围分布
        heat_ranges = {
            "<10万": 0,
            "10-50万": 0,
            "50-100万": 0,
            "100-500万": 0,
            ">500万": 0
        }
        
        all_hotspots_query = select(Hotspot.heat)
        all_hotspots_result = await db.execute(all_hotspots_query)
        heats = [h[0] for h in all_hotspots_result.all()]
        
        for heat in heats:
            if heat < 100000:
                heat_ranges["<10万"] += 1
            elif heat < 500000:
                heat_ranges["10-50万"] += 1
            elif heat < 1000000:
                heat_ranges["50-100万"] += 1
            elif heat < 5000000:
                heat_ranges["100-500万"] += 1
            else:
                heat_ranges[">500万"] += 1
        
        return {
            "success": True,
            "stats": {
                "total_hotspots": total,
                "today_new": today_count,
                "source_distribution": source_distribution,
                "category_distribution": category_distribution,
                "heat_distribution": heat_ranges
            }
        }
        
    except Exception as e:
        logger.error(f"获取热点统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热点统计失败: {str(e)}")


# 导入所需的函数
from sqlalchemy import or_