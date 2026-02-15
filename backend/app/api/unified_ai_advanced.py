"""
AI写作进阶API路由 - 分步写作流程
支持大纲生成、段落扩写、文章润色、敏感词检测
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import httpx
import re
from ..core.database import get_db
from ..core.config import settings
from ..core.logger import logger
from ..services.sensitive_words import check_sensitive_words, filter_sensitive_words
from ..services.writing_templates import writing_template_service

router = APIRouter()


async def get_config_from_db(db: AsyncSession):
    """从数据库获取配置"""
    from ..models.config import AppConfig
    from sqlalchemy import select
    
    query = select(AppConfig).order_by(AppConfig.id.desc())
    result = await db.execute(query)
    config = result.scalar_one_or_none()
    
    if not config or not config.api_key:
        raise HTTPException(status_code=400, detail="请先在系统设置中配置AI API Key")
    
    # 补充默认配置值
    provider = config.ai_provider or "deepseek"
    if provider == "deepseek":
        config.base_url = config.base_url or "https://api.deepseek.com/v1"
        config.model = config.model or "deepseek-chat"
    elif provider == "openai":
        config.base_url = config.base_url or "https://api.openai.com/v1"
        config.model = config.model or "gpt-4-turbo-preview"
    
    return config


# ========== 请求/响应模型 ==========

class GenerateOutlineRequest(BaseModel):
    """生成大纲请求"""
    topic: str = Field(..., description="文章主题")
    target_audience: str = Field(default="普通读者", description="目标读者")
    article_type: str = Field(default="分析类", description="文章类型：分析类/教程类/观点类/故事类/清单类")
    template_id: Optional[str] = Field(None, description="使用模板ID")
    model: Optional[str] = Field(None, description="使用的模型")


class OutlineSection(BaseModel):
    """大纲段落"""
    title: str
    content: str
    word_count: int


class GenerateOutlineResponse(BaseModel):
    """生成大纲响应"""
    titles: List[Dict[str, Any]]  # 标题选项
    outline: List[OutlineSection]  # 大纲结构
    total_word_count: int  # 总字数
    estimated_time: str  # 预计阅读时间


class ExpandSectionRequest(BaseModel):
    """扩写段落请求"""
    outline_point: str = Field(..., description="大纲要点")
    context: str = Field(default="", description="上下文")
    style: str = Field(default="professional", description="写作风格")
    word_count: int = Field(default=500, description="目标字数")
    model: Optional[str] = Field(None, description="使用的模型")


class ExpandSectionResponse(BaseModel):
    """扩写段落响应"""
    content: str
    word_count: int
    keywords: List[str]


class PolishArticleRequest(BaseModel):
    """润色文章请求"""
    content: str = Field(..., description="文章内容")
    polish_type: str = Field(default="overall", description="润色类型：overall(整体)/clarity(清晰度)/readability(可读性)/engagement(吸引力)")
    model: Optional[str] = Field(None, description="使用的模型")


class PolishArticleResponse(BaseModel):
    """润色文章响应"""
    polished_content: str
    changes_summary: List[str]  # 修改摘要
    quality_score: float


class CheckSensitiveRequest(BaseModel):
    """检测敏感词请求"""
    content: str = Field(..., description="文章内容")


class SensitiveWordMatch(BaseModel):
    """敏感词匹配"""
    word: str
    replacement: str
    position: int  # 位置
    context: str  # 上下文


class CheckSensitiveResponse(BaseModel):
    """检测敏感词响应"""
    has_sensitive: bool
    matches: List[SensitiveWordMatch]
    filtered_content: str
    total_count: int


# ========== API 端点 ==========

@router.post("/generate-outline", response_model=GenerateOutlineResponse)
async def generate_outline(request: GenerateOutlineRequest, db: AsyncSession = Depends(get_db)):
    """
    生成文章大纲
    
    根据主题、目标读者和文章类型，生成文章标题和大纲结构
    
    Args:
        request: 生成大纲请求
        db: 数据库会话
    
    Returns:
        大纲响应
    """
    try:
        config = await get_config_from_db(db)
        model = request.model or config.model or "deepseek-chat"
        base_url = config.base_url or "https://api.deepseek.com/v1"
        
        logger.info(f"生成大纲，主题: {request.topic}, 类型: {request.article_type}")
        
        # 使用模板生成提示词
        if request.template_id and request.template_id in writing_template_service.TEMPLATES:
            prompt = writing_template_service.get_template_prompt(request.template_id, request.topic)
        else:
            prompt = f"""你是一位专业的文章结构策划师。请根据以下信息生成文章大纲。

主题：{request.topic}
目标读者：{request.target_audience}
文章类型：{request.article_type}

要求：
1. 生成3-5个吸引人的标题选项
2. 设计清晰的文章结构（引言、主体、结论）
3. 主体部分包含2-4个小节
4. 每个部分列出核心要点
5. 标注每部分的预计字数
6. 确保逻辑连贯、层层递进

请以JSON格式返回，格式如下：
{{
  "titles": [{{"title": "标题1", "score": 85}}, {{"title": "标题2", "score": 80}}],
  "outline": [
    {{"title": "引言", "content": "要点说明", "word_count": 200}},
    {{"title": "第一部分", "content": "要点说明", "word_count": 400}},
    ...
  ]
}}
score为标题质量评分（0-100）。"""

        # 调用AI
        http_client = httpx.AsyncClient(verify=False, timeout=120.0, follow_redirects=True, trust_env=False)
        async with AsyncOpenAI(api_key=config.api_key, base_url=base_url, http_client=http_client) as client:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的文章结构策划师。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # 解析JSON响应
            import json
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            data = json.loads(content)
            
            # 计算总字数和阅读时间
            total_word_count = sum(s.get("word_count", 0) for s in data.get("outline", []))
            estimated_time = f"{total_word_count // 400 + 1}分钟"  # 假设阅读速度400字/分钟
            
            logger.info(f"大纲生成完成，共 {len(data.get('outline', []))} 个部分")
            
            return GenerateOutlineResponse(
                titles=data.get("titles", []),
                outline=[OutlineSection(**s) for s in data.get("outline", [])],
                total_word_count=total_word_count,
                estimated_time=estimated_time
            )
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"生成大纲失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")

        if settings.ALLOW_MOCK_FALLBACK or settings.DEBUG:
            logger.warning("AI 大纲生成失败，已启用模拟大纲降级")
            return GenerateOutlineResponse(
                titles=[
                    {"title": f"深度解析：{request.topic}的核心价值", "score": 85},
                    {"title": f"90%的人都不知道的{request.topic}真相", "score": 88},
                ],
                outline=[
                    OutlineSection(title="引言", content=f"引入{request.topic}的重要性和背景", word_count=200),
                    OutlineSection(title="核心要点", content=f"分析{request.topic}的关键特征", word_count=400),
                    OutlineSection(title="实际应用", content=f"{request.topic}的应用场景和案例", word_count=300),
                    OutlineSection(title="总结", content="总结全文并提出行动建议", word_count=150),
                ],
                total_word_count=1050,
                estimated_time="3分钟"
            )

        raise HTTPException(
            status_code=502,
            detail={
                "message": "AI 大纲生成失败，请检查模型配置或稍后重试",
                "error_type": "ai_generate_outline_failed",
                "allow_mock_fallback": False,
                "debug_error": str(e) if settings.DEBUG else None,
            }
        )


@router.post("/expand-section", response_model=ExpandSectionResponse)
async def expand_section(request: ExpandSectionRequest, db: AsyncSession = Depends(get_db)):
    """
    扩写段落
    
    根据大纲要点扩写为详细的段落内容
    
    Args:
        request: 扩写段落请求
        db: 数据库会话
    
    Returns:
        扩写响应
    """
    try:
        config = await get_config_from_db(db)
        model = request.model or config.model or "deepseek-chat"
        base_url = config.base_url or "https://api.deepseek.com/v1"
        
        logger.info(f"扩写段落，要点: {request.outline_point[:50]}...")
        
        # 风格映射
        style_map = {
            "professional": "专业严谨，深度分析",
            "casual": "轻松活泼，通俗易懂",
            "humor": "幽默风趣，生动有趣",
            "story": "故事叙述，情感共鸣",
            "dry_goods": "干货分享，实用至上",
            "opinion": "观点评论，犀利独到",
        }
        
        prompt = f"""你是一位专业的文章作家。请根据以下大纲要点扩写段落。

大纲要点：{request.outline_point}
上下文：{request.context}
写作风格：{style_map.get(request.style, '专业严谨')}
目标字数：约{request.word_count}字

要求：
1. 内容详实，有深度和价值
2. 符合指定的写作风格
3. 包含具体例子或数据支撑
4. 段落清晰，适合手机阅读
5. 避免空洞和重复

请直接输出扩写内容，不要包含任何说明文字。"""

        http_client = httpx.AsyncClient(verify=False, timeout=120.0, follow_redirects=True, trust_env=False)
        async with AsyncOpenAI(api_key=config.api_key, base_url=base_url, http_client=http_client) as client:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一位专业的文章作家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # 提取关键词
            keywords = _extract_keywords(content)
            
            logger.info(f"段落扩写完成，字数: {len(content)}")
            
            return ExpandSectionResponse(
                content=content,
                word_count=len(content),
                keywords=keywords
            )
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"扩写段落失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")

        if settings.ALLOW_MOCK_FALLBACK or settings.DEBUG:
            logger.warning("AI 扩写失败，已启用模拟扩写降级")
            mock_content = f"""关于{request.outline_point}，这是一个值得深入探讨的话题。

首先，我们需要理解其核心价值。在实际应用中，这一点尤为明显。无论是从理论层面还是实践角度，都体现了其重要性。

具体来说，可以通过以下几个方面来实现：
1. 明确目标，制定详细计划
2. 分步骤执行，注重细节
3. 及时总结和调整

通过这样的方法，我们能够更好地理解和运用这一知识，从而在实际工作中取得更好的效果。

> 关键词：{request.outline_point[:10]}"""

            return ExpandSectionResponse(
                content=mock_content,
                word_count=len(mock_content),
                keywords=[request.outline_point[:10], "应用", "方法"]
            )

        raise HTTPException(
            status_code=502,
            detail={
                "message": "AI 扩写失败，请检查模型配置或稍后重试",
                "error_type": "ai_expand_section_failed",
                "allow_mock_fallback": False,
                "debug_error": str(e) if settings.DEBUG else None,
            }
        )


@router.post("/polish-article", response_model=PolishArticleResponse)
async def polish_article(request: PolishArticleRequest, db: AsyncSession = Depends(get_db)):
    """
    润色文章
    
    优化文章的语言表达、结构、逻辑性等
    
    Args:
        request: 润色文章请求
        db: 数据库会话
    
    Returns:
        润色响应
    """
    try:
        config = await get_config_from_db(db)
        model = request.model or config.model or "deepseek-chat"
        base_url = config.base_url or "https://api.deepseek.com/v1"
        
        logger.info(f"润色文章，类型: {request.polish_type}")
        
        # 润色类型提示词
        polish_prompts = {
            "overall": "请全面优化这篇文章，包括语言表达、段落结构、逻辑性等方面。",
            "clarity": "请优化这篇文章的清晰度，使表达更加准确、简洁。",
            "readability": "请优化这篇文章的可读性，使其更易于理解和阅读。",
            "engagement": "请优化这篇文章的吸引力，增加互动性和趣味性。",
        }
        
        prompt = f"""你是一位专业的编辑。请优化以下文章。

文章内容：
{request.content}

优化要求：
{polish_prompts.get(request.polish_type, '请全面优化这篇文章')}

要求：
1. 保持原意不变
2. 优化语言表达
3. 调整段落结构
4. 增强逻辑性
5. 使内容更流畅

请直接输出优化后的文章内容，不要包含任何说明文字。"""

        http_client = httpx.AsyncClient(verify=False, timeout=300.0, follow_redirects=True, trust_env=False)
        async with AsyncOpenAI(api_key=config.api_key, base_url=base_url, http_client=http_client) as client:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一位专业的编辑。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=4000
            )
            
            polished_content = response.choices[0].message.content
            
            # 生成修改摘要
            changes_summary = _generate_changes_summary(request.content, polished_content)
            
            # 评估质量
            quality_score = _assess_quality(polished_content)
            
            logger.info(f"文章润色完成，质量评分: {quality_score}")
            
            return PolishArticleResponse(
                polished_content=polished_content,
                changes_summary=changes_summary,
                quality_score=quality_score
            )
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"润色文章失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        
        # 降级方案：返回原始内容
        logger.warning("使用原始内容作为降级方案")
        return PolishArticleResponse(
            polished_content=request.content,
            changes_summary=["润色服务暂时不可用"],
            quality_score=_assess_quality(request.content)
        )


@router.post("/check-sensitive", response_model=CheckSensitiveResponse)
async def check_sensitive_words_endpoint(request: CheckSensitiveRequest):
    """
    检测敏感词
    
    检测文章中的敏感词，并提供替换建议
    
    Args:
        request: 检测敏感词请求
    
    Returns:
        检测结果
    """
    try:
        logger.info(f"检测敏感词，内容长度: {len(request.content)}")
        
        # 检测敏感词
        found_words = check_sensitive_words(request.content)
        
        # 生成匹配列表（带位置信息）
        matches = []
        for word in found_words:
            positions = [m.start() for m in re.finditer(re.escape(word), request.content)]
            for pos in positions:
                # 获取上下文（前后各20字）
                start = max(0, pos - 20)
                end = min(len(request.content), pos + len(word) + 20)
                context = request.content[start:end]
                
                from ..services.sensitive_words import get_replacement
                matches.append(SensitiveWordMatch(
                    word=word,
                    replacement=get_replacement(word),
                    position=pos,
                    context=context
                ))
        
        # 过滤内容
        filtered_content = filter_sensitive_words(request.content)
        
        logger.info(f"敏感词检测完成，发现 {len(found_words)} 个敏感词")
        
        return CheckSensitiveResponse(
            has_sensitive=len(found_words) > 0,
            matches=matches,
            filtered_content=filtered_content,
            total_count=len(found_words)
        )
        
    except Exception as e:
        import traceback
        logger.error(f"检测敏感词失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        
        raise HTTPException(status_code=500, detail=f"检测敏感词失败: {str(e)}")


# ========== 辅助函数 ==========

def _extract_keywords(content: str) -> List[str]:
    """提取关键词"""
    # 简单的关键词提取：提取加粗内容和重要词汇
    keywords = []
    
    # 提取加粗内容
    bold_matches = re.findall(r'\*\*(.+?)\*\*', content)
    keywords.extend(bold_matches)
    
    # 提取数字+关键词模式
    number_keywords = re.findall(r'\d+\s*(个|种|项|点|步)', content)
    keywords.extend(number_keywords)
    
    # 去重并限制数量
    unique_keywords = list(set(keywords))[:10]
    return unique_keywords


def _generate_changes_summary(original: str, polished: str) -> List[str]:
    """生成修改摘要"""
    changes = []
    
    # 比较字数变化
    if len(polished) != len(original):
        diff = len(polished) - len(original)
        if diff > 0:
            changes.append(f"字数增加 {diff} 字")
        else:
            changes.append(f"字数减少 {-diff} 字")
    
    # 检查结构变化
    original_sections = len(re.findall(r'^#+\s+', original, re.MULTILINE))
    polished_sections = len(re.findall(r'^#+\s+', polished, re.MULTILINE))
    if original_sections != polished_sections:
        changes.append(f"段落结构调整（{original_sections} → {polished_sections}个）")
    
    # 检查加粗使用
    original_bold = len(re.findall(r'\*\*', original))
    polished_bold = len(re.findall(r'\*\*', polished))
    if original_bold != polished_bold:
        changes.append(f"重点标记调整（{original_bold} → {polished_bold}处）")
    
    if not changes:
        changes.append("语言表达优化")
    
    return changes


def _assess_quality(content: str) -> float:
    """评估文章质量"""
    score = 70.0
    
    # 检查字数
    word_count = len(content)
    if 800 <= word_count <= 3000:
        score += 10
    elif word_count < 500:
        score -= 20
    
    # 检查结构
    if re.search(r'#+\s+', content):
        score += 10
    
    # 检查段落数量
    paragraphs = content.split('\n\n')
    if len(paragraphs) >= 3:
        score += 10
    
    return min(100.0, max(0.0, score))
