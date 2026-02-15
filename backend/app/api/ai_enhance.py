"""
AI增强功能API
提供标题A/B测试、SEO优化建议、文章续写扩写、多版本生成等功能
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..core.database import get_db
from ..core.logger import logger
from ..services.unified_ai_service import unified_ai_service
from ..models.article import Article, ArticleStatus

router = APIRouter()


class TitleVariant(BaseModel):
    """标题变体"""
    title: str
    score: int = Field(..., ge=0, le=100)
    reason: str
    style: str  # 标题风格类型


class TitleABTestRequest(BaseModel):
    """标题A/B测试请求"""
    content: str  # 文章内容
    topic: Optional[str] = None  # 文章主题
    current_title: Optional[str] = None  # 当前标题（可选）
    count: int = Field(default=5, ge=3, le=10)  # 生成标题数量
    style_preferences: List[str] = []  # 偏好风格


class TitleABTestResponse(BaseModel):
    """标题A/B测试响应"""
    variants: List[TitleVariant]
    analysis: str  # 整体分析建议
    best_for_click: TitleVariant  # 最适合点击的标题
    best_for_seo: TitleVariant  # 最适合SEO的标题


class SEOAnalysisResult(BaseModel):
    """SEO分析结果"""
    score: int = Field(..., ge=0, le=100)
    title_analysis: Dict[str, Any]
    keyword_analysis: Dict[str, Any]
    content_analysis: Dict[str, Any]
    suggestions: List[Dict[str, Any]]
    improved_version: Optional[str] = None


class ContinueWriteRequest(BaseModel):
    """续写请求"""
    content: str  # 现有内容
    direction: Optional[str] = None  # 续写方向提示
    target_length: int = Field(default=500, ge=100, le=2000)  # 目标字数
    style: str = "match"  # match: 匹配原文风格, creative: 创意风格


class ContentVersion(BaseModel):
    """内容版本"""
    version_type: str  # formal, casual, concise, detailed, creative
    title: str
    content: str
    description: str  # 版本特点说明


class MultiVersionRequest(BaseModel):
    """多版本生成请求"""
    content: str
    topic: str
    versions: List[str] = ["formal", "casual", "concise"]  # 需要生成的版本类型


class MultiVersionResponse(BaseModel):
    """多版本生成响应"""
    original: str
    versions: List[ContentVersion]
    comparison: Dict[str, Any]


@router.post("/title-ab-test", response_model=TitleABTestResponse)
async def title_ab_test(
    request: TitleABTestRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    标题A/B测试
    生成多个标题变体，提供评分和分析
    """
    try:
        # 构建提示词
        style_hints = ""
        if request.style_preferences:
            style_hints = f"偏好风格：{', '.join(request.style_preferences)}"
        
        topic_hint = f"主题为：{request.topic}" if request.topic else ""
        
        prompt = f"""请为以下文章内容生成{request.count}个不同风格的标题变体。

文章内容：
{request.content[:1000]}...

{topic_hint}
{style_hints}

要求：
1. 每个标题需要有不同的风格和侧重点
2. 评估每个标题的点击吸引力（1-100分）
3. 评估每个标题的SEO友好度（1-100分）
4. 提供选择该标题的理由
5. 标注标题风格类型（如：悬念型、数据型、提问型、情感型、实用型等）

请按以下格式返回：
标题1：[标题内容]
吸引力评分：[分数]
SEO评分：[分数]
风格类型：[类型]
推荐理由：[理由]

最后提供整体分析：
- 最适合点击的标题及原因
- 最适合SEO的标题及原因
- 综合建议
"""

        # 调用AI生成
        messages = [{"role": "user", "content": prompt}]
        response = await unified_ai_service.generate(messages, temperature=0.8)
        
        # 解析AI响应
        ai_content = response.content
        
        # 解析标题变体
        variants = []
        lines = ai_content.split('\n')
        current_variant = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('标题') and '：' in line:
                if current_variant and 'title' in current_variant:
                    variants.append(TitleVariant(**current_variant))
                current_variant = {'title': line.split('：', 1)[1].strip()}
            elif '吸引力评分' in line or '点击' in line:
                try:
                    score = int(line.split('：')[1].split('/')[0].strip())
                    current_variant['score'] = score
                except:
                    current_variant['score'] = 70
            elif '风格类型' in line:
                current_variant['style'] = line.split('：')[1].strip()
            elif '推荐理由' in line:
                current_variant['reason'] = line.split('：')[1].strip()
        
        # 添加最后一个变体
        if current_variant and 'title' in current_variant:
            variants.append(TitleVariant(**current_variant))
        
        # 如果解析失败，生成默认变体
        if len(variants) < 3:
            variants = generate_default_variants(request.content, request.topic)
        
        # 找出最适合点击和SEO的标题
        best_for_click = max(variants, key=lambda x: x.score)
        best_for_seo = sorted(variants, key=lambda x: len(x.title), reverse=True)[0]  # 简单启发式：较长的通常SEO更好
        
        # 提取分析建议
        analysis = "建议根据目标受众和发布平台选择合适的标题。悬念型标题适合社交媒体传播，数据型标题适合专业领域，提问型标题能提高互动率。"
        if '整体分析' in ai_content:
            analysis_start = ai_content.find('整体分析')
            analysis = ai_content[analysis_start:analysis_start+500]
        
        return TitleABTestResponse(
            variants=variants[:request.count],
            analysis=analysis,
            best_for_click=best_for_click,
            best_for_seo=best_for_seo
        )
        
    except Exception as e:
        logger.error(f"标题A/B测试失败: {str(e)}")
        # 返回默认变体
        variants = generate_default_variants(request.content, request.topic)
        return TitleABTestResponse(
            variants=variants,
            analysis="建议使用A/B测试来验证不同标题的效果",
            best_for_click=variants[0],
            best_for_seo=variants[1]
        )


def generate_default_variants(content: str, topic: Optional[str]) -> List[TitleVariant]:
    """生成默认标题变体"""
    base_topic = topic or content[:20] if content else "文章"
    return [
        TitleVariant(
            title=f"深度解析：{base_topic}的核心要点",
            score=85,
            reason="专业权威，适合知识型读者",
            style="专业型"
        ),
        TitleVariant(
            title=f"{base_topic}，你不知道的5个秘密",
            score=92,
            reason="悬念感强，点击率高",
            style="悬念型"
        ),
        TitleVariant(
            title=f"为什么{base_topic}如此重要？",
            score=78,
            reason="提问式标题，引发思考",
            style="提问型"
        ),
        TitleVariant(
            title=f"从入门到精通：{base_topic}完全指南",
            score=88,
            reason="实用性强，搜索量高",
            style="实用型"
        ),
        TitleVariant(
            title=f"{base_topic}实战分享：我的成功经验",
            score=82,
            reason="个人经历，真实可信",
            style="经验型"
        )
    ]


@router.post("/seo-analysis", response_model=SEOAnalysisResult)
async def seo_analysis(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    SEO优化分析
    分析文章的SEO表现并提供优化建议
    """
    try:
        # 获取文章
        result = await db.execute(select(Article).where(Article.id == article_id))
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        # 构建分析提示词
        prompt = f"""请对以下文章进行SEO优化分析：

标题：{article.title}
内容摘要：{article.content[:1500]}...

请从以下维度分析：
1. 标题优化（长度、关键词、吸引力）
2. 关键词分析（密度、分布、相关词建议）
3. 内容结构（段落、小标题、可读性）
4. 元描述建议
5. 改进建议列表

请按JSON格式返回：
{{
    "score": 总分(0-100),
    "title_analysis": {{
        "length_ok": true/false,
        "has_keywords": true/false,
        "attractiveness": "高/中/低",
        "suggestions": ["建议1", "建议2"]
    }},
    "keyword_analysis": {{
        "main_keywords": ["关键词1", "关键词2"],
        "density": "合适/过高/过低",
        "suggestions": ["建议1"]
    }},
    "content_analysis": {{
        "structure_score": 分数,
        "readability": "易读/中等/难读",
        "suggestions": ["建议1"]
    }},
    "suggestions": [
        {{"type": "标题", "content": "具体建议", "priority": "高/中/低"}},
        {{"type": "内容", "content": "具体建议", "priority": "高/中/低"}}
    ],
    "improved_title": "优化后的标题建议",
    "improved_description": "优化后的描述建议"
}}
"""

        messages = [{"role": "user", "content": prompt}]
        response = await unified_ai_service.generate(messages, temperature=0.3)
        
        # 尝试解析JSON响应
        try:
            import json
            ai_result = json.loads(response.content)
            
            return SEOAnalysisResult(
                score=ai_result.get("score", 70),
                title_analysis=ai_result.get("title_analysis", {}),
                keyword_analysis=ai_result.get("keyword_analysis", {}),
                content_analysis=ai_result.get("content_analysis", {}),
                suggestions=ai_result.get("suggestions", []),
                improved_version=ai_result.get("improved_title")
            )
        except:
            # 解析失败返回默认分析
            return generate_default_seo_analysis(article)
            
    except Exception as e:
        logger.error(f"SEO分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


def generate_default_seo_analysis(article: Article) -> SEOAnalysisResult:
    """生成默认SEO分析"""
    title_len = len(article.title) if article.title else 0
    content_len = len(article.content) if article.content else 0
    
    suggestions = []
    if title_len < 10:
        suggestions.append({"type": "标题", "content": "标题过短，建议增加到15-30字", "priority": "高"})
    elif title_len > 50:
        suggestions.append({"type": "标题", "content": "标题过长，建议控制在30字以内", "priority": "中"})
    
    if content_len < 500:
        suggestions.append({"type": "内容", "content": "内容较短，建议增加到800字以上以获得更好SEO效果", "priority": "高"})
    
    return SEOAnalysisResult(
        score=75,
        title_analysis={
            "length_ok": 10 <= title_len <= 50,
            "has_keywords": True,
            "attractiveness": "中",
            "suggestions": ["标题可适当增加关键词密度"]
        },
        keyword_analysis={
            "main_keywords": [article.source_topic or "未识别"],
            "density": "适中",
            "suggestions": ["建议添加更多相关关键词"]
        },
        content_analysis={
            "structure_score": 70,
            "readability": "中等",
            "suggestions": ["可增加小标题提升可读性"]
        },
        suggestions=suggestions,
        improved_version=None
    )


@router.post("/continue-write")
async def continue_write(request: ContinueWriteRequest):
    """
    文章续写/扩写
    根据现有内容智能续写
    """
    try:
        style_hint = "保持与原文相同的写作风格" if request.style == "match" else "采用更有创意的写作风格"
        direction_hint = f"续写方向：{request.direction}" if request.direction else "请自然延续上文内容"
        
        prompt = f"""请根据以下内容进行续写：

原文：
{request.content[-1000:]}  # 取最后1000字作为上下文

要求：
1. {style_hint}
2. {direction_hint}
3. 续写长度约{request.target_length}字
4. 保持段落连贯，逻辑清晰
5. 与原文自然衔接

请直接输出续写内容，不需要额外说明。
"""

        messages = [{"role": "user", "content": prompt}]
        response = await unified_ai_service.generate(
            messages,
            temperature=0.7,
            max_tokens=request.target_length * 2
        )
        
        return {
            "original_length": len(request.content),
            "continued_content": response.content.strip(),
            "continued_length": len(response.content),
            "style": request.style
        }
        
    except Exception as e:
        logger.error(f"续写失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"续写失败: {str(e)}")


@router.post("/multi-version", response_model=MultiVersionResponse)
async def generate_multi_versions(request: MultiVersionRequest):
    """
    多版本内容生成
    生成正式版、通俗版、精简版等不同版本
    """
    try:
        version_prompts = {
            "formal": "正式专业版：使用专业术语，结构严谨，适合行业报告",
            "casual": "轻松通俗版：语言轻松，通俗易懂，适合大众阅读",
            "concise": "精简版：保留核心要点，精简表达，适合快速阅读",
            "detailed": "详细版：增加细节和案例，深度解析",
            "creative": "创意版：独特视角，新颖表达，适合社交媒体传播"
        }
        
        versions = []
        
        for version_type in request.versions:
            if version_type not in version_prompts:
                continue
                
            prompt = f"""请将以下内容改写为"{version_prompts[version_type]}"：

主题：{request.topic}
原文：{request.content[:800]}...

要求：
1. 保持核心信息不变
2. 根据版本特点调整表达方式
3. 为该版本起一个合适的标题

请按以下格式返回：
标题：[版本标题]
内容：[改写后的内容]
特点说明：[该版本的特点和适用场景]
"""

            messages = [{"role": "user", "content": prompt}]
            response = await unified_ai_service.generate(messages, temperature=0.7)
            
            # 解析响应
            content = response.content
            title = ""
            body = ""
            desc = ""
            
            for line in content.split('\n'):
                if line.startswith('标题：'):
                    title = line[3:].strip()
                elif line.startswith('内容：'):
                    body = line[3:].strip()
                elif line.startswith('特点说明：'):
                    desc = line[5:].strip()
            
            # 如果没有正确解析，使用默认格式
            if not body:
                body = content
                title = f"{request.topic} - {version_type}"
                desc = version_prompts.get(version_type, "")
            
            versions.append(ContentVersion(
                version_type=version_type,
                title=title or f"{request.topic}({version_type})",
                content=body,
                description=desc or version_prompts.get(version_type, "")
            ))
        
        # 生成版本对比
        comparison = {
            "lengths": {v.version_type: len(v.content) for v in versions},
            "best_for": {
                "formal": "专业读者、行业报告",
                "casual": "大众读者、社交媒体",
                "concise": "快速阅读、信息获取",
                "detailed": "深度阅读、学习研究",
                "creative": "社交媒体、病毒传播"
            }
        }
        
        return MultiVersionResponse(
            original=request.content,
            versions=versions,
            comparison=comparison
        )
        
    except Exception as e:
        logger.error(f"多版本生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.get("/tools")
async def get_ai_tools():
    """获取可用的AI增强工具列表"""
    return {
        "tools": [
            {
                "id": "title_ab_test",
                "name": "标题A/B测试",
                "description": "生成多个标题变体并提供评分分析",
                "icon": "split",
                "endpoint": "/api/ai-enhance/title-ab-test"
            },
            {
                "id": "seo_analysis",
                "name": "SEO优化分析",
                "description": "分析文章SEO表现并提供优化建议",
                "icon": "search",
                "endpoint": "/api/ai-enhance/seo-analysis"
            },
            {
                "id": "continue_write",
                "name": "智能续写",
                "description": "根据现有内容智能续写文章",
                "icon": "edit",
                "endpoint": "/api/ai-enhance/continue-write"
            },
            {
                "id": "multi_version",
                "name": "多版本生成",
                "description": "生成正式版、通俗版、精简版等多个版本",
                "icon": "copy",
                "endpoint": "/api/ai-enhance/multi-version"
            }
        ]
    }
