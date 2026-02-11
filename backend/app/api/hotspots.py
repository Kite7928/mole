"""
热门话题API路由
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel, Field
from ..core.database import get_db
from ..core.logger import logger
from ..services.hotspot_service import hotspot_service, HotspotSource

router = APIRouter()


class HotspotResponse(BaseModel):
    """热门话题响应模型"""
    rank: int
    title: str
    url: Optional[str]
    source: str
    category: Optional[str]
    heat: int
    created_at: str

    class Config:
        from_attributes = True


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