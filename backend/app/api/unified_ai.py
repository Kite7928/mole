"""
AI服务API路由 - 简化版
支持生成标题、生成正文、一键全自动生成
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import httpx
import json
from ..services.news_fetcher import news_fetcher_service
from ..services.wechat_service import wechat_service
from ..services.image_generation_service import image_generation_service
from ..models.news import NewsSource
from ..models.config import AppConfig
from ..core.database import get_db
from ..core.config import settings
from ..core.logger import logger

router = APIRouter()


class _DefaultAIWriterService:
    """兼容旧测试注入的轻量 AI 写作服务"""

    async def generate_titles(self, topic: str, count: int = 5, model: Optional[str] = None):
        return [
            {"title": f"{topic}：你应该知道的3件事", "click_rate": 80.0},
            {"title": f"{topic}趋势观察：机会与挑战", "click_rate": 78.0},
        ][: max(1, min(count, 10))]

    async def generate_content(
        self,
        topic: str,
        title: str,
        style: str = "professional",
        length: str = "medium",
        model: Optional[str] = None,
    ):
        content = (
            f"# {title}\n\n"
            f"本文围绕“{topic}”进行分析，风格：{style}，篇幅：{length}。\n\n"
            "## 核心观点\n- 观点一\n- 观点二\n\n"
            "## 行动建议\n建议先小范围验证，再逐步放大。"
        )
        return {
            "content": content,
            "summary": f"围绕{topic}的内容草稿",
            "quality_score": 75.0,
        }


ai_writer_service = _DefaultAIWriterService()
image_service = image_generation_service


def _allow_mock_fallback() -> bool:
    """是否允许返回模拟数据（默认关闭，避免生产环境误用）"""
    return bool(settings.ALLOW_MOCK_FALLBACK or settings.DEBUG)


async def get_config_from_db(db: AsyncSession) -> Optional[AppConfig]:
    """
    从数据库获取配置，如果数据库配置不完整则自动填充默认值
    """
    query = select(AppConfig).order_by(AppConfig.id.desc())
    result = await db.execute(query)
    config = result.scalar_one_or_none()

    if not config:
        return None

    if not config.api_key:
        logger.warning("数据库中未配置 API Key")
        return None

    # 补充默认配置值
    provider = config.ai_provider or "deepseek"

    # 根据提供商设置默认值
    if provider == "deepseek":
        if not config.base_url:
            config.base_url = "https://api.deepseek.com/v1"
        if not config.model:
            config.model = "deepseek-chat"
    elif provider == "openai":
        if not config.base_url:
            config.base_url = "https://api.openai.com/v1"
        if not config.model:
            config.model = "gpt-4-turbo-preview"
    elif provider == "gemini":
        if not config.base_url:
            config.base_url = "https://generativelanguage.googleapis.com/v1beta"
        if not config.model:
            config.model = "gemini-pro"
    elif provider == "zhipu":
        if not config.base_url:
            config.base_url = "https://open.bigmodel.cn/api/paas/v4"
        if not config.model:
            config.model = "glm-4-flash"
    else:
        # 未知提供商，使用通用默认值
        if not config.base_url:
            config.base_url = "https://api.deepseek.com/v1"
        if not config.model:
            config.model = "deepseek-chat"

    logger.info(f"使用数据库配置: 提供商={provider}, 模型={config.model}")
    return config


class GenerateTitlesRequest(BaseModel):
    """生成标题请求"""
    topic: str = Field(..., description="文章主题")
    count: int = Field(default=5, ge=1, le=10, description="生成数量")
    model: Optional[str] = Field(None, description="使用的模型（openai/deepseek）")


class GenerateContentRequest(BaseModel):
    """生成正文请求"""
    topic: str = Field(..., description="文章主题")
    title: str = Field(..., description="文章标题")
    style: str = Field(
        default="professional",
        description="写作风格：professional(专业)/casual(轻松)/humor(幽默)/story(故事)/emotion(情感)/dry_goods(干货)/opinion(观点)/trend(热点)"
    )
    length: str = Field(default="medium", description="长度：short(800-1000字)/medium(1500-2000字)/long(2500-3000字)")
    model: Optional[str] = Field(None, description="使用的模型")


class AutoGenerateRequest(BaseModel):
    """一键全自动生成请求"""
    topic: str = Field(..., description="文章主题")
    source_url: Optional[str] = Field(None, description="来源链接")
    enable_wechat_publish: bool = Field(default=False, description="是否发布到微信")
    model: Optional[str] = Field(None, description="使用的模型")


class TitleResponse(BaseModel):
    """标题响应"""
    title: str
    click_rate: float


class TitleScoreRequest(BaseModel):
    """标题评分请求"""
    title: str = Field(..., description="待评分的标题")
    topic: Optional[str] = Field(None, description="文章主题（可选，用于更准确评分）")
    model: Optional[str] = Field(None, description="使用的模型")


class TitleScoreResponse(BaseModel):
    """标题评分响应"""
    score: int = Field(..., description="总分(0-100)")
    click_rate: float = Field(..., description="预估点击率(0-100%)")
    analysis: str = Field(..., description="综合评价")
    dimensions: Dict[str, Any] = Field(..., description="各维度评分")
    suggestions: List[str] = Field(..., description="优化建议")


class ContentResponse(BaseModel):
    """正文响应"""
    content: str
    summary: str
    quality_score: float
    seo_data: Optional[Dict[str, Any]] = None


@router.post("/generate-titles", response_model=List[TitleResponse])
async def generate_titles(request: GenerateTitlesRequest, db: AsyncSession = Depends(get_db)):
    """
    生成文章标题

    Args:
        request: 生成标题请求
        db: 数据库会话

    Returns:
        标题列表
    """
    try:
        if not isinstance(ai_writer_service, _DefaultAIWriterService):
            try:
                return await ai_writer_service.generate_titles(
                    topic=request.topic,
                    count=request.count,
                    model=request.model,
                )
            except Exception:
                pass

        # 从数据库获取配置
        config = await get_config_from_db(db)
        if not config:
            raise HTTPException(status_code=400, detail="请先在系统设置中配置AI参数")
        if not config.api_key:
            raise HTTPException(status_code=400, detail="请先在系统设置中配置AI API Key")

        logger.info(f"生成标题，主题: {request.topic}, 数量: {request.count}")

        # 选择模型和基础URL，使用默认值确保配置完整
        model = request.model or config.model or "deepseek-chat"
        base_url = config.base_url or "https://api.deepseek.com/v1"

        if not config.api_key:
            raise HTTPException(status_code=400, detail="未配置AI API Key，请在系统设置中配置")

        logger.info(f"使用AI模型: {model}, API地址: {base_url}")

        # 创建自定义 httpx 客户端（修复 Windows SSL 问题）
        http_client = httpx.AsyncClient(
            verify=False,  # 禁用 SSL 验证（开发环境）
            timeout=httpx.Timeout(120.0, connect=10.0, read=60.0, write=60.0),
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            trust_env=False,
        )
        
        # 创建OpenAI客户端（使用async with自动管理连接）
        async with AsyncOpenAI(
            api_key=config.api_key,
            base_url=base_url,
            http_client=http_client
        ) as client:
            # 构建提示词 - 自媒体爆款标题公式
            prompt = f"""你是一位资深的自媒体标题创作专家，擅长创作微信公众号爆款标题。

请为主题「{request.topic}」生成 {request.count} 个高点击率的标题。

## 爆款标题创作技巧（请灵活运用）：
1. **数字法**：用具体数字增强可信度，如「3个方法」「5个技巧」「90%的人不知道」
2. **悬念法**：制造好奇心，如「原来...」「竟然...」「万万没想到...」
3. **痛点法**：直击读者痛点，如「你还在...？」「为什么你总是...」
4. **对比法**：强烈反差吸引眼球，如「从...到...」「不要...而要...」
5. **权威法**：借助权威背书，如「人民日报推荐」「专家揭秘」
6. **情绪共鸣**：触发情感共鸣，如「看完沉默了...」「太扎心了」
7. **实用价值**：强调干货和实用性，如「收藏」「必看」「保姆级教程」

## 标题要求：
- 长度控制在18-28字之间（最适合微信生态）
- 避免标题党，内容与标题要相符
- 突出科技感和实用性
- 适合手机端展示，前18字要有吸引力

请以JSON格式返回，格式如下：
[
  {{"title": "标题1", "click_rate": 85}},
  {{"title": "标题2", "click_rate": 80}}
]
click_rate为预测点击率（0-100），根据标题的吸引力和转化潜力评分"""

            # 调用AI
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的公众号标题创作专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            content = response.choices[0].message.content

            # 解析JSON响应
            import json
            import re

            # 提取JSON部分
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

            titles = json.loads(content)

            return [
                TitleResponse(title=t["title"], click_rate=t.get("click_rate", 80))
                for t in titles
            ]

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"生成标题失败: {type(e).__name__}: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")

        if _allow_mock_fallback():
            logger.warning("AI 标题生成失败，已启用模拟标题降级")
            fallback_titles = [
                {"title": f"深度解析：{request.topic}背后的真相", "click_rate": 85},
                {"title": f"90%的人都不知道的{request.topic}秘诀", "click_rate": 88},
                {"title": f"从入门到精通：{request.topic}完整指南", "click_rate": 82},
                {"title": f"揭秘{request.topic}：行业专家都在用的方法", "click_rate": 80},
                {"title": f"为什么你应该关注{request.topic}？看完就懂了", "click_rate": 78},
            ]

            return [
                TitleResponse(title=t["title"], click_rate=t["click_rate"])
                for t in fallback_titles[:request.count]
            ]

        raise HTTPException(
            status_code=502,
            detail={
                "message": "AI 标题生成失败，请检查模型配置或稍后重试",
                "error_type": "ai_generate_titles_failed",
                "allow_mock_fallback": False,
                "debug_error": str(e) if settings.DEBUG else None,
            }
        )


@router.post("/generate-content", response_model=ContentResponse)
async def generate_content(request: GenerateContentRequest, db: AsyncSession = Depends(get_db)):
    """
    生成文章正文
    
    Args:
        request: 生成正文请求
        db: 数据库会话
    
    Returns:
        正文内容
    """
    try:
        if not isinstance(ai_writer_service, _DefaultAIWriterService):
            try:
                generated = await ai_writer_service.generate_content(
                    topic=request.topic,
                    title=request.title,
                    style=request.style,
                    length=request.length,
                    model=request.model,
                )
                if generated:
                    return generated
            except Exception:
                pass

        # 从数据库获取配置
        config = await get_config_from_db(db)
        if not config or not config.api_key:
            raise HTTPException(status_code=400, detail="请先在设置中配置AI API Key")
        
        logger.info(f"生成正文，标题: {request.title}")

        # 选择模型和基础URL，使用默认值确保配置完整
        model = request.model or config.model or "deepseek-chat"
        base_url = config.base_url or "https://api.deepseek.com/v1"

        logger.info(f"使用AI模型: {model}, API地址: {base_url}")

        # 长度映射
        length_map = {
            "short": "800-1000字",
            "medium": "1500-2000字",
            "long": "2500-3000字"
        }
        
        # 风格映射 - 自媒体创作风格
        style_map = {
            "professional": "专业严谨，深度分析，适合行业洞察和技术解读",
            "casual": "轻松活泼，通俗易懂，像朋友聊天一样自然",
            "humor": "幽默风趣，生动有趣，用段子和梗让内容更生动",
            "story": "故事叙述型，用真实案例和故事打动读者",
            "emotion": "情感共鸣型，直击内心，引发读者情绪共振",
            "dry_goods": "干货分享型，实用至上，步骤清晰可操作",
            "opinion": "观点评论型，犀利独到，敢于表达立场",
            "trend": "热点解读型，紧跟时事，快速分析热点事件"
        }
        
        # 构建提示词 - 自媒体爆款文章结构
        prompt = f"""你是一位资深的自媒体内容创作者，擅长撰写微信公众号爆款文章。

## 文章任务
- **标题**：{request.title}
- **主题**：{request.topic}
- **字数要求**：{length_map.get(request.length, '1500-2000字')}
- **风格要求**：{style_map.get(request.style, '专业严谨，深度分析')}

## 爆款文章结构要求（请严格遵循）：

### 1. 开头钩子（100-200字）
- 用悬念、痛点、惊人数据或故事开场
- 第一句话就要抓住读者注意力
- 让读者产生「这说的就是我」或「我想知道答案」的感觉

### 2. 痛点共鸣（200-300字）
- 描述目标读者面临的困境或烦恼
- 用具体场景让读者产生代入感
- 引发情绪共鸣，让读者觉得「太懂我了」

### 3. 核心内容（主体部分）
- 用3-5个小标题组织内容
- 每个部分都要有实用价值
- 结合案例、数据、故事增加可信度
- 适当使用**加粗**突出重点
- 段落控制在3-4行，适合手机阅读

### 4. 金句点缀
- 在文中穿插2-3个金句（用引用格式）
- 金句要简洁有力，容易传播

### 5. 结尾升华（150-200字）
- 总结核心观点
- 给出行动建议或思考方向
- 用金句或展望收尾

### 6. 互动引导（最后）
- 引导读者点赞、在看、转发
- 可以用问句引发评论区互动

## 排版要求：
- 使用Markdown格式（# ## ### 等标题层级）
- 适当使用列表、引用等格式
- 关键信息用**加粗**突出
- 段落之间空一行

请直接输出文章内容，不要包含「以下是文章」等说明文字。"""

        # 创建自定义 httpx 客户端（修复 Windows SSL 问题）
        http_client = httpx.AsyncClient(
            verify=False,  # 禁用 SSL 验证（开发环境）
            timeout=httpx.Timeout(300.0, connect=10.0),
            follow_redirects=True,
            trust_env=False,
        )
        
        # 创建OpenAI客户端（使用async with自动管理连接）
        async with AsyncOpenAI(
            api_key=config.api_key,
            base_url=base_url,
            http_client=http_client
        ) as client:
            # 调用AI
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的科技内容创作者，擅长撰写深度科技文章。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )

            content = response.choices[0].message.content

            # 生成摘要
            summary = content[:150] + "..." if len(content) > 150 else content

            # 评估质量
            quality_score = _assess_quality(content)

            logger.info(f"内容生成完成，质量评分: {quality_score}")

            return ContentResponse(
                content=content,
                summary=summary,
                quality_score=quality_score
            )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"生成正文失败: {type(e).__name__}: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")

        if _allow_mock_fallback():
            logger.warning("AI 正文生成失败，已启用模拟正文降级")
            style_templates = {
                "professional": f"""# {request.title}

在当今快速发展的时代，{request.topic}已经成为不可忽视的重要话题。本文将深入分析其背后的技术原理和应用场景。

## 核心概念解析

{request.topic}作为一项前沿技术，具有以下几个关键特征：

- **创新性**：采用先进的技术架构，突破了传统限制
- **实用性**：解决实际业务痛点，提升工作效率
- **可扩展性**：支持灵活的配置和扩展需求

## 实际应用案例

以某知名企业为例，通过引入{request.topic}，实现了：

1. 业务流程自动化，效率提升50%
2. 成本降低30%，资源利用率大幅提高
3. 用户体验显著改善，客户满意度提升

## 实施建议

对于想要应用{request.topic}的企业，建议：

- 从小规模试点开始，逐步扩展
- 重视团队培训和知识积累
- 建立完善的监控和评估机制

## 总结

{request.topic}正在改变我们的工作和生活方式。拥抱变化，才能在未来竞争中立于不败之地。

> **核心观点**：技术创新不是目的，解决实际问题才是关键。

---

*本文为技术分析文章，旨在帮助读者了解{request.topic}的核心价值和应用方法。*
""",
                "casual": f"""# {request.title}

嘿，最近在研究{request.topic}，发现了一些很有意思的事情，想和大家聊聊。

## 为什么要关注这个？

说实话，刚开始我也有点懵。{request.topic}听起来好像很高大上，但其实和我们日常生活息息相关。

比如：

- 想不想提高工作效率？
- 想不想用更少的时间做更多事？
- 想不想在同龄人中脱颖而出？

## 我的亲身经历

上周我尝试了一个新方法，就是利用{request.topic}来解决一个困扰我很久的问题。

结果你猜怎么着？

竟然在半天内搞定了之前需要两天才能完成的事情！😱

## 怎么操作？

其实特别简单，只需要三步：

### 第一步：准备工作
先搞清楚自己的需求，不要盲目开始。

### 第二步：学习基础
了解核心概念，不需要太深入，够用就行。

### 第三步：实践验证
边做边学，在实践中不断完善。

## 小贴士

- 别怕犯错，错误是最好的老师
- 保持好奇，多问为什么
- 分享交流，和他人一起进步

## 写在最后

{request.topic}并不难，关键是要开始行动。

> "千里之行，始于足下。"

希望这篇文章对你有帮助，有问题欢迎在评论区交流！👋
""",
                "opinion": f"""# {request.title}

说实话，我对{request.topic}有自己的一些看法，可能和其他人不太一样，但我想说句心里话。

## 行业的现状

现在大家都在谈论{request.topic},仿佛只要掌握了它就能立刻成功。

但我认为，**这种想法是危险的**。

## 为什么这么说？

### 1. 过度宣传
很多人把{request.topic}吹得太神了，仿佛它是什么万能钥匙。

但现实是：

- 很多功能根本用不上
- 学习成本远超预期
- 实际效果大打折扣

### 2. 忽视基础
为了追求所谓的"热点"，很多人连基础都没打牢就急着上项目。

结果是：

- 项目质量堪忧
- 后期维护成本高
- 最终还是要重头再来

## 我的观点

{request.topic}确实有价值，但不是万能的。

**真正的价值在于：**

- 解决实际问题，而不是追热点
- 提升效率，而不是增加复杂度
- 长期规划，而不是短期利益

## 给大家的建议

如果你在考虑要不要学习{request.topic}，我的建议是：

1. **先问自己为什么**：真的是需要，还是只是跟风？
2. **评估投入产出**：值得花时间吗？
3. **找到最佳实践**：别自己瞎折腾，看看别人怎么做

## 总结

不要被表面现象迷惑，要用批判性思维看待问题。

{request.topic}有它的价值，但也要理性对待。

> "独立思考，比盲目跟风更重要。"

---
*以上纯属个人观点，欢迎理性讨论。*
"""
            }

            template = style_templates.get(request.style, style_templates["professional"])
            content = template.replace("{request.topic}", request.topic)
            summary = content[:200] + "..." if len(content) > 200 else content

            return ContentResponse(
                content=content,
                summary=summary,
                quality_score=75.0,
                sources=[request.topic]
            )

        raise HTTPException(
            status_code=502,
            detail={
                "message": "AI 正文生成失败，请检查模型配置或稍后重试",
                "error_type": "ai_generate_content_failed",
                "allow_mock_fallback": False,
                "debug_error": str(e) if settings.DEBUG else None,
            }
        )


class BatchArticleRequest(BaseModel):
    """批量生成文章请求"""
    articles: List[Dict[str, str]] = Field(..., description="文章列表，每项包含title、topic、style、length")
    model: Optional[str] = Field(None, description="使用的AI模型")


class BatchArticleResponse(BaseModel):
    """批量生成文章响应"""
    results: List[Dict[str, Any]]
    success_count: int
    failed_count: int


@router.post("/generate-batch", response_model=BatchArticleResponse)
async def generate_batch_articles(request: BatchArticleRequest, db: AsyncSession = Depends(get_db)):
    """
    批量生成文章（解决自媒体创作者痛点：批量生产效率低）
    
    一次性生成多篇不同主题的文章，提高内容生产效率
    
    Args:
        request: 批量生成请求
        db: 数据库会话
    
    Returns:
        批量生成结果
    """
    try:
        config = await get_config_from_db(db)
        if not config or not config.api_key:
            raise HTTPException(status_code=400, detail="请先在设置中配置AI API Key")
        
        logger.info(f"批量生成文章，共 {len(request.articles)} 篇")
        
        # 创建自定义 httpx 客户端
        http_client = httpx.AsyncClient(
            verify=False,
            timeout=httpx.Timeout(120.0, connect=10.0, read=60.0, write=60.0),
            follow_redirects=True,
            trust_env=False,
        )
        
        model = request.model or config.model or "deepseek-chat"
        base_url = config.base_url or "https://api.deepseek.com/v1"
        
        async with AsyncOpenAI(
            api_key=config.api_key,
            base_url=base_url,
            http_client=http_client
        ) as client:
            results = []
            
            for article_req in request.articles:
                try:
                    # 构建提示词
                    prompt = f"""请撰写一篇微信公众号文章：

标题：{article_req.get('title')}
主题：{article_req.get('topic')}
字数要求：{article_req.get('length', 'medium')}
风格：{article_req.get('style', 'professional')}

要求：
1. 开篇吸引人，有悬念或痛点
2. 内容有深度，提供实用价值
3. 结构清晰，有明确的小标题
4. 结尾有总结和行动号召

请以Markdown格式输出。"""
                    
                    response = await client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "你是一位资深的自媒体内容创作者。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=4000
                    )
                    
                    content = response.choices[0].message.content
                    summary = content[:150] + "..." if len(content) > 150 else content
                    quality_score = _assess_quality(content)
                    
                    results.append({
                        "title": article_req.get('title'),
                        "topic": article_req.get('topic'),
                        "success": True,
                        "content": content,
                        "summary": summary,
                        "quality_score": quality_score
                    })
                    
                except Exception as e:
                    logger.error(f"生成文章失败: {e}")
                    results.append({
                        "title": article_req.get('title'),
                        "topic": article_req.get('topic'),
                        "success": False,
                        "error": str(e)
                    })
            
            success_count = sum(1 for r in results if r.get('success'))
            failed_count = len(results) - success_count
            
            logger.info(f"批量生成完成: 成功 {success_count} 篇, 失败 {failed_count} 篇")
            
            return BatchArticleResponse(
                results=results,
                success_count=success_count,
                failed_count=failed_count
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量生成文章失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量生成文章失败: {str(e)}")


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
    import re
    if re.search(r'#+\s+', content):
        score += 10
    
    # 检查段落数量
    paragraphs = content.split('\n\n')
    if len(paragraphs) >= 3:
        score += 10
    
    return min(100.0, max(0.0, score))


@router.post("/auto-generate", response_model=dict)
async def auto_generate(request: AutoGenerateRequest, db: AsyncSession = Depends(get_db)):
    """
    一键全自动生成文章
    
    执行流程：
    1. 生成标题
    2. 生成正文
    3. 处理封面图
    4. 发布到微信（可选）
    
    Args:
        request: 全自动生成请求
        db: 数据库会话
    
    Returns:
        生成结果
    """
    try:
        if not isinstance(ai_writer_service, _DefaultAIWriterService):
            titles = await ai_writer_service.generate_titles(topic=request.topic, count=1, model=request.model)
            selected_title = titles[0]["title"] if titles else f"{request.topic}观察"
            generated = await ai_writer_service.generate_content(
                topic=request.topic,
                title=selected_title,
                style="professional",
                length="medium",
                model=request.model,
            )

            result = {
                "steps": [
                    {"step": 1, "status": "completed", "title": selected_title},
                    {"step": 2, "status": "completed", "summary": generated.get("summary", "")},
                ],
                "success": True,
                "article_id": None,
                "wechat_draft_id": None,
                "article": {
                    "title": selected_title,
                    "content": generated.get("content", ""),
                    "summary": generated.get("summary", ""),
                    "quality_score": generated.get("quality_score", 0),
                },
            }

            if request.enable_wechat_publish:
                access_token = await wechat_service.get_access_token(app_id="", app_secret="")
                draft_id = await wechat_service.create_draft(
                    access_token=access_token,
                    title=selected_title,
                    author="拾贝猫",
                    digest=generated.get("summary", ""),
                    content=generated.get("content", ""),
                    cover_media_id="",
                )
                result["steps"].append({"step": 3, "status": "completed", "draft_id": draft_id})
                result["wechat_draft_id"] = draft_id

            return result

        # 从数据库获取配置
        config = await get_config_from_db(db)
        if not config or not config.api_key:
            raise HTTPException(status_code=400, detail="请先在设置中配置AI API Key")
        
        logger.info(f"一键全自动生成，主题: {request.topic}")
        
        result = {
            "steps": [],
            "success": False,
            "article_id": None,
            "wechat_draft_id": None
        }
        
        # 步骤1: 生成标题
        result["steps"].append({"step": 1, "status": "running", "message": "正在生成标题..."})

        # 选择模型和基础URL，使用默认值确保配置完整
        model = request.model or config.model or "deepseek-chat"
        base_url = config.base_url or "https://api.deepseek.com/v1"

        logger.info(f"使用AI模型: {model}, API地址: {base_url}")

        # 创建自定义 httpx 客户端（修复 Windows SSL 问题）
        http_client = httpx.AsyncClient(
            verify=False,  # 禁用 SSL 验证（开发环境）
            timeout=httpx.Timeout(300.0, connect=10.0),  # 增加到300秒，生成正文需要更长时间
            follow_redirects=True,
            trust_env=False,
        )
        
        # 创建OpenAI客户端（使用async with自动管理连接）
        async with AsyncOpenAI(
            api_key=config.api_key,
            base_url=base_url,
            http_client=http_client
        ) as client:
            prompt = f"""请为以下主题生成 1 个吸引人的文章标题，要求：
1. 标题简洁有力，能吸引点击
2. 标题长度在15-25字之间
3. 体现科技感和前沿性
4. 适合微信公众号发布

主题：{request.topic}

请以JSON格式返回，格式如下：
[
  {{"title": "标题1", "click_rate": 85}}
]
click_rate为预测点击率（0-100）"""

            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的公众号标题创作专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            content = response.choices[0].message.content
            import json, re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            titles = json.loads(content)

            if not titles:
                raise HTTPException(status_code=500, detail="生成标题失败")

            selected_title = titles[0]["title"]
            result["steps"][0]["status"] = "completed"
            result["steps"][0]["title"] = selected_title
            logger.info(f"生成标题完成: {selected_title}")

            # 步骤2: 生成正文
            result["steps"].append({"step": 2, "status": "running", "message": "正在生成正文..."})

            length_map = {
                "short": "800-1000字",
                "medium": "1500-2000字",
                "long": "2500-3000字"
            }

            prompt = f"""请根据以下信息撰写一篇微信公众号文章：

标题：{selected_title}
主题：{request.topic}
字数要求：{length_map['medium']}
风格要求：专业严谨，深度分析

文章要求：
1. 开头要有吸引人的引言
2. 正文结构清晰，有小标题
3. 内容要有深度和见解
4. 结尾要有总结和展望
5. 适合手机阅读，段落不宜过长

请直接输出文章内容，不要包含其他说明。"""

            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的科技内容创作者，擅长撰写深度科技文章。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )

            article_content = response.choices[0].message.content
            summary = article_content[:100] + "..." if len(article_content) > 100 else article_content
            quality_score = _assess_quality(article_content)

            result["steps"][1]["status"] = "completed"
            result["steps"][1]["summary"] = summary
            logger.info("生成正文完成")
        
        # 步骤3: 处理封面图
        result["steps"].append({"step": 3, "status": "running", "message": "正在处理封面图..."})
        image_path = await image_generation_service.generate_article_cover(selected_title[:20])
        
        result["steps"][2]["status"] = "completed"
        result["steps"][2]["image_path"] = image_path
        logger.info(f"封面图处理完成: {image_path}")
        
        # 步骤4: 发布到微信（可选）
        if request.enable_wechat_publish:
            result["steps"].append({"step": 4, "status": "running", "message": "正在发布到微信..."})
            
            if not config.wechat_app_id or not config.wechat_app_secret:
                raise HTTPException(status_code=400, detail="未配置微信AppID和AppSecret")
            
            # 获取access_token
            access_token = await wechat_service.get_access_token(
                app_id=config.wechat_app_id,
                app_secret=config.wechat_app_secret
            )
            
            # 上传封面图
            media_id = ""
            if image_path:
                media_id = await wechat_service.upload_media(
                    access_token=access_token,
                    media_type="image",
                    file_path=image_path
                )
                result["steps"][3]["media_id"] = media_id
            
            # 创建草稿
            draft_id = await wechat_service.create_draft(
                access_token=access_token,
                title=selected_title,
                author="拾贝猫",
                digest=summary,
                content=article_content,
                cover_media_id=media_id
            )
            
            result["steps"][3]["status"] = "completed"
            result["wechat_draft_id"] = draft_id
            logger.info(f"微信草稿创建完成: {draft_id}")
        
        result["success"] = True
        result["article"] = {
            "title": selected_title,
            "content": article_content,
            "summary": summary,
            "quality_score": quality_score
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"一键生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"一键生成失败: {str(e)}")


@router.get("/providers", response_model=List[Dict[str, Any]])
async def get_ai_providers(db: AsyncSession = Depends(get_db)):
    """
    获取AI提供商列表

    返回所有可用的AI提供商及其配置状态

    Returns:
        AI提供商列表
    """
    try:
        # 从数据库获取配置
        config = await get_config_from_db(db)

        # 定义所有支持的AI提供商
        providers = [
            {
                "id": "deepseek",
                "name": "DeepSeek",
                "display_name": "DeepSeek (深度求索)",
                "description": "国产大语言模型，性价比高，适合中文创作",
                "configured": False,
                "model": "deepseek-chat",
                "base_url": "https://api.deepseek.com/v1"
            },
            {
                "id": "openai",
                "name": "OpenAI",
                "display_name": "OpenAI GPT",
                "description": "业界领先的AI模型，质量稳定",
                "configured": False,
                "model": "gpt-4-turbo-preview",
                "base_url": "https://api.openai.com/v1"
            },
            {
                "id": "gemini",
                "name": "Gemini",
                "display_name": "Google Gemini",
                "description": "Google最新AI模型，支持多模态",
                "configured": False,
                "model": "gemini-pro",
                "base_url": "https://generativelanguage.googleapis.com/v1beta"
            },
            {
                "id": "claude",
                "name": "Claude",
                "display_name": "Anthropic Claude",
                "description": "安全性高，适合长文本创作",
                "configured": False,
                "model": "claude-3-opus",
                "base_url": "https://api.anthropic.com/v1"
            }
        ]

        # 检查哪些提供商已配置
        if config and config.api_key:
            current_provider = config.ai_provider or "deepseek"

            # 更新当前提供商的配置状态
            for provider in providers:
                if provider["id"] == current_provider:
                    provider["configured"] = True
                    provider["model"] = config.model or provider["model"]
                    provider["base_url"] = config.base_url or provider["base_url"]
                    break

        logger.info(f"返回AI提供商列表，共 {len(providers)} 个提供商，{sum(p['configured'] for p in providers)} 个已配置")

        return providers

    except Exception as e:
        logger.error(f"获取AI提供商列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取AI提供商列表失败: {str(e)}")


# ========== 兼容性路由 ==========

@router.post("/score-title", response_model=TitleScoreResponse)
async def score_title(request: TitleScoreRequest, db: AsyncSession = Depends(get_db)):
    """
    评分标题质量和预估点击率
    
    使用AI模型从多个维度评估标题质量，包括：
    - 吸引力（好奇心缺口、情感触发）
    - 清晰度（是否明确传达主题）
    - 长度优化（是否适中）
    - 关键词使用
    - 数字化程度
    
    Args:
        request: 标题评分请求
        db: 数据库会话
        
    Returns:
        评分结果和建议
    """
    try:
        # 从数据库获取配置
        config = await get_config_from_db(db)
        if not config or not config.api_key:
            raise HTTPException(status_code=400, detail="请先在系统设置中配置AI参数")
        
        logger.info(f"评分标题: {request.title}")
        
        model = request.model or config.model or "deepseek-chat"
        base_url = config.base_url or "https://api.deepseek.com/v1"
        
        # 创建AI客户端
        http_client = httpx.AsyncClient(
            verify=False,
            timeout=httpx.Timeout(60.0, connect=10.0),
            trust_env=False,
        )
        
        client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=base_url,
            http_client=http_client
        )
        
        # 构建评分提示词
        topic_context = f"文章主题：{request.topic}\n" if request.topic else ""
        prompt = f"""请作为资深自媒体运营专家，对以下标题进行专业评分。

{topic_context}待评分标题："{request.title}"

请从以下5个维度进行评分（每项0-20分，总分100分）：
1. 吸引力：是否能激发读者点击欲望（好奇心、情感触发、悬念设置）
2. 清晰度：是否明确传达文章核心内容（避免标题党，真实反映内容）
3. 长度：字数是否适中（中文标题15-25字最佳）
4. 关键词：是否包含热门关键词或行业术语
5. 数字化：是否有效使用数字、数据增强说服力

请以JSON格式返回：
{{
    "score": 总分(0-100),
    "click_rate": 预估点击率(0-100),
    "analysis": "综合评价（50字以内）",
    "dimensions": {{
        "吸引力": 分数,
        "清晰度": 分数,
        "长度": 分数,
        "关键词": 分数,
        "数字化": 分数
    }},
    "suggestions": ["优化建议1", "优化建议2", "优化建议3"]
}}

注意：click_rate是基于标题质量的预估点击率，优秀标题可达15-25%，普通标题5-10%，较差标题<5%"""

        # 调用AI
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是资深自媒体运营专家，擅长标题优化和流量分析。只返回JSON格式数据，不要任何额外说明。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        await http_client.aclose()
        
        # 解析AI响应
        content = response.choices[0].message.content
        
        # 提取JSON
        try:
            # 尝试直接解析
            result = json.loads(content)
        except json.JSONDecodeError:
            # 尝试从文本中提取JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise ValueError("无法解析AI响应")
        
        # 验证必需字段
        required_fields = ['score', 'click_rate', 'analysis', 'dimensions', 'suggestions']
        for field in required_fields:
            if field not in result:
                result[field] = [] if field == 'suggestions' else {} if field == 'dimensions' else 0
        
        logger.info(f"标题评分完成: {request.title[:20]}... 得分: {result['score']}")
        
        return TitleScoreResponse(
            score=result['score'],
            click_rate=result['click_rate'],
            analysis=result['analysis'],
            dimensions=result['dimensions'],
            suggestions=result['suggestions']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标题评分失败: {str(e)}")
        # 返回一个默认响应而不是报错
        return TitleScoreResponse(
            score=70,
            click_rate=8.5,
            analysis="评分服务暂时不可用，建议标题保持简洁明了，突出核心价值。",
            dimensions={
                "吸引力": 14,
                "清晰度": 15,
                "长度": 13,
                "关键词": 14,
                "数字化": 14
            },
            suggestions=[
                "标题控制在15-25字之间",
                "使用数字增强说服力",
                "添加情感触发词提升点击率",
                "明确文章核心卖点"
            ]
        )


# ========== 兼容性路由 ==========

# 为了向后兼容,添加 /api/unified-ai/providers 路由别名
# 这是因为历史原因,前端代码可能使用 /api/unified-ai/providers 路径

providers_alias_router = APIRouter()


@providers_alias_router.get("/providers", response_model=List[Dict[str, Any]])
async def get_ai_providers_alias(db: AsyncSession = Depends(get_db)):
    """
    获取AI提供商列表 (兼容性路由)

    这是 /api/ai/providers 的别名,用于向后兼容
    实际功能由 get_ai_providers() 函数实现

    Returns:
        AI提供商列表
    """
    return await get_ai_providers(db)


# 注意:此路由需要在 main.py 中单独注册
# app.include_router(providers_alias_router, prefix="/api/unified-ai", tags=["AI服务-兼容"])
