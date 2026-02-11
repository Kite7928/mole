"""
模板管理API路由
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel, Field
from ..core.database import get_db
from ..core.logger import logger
from ..services.template_service import template_service
from ..models.template import Template

router = APIRouter()


class TemplateResponse(BaseModel):
    """模板响应模型"""
    id: int
    name: str
    category: str
    description: Optional[str]
    preview_image: Optional[str]
    thumbnail: Optional[str]
    is_default: bool
    is_active: bool
    version: str
    sort_order: int
    usage_count: int
    like_count: int
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class CreateTemplateRequest(BaseModel):
    """创建模板请求"""
    name: str = Field(..., description="模板名称")
    category: str = Field(..., description="模板分类")
    html_content: str = Field(..., description="HTML内容")
    description: Optional[str] = Field(None, description="模板描述")
    css_content: Optional[str] = Field(None, description="CSS样式")
    is_default: bool = Field(False, description="是否为默认模板")


class UpdateTemplateRequest(BaseModel):
    """更新模板请求"""
    name: Optional[str] = Field(None, description="模板名称")
    category: Optional[str] = Field(None, description="模板分类")
    html_content: Optional[str] = Field(None, description="HTML内容")
    description: Optional[str] = Field(None, description="模板描述")
    css_content: Optional[str] = Field(None, description="CSS样式")
    is_default: Optional[bool] = Field(None, description="是否为默认模板")
    is_active: Optional[bool] = Field(None, description="是否启用")


@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    category: Optional[str] = Query(None, description="分类筛选"),
    is_active: Optional[bool] = Query(None, description="是否启用筛选"),
    skip: int = Query(0, description="跳过数量"),
    limit: int = Query(20, description="返回数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取模板列表

    Args:
        category: 分类筛选
        is_active: 是否启用筛选
        skip: 跳过数量
        limit: 返回数量
        db: 数据库会话

    Returns:
        模板列表
    """
    try:
        templates = await template_service.list_templates(
            db, category=category, is_active=is_active, skip=skip, limit=limit
        )
        return templates

    except Exception as e:
        logger.error(f"获取模板列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模板列表失败: {str(e)}")


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取模板详情

    Args:
        template_id: 模板ID
        db: 数据库会话

    Returns:
        模板详情
    """
    try:
        template = await template_service.get_template(db, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        return template

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模板详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模板详情失败: {str(e)}")


@router.post("/", response_model=TemplateResponse)
async def create_template(
    request: CreateTemplateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    创建模板

    Args:
        request: 创建模板请求
        db: 数据库会话

    Returns:
        创建的模板
    """
    try:
        template = await template_service.create_template(
            db,
            name=request.name,
            category=request.category,
            html_content=request.html_content,
            description=request.description,
            css_content=request.css_content,
            is_default=request.is_default
        )
        return template

    except Exception as e:
        logger.error(f"创建模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建模板失败: {str(e)}")


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    request: UpdateTemplateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    更新模板

    Args:
        template_id: 模板ID
        request: 更新模板请求
        db: 数据库会话

    Returns:
        更新后的模板
    """
    try:
        template = await template_service.update_template(
            db, template_id, **request.dict(exclude_none=True)
        )
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        return template

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新模板失败: {str(e)}")


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除模板

    Args:
        template_id: 模板ID
        db: 数据库会话

    Returns:
        删除结果
    """
    try:
        success = await template_service.delete_template(db, template_id)
        return {"success": success}

    except Exception as e:
        logger.error(f"删除模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除模板失败: {str(e)}")


@router.get("/categories/list")
async def get_categories():
    """获取所有分类"""
    try:
        categories = await template_service.get_categories()
        return categories

    except Exception as e:
        logger.error(f"获取分类失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取分类失败: {str(e)}")