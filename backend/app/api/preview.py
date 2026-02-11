"""
文章预览API路由
支持 Markdown 实时转换、模板预览、自定义样式
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from ..core.logger import logger
from ..services.markdown_converter import markdown_converter_service

router = APIRouter()


class ConvertRequest(BaseModel):
    """Markdown 转换请求"""
    markdown: str = Field(..., description="Markdown 内容")
    style: Optional[str] = Field(None, description="自定义样式（可选）")
    inline_css: bool = Field(True, description="是否内联 CSS")
    use_wechat_style: bool = Field(False, description="是否使用微信样式")


class ConvertResponse(BaseModel):
    """转换响应"""
    html: str
    word_count: int
    preview_url: Optional[str] = None


class ThemeRequest(BaseModel):
    """主题请求"""
    theme: str = Field(default="default", description="主题名称：default/blue/green/purple/dark")


class ThemeResponse(BaseModel):
    """主题响应"""
    style: str
    theme: str
    colors: Dict[str, str]


class ConvertWithThemeRequest(BaseModel):
    """带主题的转换请求"""
    markdown: str = Field(..., description="Markdown 内容")
    theme: str = Field(default="default", description="主题名称")


@router.post("/convert", response_model=ConvertResponse)
async def convert_markdown(request: ConvertRequest):
    """
    Markdown 转微信 HTML
    
    将 Markdown 文本转换为适合微信公众号发布的 HTML
    
    Args:
        request: 转换请求
    
    Returns:
        转换结果
    """
    try:
        logger.info(f"转换 Markdown，长度: {len(request.markdown)} 字符")
        
        # 转换 Markdown
        html = await markdown_converter_service.convert_to_html(
            request.markdown,
            style=request.style,
            inline_css=request.inline_css,
            use_wechat_style=request.use_wechat_style
        )
        
        # 计算字数
        word_count = len(request.markdown)
        
        logger.info(f"Markdown 转换完成，字数: {word_count}")
        
        return ConvertResponse(
            html=html,
            word_count=word_count
        )
        
    except Exception as e:
        logger.error(f"转换 Markdown 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")


@router.post("/convert/wechat", response_model=ConvertResponse)
async def convert_to_wechat_html(request: ConvertRequest):
    """
    Markdown 转微信 HTML（带官方样式）
    
    使用微信官方样式转换 Markdown
    
    Args:
        request: 转换请求
    
    Returns:
        转换结果
    """
    try:
        logger.info(f"转换 Markdown 为微信 HTML，长度: {len(request.markdown)} 字符")
        
        # 转换为微信 HTML
        html = await markdown_converter_service.convert_to_wechat_html(
            request.markdown,
            inline_css=request.inline_css
        )
        
        # 计算字数
        word_count = len(request.markdown)
        
        logger.info(f"微信 HTML 转换完成，字数: {word_count}")
        
        return ConvertResponse(
            html=html,
            word_count=word_count
        )
        
    except Exception as e:
        logger.error(f"转换微信 HTML 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")


@router.post("/convert/theme", response_model=ConvertResponse)
async def convert_with_theme(request: ConvertWithThemeRequest):
    """
    使用自定义主题转换 Markdown
    
    Args:
        request: 转换请求
    
    Returns:
        转换结果
    """
    try:
        logger.info(f"使用主题转换 Markdown: {request.theme}")
        
        # 使用主题转换
        html = await markdown_converter_service.convert_with_custom_theme(
            request.markdown,
            theme=request.theme
        )
        
        # 计算字数
        word_count = len(request.markdown)
        
        logger.info(f"主题转换完成，字数: {word_count}")
        
        return ConvertResponse(
            html=html,
            word_count=word_count
        )
        
    except Exception as e:
        logger.error(f"主题转换失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")


@router.get("/themes", response_model=list)
async def get_available_themes():
    """
    获取可用主题列表
    
    Returns:
        主题列表
    """
    try:
        themes = ["default", "blue", "green", "purple", "dark"]
        theme_descriptions = {
            "default": "默认主题（经典蓝）",
            "blue": "蓝色主题（清新）",
            "green": "绿色主题（活力）",
            "purple": "紫色主题（优雅）",
            "dark": "暗黑主题（护眼）"
        }
        
        result = []
        for theme in themes:
            result.append({
                "name": theme,
                "description": theme_descriptions.get(theme, ""),
                "colors": {}
            })
        
        logger.info(f"返回 {len(result)} 个可用主题")
        return result
        
    except Exception as e:
        logger.error(f"获取主题列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取主题列表失败: {str(e)}")


@router.post("/theme/generate", response_model=ThemeResponse)
async def generate_theme(request: ThemeRequest):
    """
    生成主题样式
    
    Args:
        request: 主题请求
    
    Returns:
        主题样式
    """
    try:
        logger.info(f"生成主题样式: {request.theme}")
        
        # 生成主题样式
        style = await markdown_converter_service.generate_custom_style(request.theme)
        
        # 提取颜色
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(style, 'html.parser')
        style_text = soup.get_text()
        
        # 简单的颜色提取
        colors = {
            "primary": "#576b95",
            "background": "#ffffff",
            "text": "#333333",
            "border": "#eeeeee"
        }
        
        logger.info(f"主题样式生成完成: {request.theme}")
        
        return ThemeResponse(
            style=style,
            theme=request.theme,
            colors=colors
        )
        
    except Exception as e:
        logger.error(f"生成主题样式失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成主题样式失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "preview"
    }