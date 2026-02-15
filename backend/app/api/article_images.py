"""
文章配图 API 路由
支持批量生成封面图和段落配图
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from ..core.database import get_db
from ..core.logger import logger
from ..services.article_image_service import article_image_service
from ..services.prompt_templates import ImageStyle

router = APIRouter(tags=["文章配图"])


class GenerateImagesRequest(BaseModel):
    """批量生成配图请求"""
    style: str = Field(default="professional", description="图片风格")
    max_images: int = Field(default=5, ge=1, le=10, description="最多生成图片数")
    language: str = Field(default="zh", description="语言（zh/en）")
    auto_insert: bool = Field(default=True, description="是否自动插入到文章内容")


class RegenerateImageRequest(BaseModel):
    """重新生成单张图片请求"""
    position: str = Field(..., description="图片位置（cover/paragraph_1/paragraph_2...）")
    style: str = Field(default="professional", description="图片风格")
    language: str = Field(default="zh", description="语言")


class AnalyzeArticleRequest(BaseModel):
    """分析文章结构请求"""
    title: str = Field(..., description="文章标题")
    content: str = Field(..., description="文章内容")


class ImageGenerationResponse(BaseModel):
    """图片生成响应"""
    success: bool
    article_id: Optional[int] = None
    total: Optional[int] = None
    success_count: Optional[int] = None
    failed_count: Optional[int] = None
    images: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class StyleOption(BaseModel):
    """风格选项"""
    value: str
    label: str
    description: str
    icon: Optional[str] = None


@router.post("/generate-batch", response_model=ImageGenerationResponse)
async def generate_batch_images(
    article_id: int,
    request: GenerateImagesRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    为文章批量生成配图
    
    - 自动生成封面图
    - 为每个段落（H2标题）生成配图
    - 自动插入到文章内容中
    """
    try:
        logger.info(f"开始为文章 {article_id} 批量生成配图")
        
        result = await article_image_service.generate_article_images(
            db=db,
            article_id=article_id,
            style=request.style,
            max_images=request.max_images,
            language=request.language,
            auto_insert=request.auto_insert
        )
        
        return result
        
    except Exception as e:
        logger.error(f"批量生成配图失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成配图失败: {str(e)}")


@router.post("/regenerate", response_model=ImageGenerationResponse)
async def regenerate_single_image(
    article_id: int,
    request: RegenerateImageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    重新生成单张图片
    
    - 支持重新生成封面图（position=cover）
    - 支持重新生成段落配图（position=paragraph_1/paragraph_2...）
    """
    try:
        logger.info(f"重新生成文章 {article_id} 的 {request.position} 图片")
        
        result = await article_image_service.regenerate_single_image(
            db=db,
            article_id=article_id,
            position=request.position,
            style=request.style,
            language=request.language
        )
        
        return {
            "success": result.get("success", False),
            "article_id": article_id,
            "images": [result] if result.get("success") else [],
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"重新生成图片失败: {e}")
        raise HTTPException(status_code=500, detail=f"重新生成图片失败: {str(e)}")


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_article_structure(
    article_id: int,
    request: AnalyzeArticleRequest
):
    """
    分析文章结构，建议配图位置
    
    - 分析文章段落结构
    - 建议配图位置
    - 预览生成的 prompts
    """
    try:
        logger.info(f"分析文章 {article_id} 结构")
        
        result = await article_image_service.analyze_article_structure(
            article_id=article_id,
            content=request.content,
            title=request.title
        )
        
        return result
        
    except Exception as e:
        logger.error(f"分析文章结构失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/styles", response_model=List[StyleOption])
async def get_image_styles():
    """
    获取所有可用的图片风格选项
    
    返回支持的所有风格列表，供前端选择
    """
    styles = [
        StyleOption(
            value="professional",
            label="专业商务",
            description="简洁大气，适合职场和商业场景",
            icon="💼"
        ),
        StyleOption(
            value="creative",
            label="创意艺术",
            description="色彩丰富，充满想象力",
            icon="🎨"
        ),
        StyleOption(
            value="minimal",
            label="极简风格",
            description="留白充足，突出主题",
            icon="⬜"
        ),
        StyleOption(
            value="vibrant",
            label="鲜艳活力",
            description="色彩明快，充满能量",
            icon="🌈"
        ),
        StyleOption(
            value="tech",
            label="科技感",
            description="未来主义，数字化元素",
            icon="🔬"
        ),
        StyleOption(
            value="nature",
            label="自然生态",
            description="清新自然，绿色环保",
            icon="🌿"
        ),
        StyleOption(
            value="chinese",
            label="中国风",
            description="水墨画风格，传统文化",
            icon="🎋"
        ),
        StyleOption(
            value="cartoon",
            label="卡通插画",
            description="可爱生动，适合轻松话题",
            icon="🎭"
        ),
        StyleOption(
            value="realistic",
            label="写实摄影",
            description="真实自然，高清晰度",
            icon="📷"
        )
    ]
    
    return styles


@router.get("/preview-prompts")
async def preview_prompts(
    article_id: int,
    title: str,
    content: str,
    style: str = "professional",
    max_images: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    预览将要生成的 prompts（不实际生成图片）
    
    用于让用户确认 prompts 是否符合预期
    """
    try:
        from ..services.prompt_templates import analyze_and_build_prompts
        
        prompts = analyze_and_build_prompts(
            title=title,
            content=content,
            style=style,
            max_images=max_images,
            language="zh"
        )
        
        return {
            "success": True,
            "article_id": article_id,
            "style": style,
            "total": len(prompts),
            "prompts": [
                {
                    "position": p.get("suggested_position"),
                    "type": "cover" if p.get("position") == "cover" else "paragraph",
                    "style": p.get("style"),
                    "prompt": p.get("prompt"),
                    "style_description": p.get("style_description")
                }
                for p in prompts
            ]
        }
        
    except Exception as e:
        logger.error(f"预览 prompts 失败: {e}")
        raise HTTPException(status_code=500, detail=f"预览失败: {str(e)}")
