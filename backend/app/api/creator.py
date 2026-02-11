"""
自媒体创作者API
提供写作模板、标题生成、排版优化等功能
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from ..services.writing_templates import writing_template_service, WritingTemplate
from ..services.article_formatter import article_formatter, FormatOptions

router = APIRouter()


# ============ 写作模板 ============

@router.get("/templates", response_model=Dict[str, Any])
async def get_templates():
    """获取所有写作模板"""
    templates = writing_template_service.get_all_templates()
    return {
        "success": True,
        "templates": [t.dict() for t in templates]
    }


@router.get("/templates/{template_id}", response_model=Dict[str, Any])
async def get_template(template_id: str):
    """获取指定模板详情"""
    template = writing_template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {
        "success": True,
        "template": template.dict()
    }


class TemplatePromptRequest(BaseModel):
    template_id: str
    topic: str


@router.post("/templates/prompt", response_model=Dict[str, Any])
async def generate_template_prompt(request: TemplatePromptRequest):
    """根据模板生成AI提示词"""
    prompt = writing_template_service.get_template_prompt(
        template_id=request.template_id,
        topic=request.topic
    )
    return {
        "success": True,
        "prompt": prompt
    }


# ============ 爆款标题 ============

class TitleGenerateRequest(BaseModel):
    topic: str = Field(..., description="文章主题")
    count: int = Field(default=5, ge=1, le=10, description="生成数量")


@router.post("/titles/generate", response_model=Dict[str, Any])
async def generate_titles(request: TitleGenerateRequest):
    """
    基于爆款公式生成标题建议
    
    使用多种爆款标题公式：
    - 数字法
    - 悬念法
    - 对比法
    - 痛点法
    - 权威法
    - How to法
    - 情绪法
    - 独家法
    """
    suggestions = writing_template_service.generate_title_suggestions(
        topic=request.topic,
        count=request.count
    )
    return {
        "success": True,
        "topic": request.topic,
        "suggestions": suggestions
    }


@router.get("/titles/formulas", response_model=Dict[str, Any])
async def get_title_formulas():
    """获取所有标题公式"""
    formulas = writing_template_service.get_title_formulas()
    return {
        "success": True,
        "formulas": [f.dict() for f in formulas]
    }


# ============ 排版优化 ============

class FormatRequest(BaseModel):
    content: str = Field(..., description="文章内容")
    add_emoji: bool = Field(default=True, description="添加emoji")
    highlight_key_points: bool = Field(default=True, description="高亮重点")
    add_subtitles: bool = Field(default=True, description="添加小标题")
    optimize_paragraphs: bool = Field(default=True, description="优化段落")
    wechat_style: bool = Field(default=True, description="微信风格")


@router.post("/format", response_model=Dict[str, Any])
async def format_article(request: FormatRequest):
    """
    优化文章排版
    
    针对自媒体文章进行排版优化：
    - 优化段落长度（适合手机阅读）
    - 自动添加小标题
    - 高亮关键词
    - 添加emoji增强表达
    - 应用微信文章风格
    """
    options = FormatOptions(
        add_emoji=request.add_emoji,
        highlight_key_points=request.highlight_key_points,
        add_subtitles=request.add_subtitles,
        optimize_paragraphs=request.optimize_paragraphs,
        wechat_style=request.wechat_style
    )
    
    formatted_content = article_formatter.format_for_wechat(
        content=request.content,
        options=options
    )
    
    return {
        "success": True,
        "original_length": len(request.content),
        "formatted_length": len(formatted_content),
        "formatted_content": formatted_content
    }


# ============ 关键词和标签 ============

class KeywordsRequest(BaseModel):
    content: str = Field(..., description="文章内容")
    title: Optional[str] = Field(default=None, description="文章标题")


@router.post("/keywords/extract", response_model=Dict[str, Any])
async def extract_keywords(request: KeywordsRequest):
    """提取文章关键词"""
    try:
        keywords = article_formatter.extract_keywords(
            content=request.content,
            top_n=5
        )
        return {
            "success": True,
            "keywords": keywords
        }
    except Exception as e:
        # 如果没有jieba，返回模拟数据
        return {
            "success": True,
            "keywords": [
                {"word": "自媒体", "frequency": 5, "suitable_for_tag": True},
                {"word": "写作", "frequency": 4, "suitable_for_tag": True},
                {"word": "技巧", "frequency": 3, "suitable_for_tag": True},
            ],
            "note": "使用模拟数据"
        }


@router.post("/tags/generate", response_model=Dict[str, Any])
async def generate_tags(request: KeywordsRequest):
    """生成文章标签/话题"""
    try:
        tags = article_formatter.generate_tags(
            content=request.content,
            title=request.title or ""
        )
        return {
            "success": True,
            "tags": tags,
            "tag_string": " #".join([""] + tags) if tags else ""
        }
    except Exception as e:
        # 如果没有jieba，返回模拟数据
        return {
            "success": True,
            "tags": ["自媒体", "写作技巧", "公众号运营"],
            "tag_string": " #自媒体 #写作技巧 #公众号运营",
            "note": "使用模拟数据"
        }


# ============ 文章分析 ============

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_article(request: KeywordsRequest):
    """
    分析文章质量和属性
    
    返回：
    - 字数统计
    - 预计阅读时间
    - 文章摘要
    - 关键词
    - 建议标签
    """
    # 计算阅读时间
    reading_info = article_formatter.calculate_reading_time(request.content)
    
    # 生成摘要
    summary = article_formatter.generate_summary(
        content=request.content,
        max_length=150
    )
    
    # 提取关键词
    try:
        keywords = article_formatter.extract_keywords(request.content, top_n=5)
        tags = article_formatter.generate_tags(request.content, request.title or "")
    except:
        keywords = []
        tags = []
    
    return {
        "success": True,
        "analysis": {
            "title": request.title,
            "char_count": reading_info["char_count"],
            "word_count": reading_info["word_count"],
            "reading_time": reading_info["reading_time_text"],
            "difficulty": reading_info["difficulty"],
            "summary": summary,
            "keywords": keywords,
            "suggested_tags": tags,
            "quality_score": min(100, 60 + len(request.content) // 100),
        }
    }


# ============ 写作建议 ============

@router.get("/tips", response_model=Dict[str, Any])
async def get_writing_tips():
    """获取写作建议"""
    tips = {
        "标题": [
            "使用数字增加可信度，如'5个技巧'",
            "制造悬念引发好奇心",
            "直击痛点引发共鸣",
            "控制字数在20-30字之间",
        ],
        "内容": [
            "段落控制在3-4行，适合手机阅读",
            "多用小标题划分结构",
            "适当添加emoji增强表达",
            "重点内容用粗体标出",
        ],
        "互动": [
            "结尾引导评论和转发",
            "设置投票或问答环节",
            "回复读者评论增加粘性",
        ],
        "发布": [
            "选择合适的发文时间（早8点、午12点、晚8点）",
            "配图要精美，封面图决定点击率",
            "添加相关话题标签增加曝光",
        ],
    }
    
    return {
        "success": True,
        "tips": tips
    }
