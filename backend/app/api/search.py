"""
全文搜索API路由
基于SQLite FTS5实现
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel, Field

from ..core.database import get_db
from ..core.logger import logger
from ..services.search_service import search_service

router = APIRouter()


class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., min_length=1, max_length=200, description="搜索关键词")
    status: Optional[str] = Field(None, description="文章状态筛选")
    date_from: Optional[str] = Field(None, description="开始日期 (ISO格式)")
    date_to: Optional[str] = Field(None, description="结束日期 (ISO格式)")
    limit: int = Field(20, ge=1, le=100, description="返回数量")
    offset: int = Field(0, ge=0, description="偏移量")


class SearchResponse(BaseModel):
    """搜索响应"""
    success: bool
    total: int
    limit: int
    offset: int
    query: str
    articles: List[dict]


@router.post("/", response_model=SearchResponse)
async def search_articles(request: SearchRequest):
    """
    全文搜索文章
    
    支持标题、内容、标签的全文检索
    使用SQLite FTS5实现
    """
    try:
        filters = {}
        if request.status:
            filters['status'] = request.status
        if request.date_from:
            filters['date_from'] = request.date_from
        if request.date_to:
            filters['date_to'] = request.date_to
        
        result = await search_service.search(
            query=request.query,
            filters=filters if filters else None,
            limit=request.limit,
            offset=request.offset
        )
        
        return SearchResponse(**result)
        
    except Exception as e:
        logger.error(f"搜索API错误: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/", response_model=SearchResponse)
async def search_articles_get(
    q: str = Query(..., min_length=1, max_length=200, description="搜索关键词"),
    status: Optional[str] = Query(None, description="文章状态筛选"),
    date_from: Optional[str] = Query(None, description="开始日期"),
    date_to: Optional[str] = Query(None, description="结束日期"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    全文搜索文章 (GET方式)
    
    支持标题、内容、标签的全文检索
    """
    try:
        filters = {}
        if status:
            filters['status'] = status
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to
        
        result = await search_service.search(
            query=q,
            filters=filters if filters else None,
            limit=limit,
            offset=offset
        )
        
        return SearchResponse(**result)
        
    except Exception as e:
        logger.error(f"搜索API错误: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/suggestions", response_model=dict)
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=50, description="输入的查询"),
    limit: int = Query(10, ge=1, le=20)
):
    """
    获取搜索建议
    
    用于搜索框的自动补全
    """
    try:
        suggestions = await search_service.get_suggestions(q, limit)
        
        return {
            "success": True,
            "query": q,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"获取搜索建议失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取建议失败: {str(e)}")


@router.get("/popular-keywords", response_model=dict)
async def get_popular_keywords(
    limit: int = Query(20, ge=1, le=50)
):
    """
    获取热门搜索关键词
    
    基于文章标签统计
    """
    try:
        keywords = await search_service.get_popular_keywords(limit)
        
        return {
            "success": True,
            "keywords": keywords
        }
        
    except Exception as e:
        logger.error(f"获取热门关键词失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取热门关键词失败: {str(e)}")


@router.post("/rebuild-index", response_model=dict)
async def rebuild_search_index():
    """
    重建全文搜索索引
    
    用于初始化或数据修复
    """
    try:
        await search_service.rebuild_index()
        
        return {
            "success": True,
            "message": "全文搜索索引重建完成"
        }
        
    except Exception as e:
        logger.error(f"重建索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"重建索引失败: {str(e)}")
