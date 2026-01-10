"""
集成API路由
提供数据分析、国内AI模型、图片生成、GitHub等API的端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from ..core.database import get_db
from ..core.logger import logger
from ..services.data_analysis_service import data_analysis_service
from ..services.domestic_ai_service import domestic_ai_service
from ..services.image_generation_service import image_generation_service
from ..services.github_service import github_service

router = APIRouter()


# ============================================================================
# 数据分析API端点
# ============================================================================

class BaiduIndexRequest(BaseModel):
    keywords: List[str] = Field(..., description="关键词列表")
    start_date: Optional[str] = Field(None, description="开始日期 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="结束日期 (YYYY-MM-DD)")


class WechatIndexRequest(BaseModel):
    keywords: List[str] = Field(..., description="关键词列表")
    start_date: Optional[str] = Field(None, description="开始日期 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="结束日期 (YYYY-MM-DD)")


class KeywordTrendRequest(BaseModel):
    keyword: str = Field(..., description="关键词")
    platform: str = Field("all", description="平台 (baidu, wechat, weibo, all)")


class CompetitorAnalysisRequest(BaseModel):
    keywords: List[str] = Field(..., description="竞品关键词列表")


@router.post("/data-analysis/baidu-index")
async def fetch_baidu_index(request: BaiduIndexRequest):
    """获取百度指数数据"""
    try:
        logger.info(f"Fetching Baidu Index for keywords: {request.keywords}")
        result = await data_analysis_service.fetch_baidu_index(
            keywords=request.keywords,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching Baidu Index: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data-analysis/wechat-index")
async def fetch_wechat_index(request: WechatIndexRequest):
    """获取微信指数数据"""
    try:
        logger.info(f"Fetching WeChat Index for keywords: {request.keywords}")
        result = await data_analysis_service.fetch_wechat_index(
            keywords=request.keywords,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching WeChat Index: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-analysis/weibo-hot")
async def fetch_weibo_hot_topics(
    limit: int = Query(20, ge=1, le=50, description="返回数量")
):
    """获取微博热搜话题"""
    try:
        logger.info(f"Fetching Weibo hot topics, limit: {limit}")
        result = await data_analysis_service.fetch_weibo_hot_topics(limit=limit)
        return result
    except Exception as e:
        logger.error(f"Error fetching Weibo hot topics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data-analysis/keyword-trend")
async def analyze_keyword_trend(request: KeywordTrendRequest):
    """分析关键词趋势"""
    try:
        logger.info(f"Analyzing keyword trend: {request.keyword}")
        result = await data_analysis_service.analyze_keyword_trend(
            keyword=request.keyword,
            platform=request.platform
        )
        return result
    except Exception as e:
        logger.error(f"Error analyzing keyword trend: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-analysis/hot-keywords")
async def get_hot_keywords(
    platform: str = Query("all", description="平台 (baidu, wechat, weibo, all)"),
    limit: int = Query(10, ge=1, le=50, description="返回数量")
):
    """获取热门关键词"""
    try:
        logger.info(f"Getting hot keywords, platform: {platform}")
        result = await data_analysis_service.get_hot_keywords(
            platform=platform,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"Error getting hot keywords: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data-analysis/competitor-analysis")
async def get_competitor_analysis(request: CompetitorAnalysisRequest):
    """获取竞品分析"""
    try:
        logger.info(f"Getting competitor analysis for keywords: {request.keywords}")
        result = await data_analysis_service.get_competitor_analysis(
            keywords=request.keywords
        )
        return result
    except Exception as e:
        logger.error(f"Error getting competitor analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 国内AI模型端点
# ============================================================================

class DomesticAITitlesRequest(BaseModel):
    topic: str = Field(..., description="主题")
    count: int = Field(5, ge=1, le=10, description="生成数量")
    model: str = Field("qwen", description="模型类型 (qwen)")


class DomesticAIContentRequest(BaseModel):
    topic: str = Field(..., description="主题")
    title: str = Field(..., description="标题")
    style: str = Field("professional", description="写作风格")
    length: str = Field("medium", description="文章长度")
    model: str = Field("qwen", description="模型类型 (qwen)")


@router.post("/domestic-ai/titles/generate")
async def generate_titles_with_domestic(request: DomesticAITitlesRequest):
    """使用国内AI模型生成标题"""
    try:
        logger.info(f"Generating titles with {request.model} for topic: {request.topic}")
        result = await domestic_ai_service.generate_titles_with_domestic(
            topic=request.topic,
            count=request.count,
            model=request.model
        )
        return result
    except Exception as e:
        logger.error(f"Error generating titles with domestic AI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/domestic-ai/content/generate")
async def generate_content_with_domestic(request: DomesticAIContentRequest):
    """使用国内AI模型生成文章内容"""
    try:
        logger.info(f"Generating content with {request.model} for: {request.title}")
        result = await domestic_ai_service.generate_content_with_domestic(
            topic=request.topic,
            title=request.title,
            style=request.style,
            length=request.length,
            model=request.model
        )
        return result
    except Exception as e:
        logger.error(f"Error generating content with domestic AI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 图片生成API端点
# ============================================================================

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="提示词")
    provider: str = Field("dalle", description="提供商 (dalle, midjourney, stable-diffusion)")
    size: Optional[str] = Field(None, description="图片尺寸")
    quality: Optional[str] = Field(None, description="图片质量")
    n: int = Field(1, ge=1, le=4, description="生成数量")


class ArticleCoverRequest(BaseModel):
    topic: str = Field(..., description="文章主题")
    style: str = Field("professional", description="风格 (professional, creative, minimal, vibrant)")
    provider: str = Field("dalle", description="提供商 (dalle, midjourney, stable-diffusion)")


class InfographicRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="数据内容")
    style: str = Field("modern", description="风格")


class ImageEditRequest(BaseModel):
    image_url: str = Field(..., description="原始图片URL")
    prompt: str = Field(..., description="编辑提示词")
    provider: str = Field("dalle", description="提供商")


@router.post("/image-generation/generate")
async def generate_image(request: ImageGenerationRequest):
    """生成图片"""
    try:
        logger.info(f"Generating image with {request.provider}")
        if request.provider == "dalle":
            result = await image_generation_service.generate_with_dalle(
                prompt=request.prompt,
                size=request.size,
                quality=request.quality,
                n=request.n
            )
        elif request.provider == "midjourney":
            result = await image_generation_service.generate_with_midjourney(
                prompt=request.prompt,
                size=request.size or "1024x1024",
                n=request.n
            )
        elif request.provider == "stable-diffusion":
            result = await image_generation_service.generate_with_stable_diffusion(
                prompt=request.prompt,
                size=request.size or "1024x1024",
                n=request.n
            )
        else:
            raise ValueError(f"Unknown provider: {request.provider}")

        return result
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-generation/article-cover")
async def generate_article_cover(request: ArticleCoverRequest):
    """生成文章封面图"""
    try:
        logger.info(f"Generating article cover for topic: {request.topic}")
        result = await image_generation_service.generate_article_cover(
            topic=request.topic,
            style=request.style,
            provider=request.provider
        )
        return result
    except Exception as e:
        logger.error(f"Error generating article cover: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-generation/infographic")
async def generate_infographic(request: InfographicRequest):
    """生成信息图"""
    try:
        logger.info("Generating infographic")
        result = await image_generation_service.generate_infographic(
            data=request.data,
            style=request.style
        )
        return result
    except Exception as e:
        logger.error(f"Error generating infographic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-generation/edit")
async def edit_image(request: ImageEditRequest):
    """编辑图片"""
    try:
        logger.info(f"Editing image with {request.provider}")
        result = await image_generation_service.edit_image(
            image_url=request.image_url,
            prompt=request.prompt,
            provider=request.provider
        )
        return result
    except Exception as e:
        logger.error(f"Error editing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GitHub API端点
# ============================================================================

class GitHubCreateIssueRequest(BaseModel):
    title: str = Field(..., description="Issue标题")
    body: str = Field(..., description="Issue内容")
    owner: Optional[str] = Field(None, description="仓库所有者")
    repo: Optional[str] = Field(None, description="仓库名称")
    labels: Optional[List[str]] = Field(None, description="标签列表")


class GitHubCreatePRRequest(BaseModel):
    title: str = Field(..., description="PR标题")
    body: str = Field(..., description="PR内容")
    head: str = Field(..., description="源分支")
    base: str = Field(..., description="目标分支")
    owner: Optional[str] = Field(None, description="仓库所有者")
    repo: Optional[str] = Field(None, description="仓库名称")


@router.get("/github/repository")
async def get_github_repository(
    owner: Optional[str] = Query(None, description="仓库所有者"),
    repo: Optional[str] = Query(None, description="仓库名称")
):
    """获取GitHub仓库信息"""
    try:
        logger.info(f"Getting GitHub repository: {owner}/{repo}")
        result = await github_service.get_repository_info(
            owner=owner,
            repo=repo
        )
        return result
    except Exception as e:
        logger.error(f"Error getting GitHub repository: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/issues")
async def list_github_issues(
    owner: Optional[str] = Query(None, description="仓库所有者"),
    repo: Optional[str] = Query(None, description="仓库名称"),
    state: str = Query("open", description="状态 (open, closed, all)"),
    limit: int = Query(20, ge=1, le=100, description="返回数量")
):
    """列出GitHub Issues"""
    try:
        logger.info(f"Listing GitHub issues for {owner}/{repo}")
        result = await github_service.list_issues(
            owner=owner,
            repo=repo,
            state=state,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"Error listing GitHub issues: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/github/issues/create")
async def create_github_issue(request: GitHubCreateIssueRequest):
    """创建GitHub Issue"""
    try:
        logger.info(f"Creating GitHub issue: {request.title}")
        result = await github_service.create_issue(
            title=request.title,
            body=request.body,
            owner=request.owner,
            repo=request.repo,
            labels=request.labels
        )
        return result
    except Exception as e:
        logger.error(f"Error creating GitHub issue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/pull-requests")
async def list_github_pull_requests(
    owner: Optional[str] = Query(None, description="仓库所有者"),
    repo: Optional[str] = Query(None, description="仓库名称"),
    state: str = Query("open", description="状态 (open, closed, all)"),
    limit: int = Query(20, ge=1, le=100, description="返回数量")
):
    """列出GitHub Pull Requests"""
    try:
        logger.info(f"Listing GitHub PRs for {owner}/{repo}")
        result = await github_service.list_pull_requests(
            owner=owner,
            repo=repo,
            state=state,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"Error listing GitHub PRs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/github/pull-requests/create")
async def create_github_pull_request(request: GitHubCreatePRRequest):
    """创建GitHub Pull Request"""
    try:
        logger.info(f"Creating GitHub PR: {request.title}")
        result = await github_service.create_pull_request(
            title=request.title,
            body=request.body,
            head=request.head,
            base=request.base,
            owner=request.owner,
            repo=request.repo
        )
        return result
    except Exception as e:
        logger.error(f"Error creating GitHub PR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/commits")
async def get_github_commits(
    owner: Optional[str] = Query(None, description="仓库所有者"),
    repo: Optional[str] = Query(None, description="仓库名称"),
    limit: int = Query(20, ge=1, le=100, description="返回数量")
):
    """获取GitHub提交记录"""
    try:
        logger.info(f"Getting GitHub commits for {owner}/{repo}")
        result = await github_service.get_commits(
            owner=owner,
            repo=repo,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"Error getting GitHub commits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/github/webhook")
async def handle_github_webhook(
    request: Request,
    x_github_event: str = Header(None, description="GitHub事件类型"),
    x_hub_signature_256: str = Header(None, description="Webhook签名")
):
    """处理GitHub Webhook事件"""
    try:
        payload = await request.json()

        # 验证签名
        if x_hub_signature_256:
            signature_valid = await github_service.verify_webhook_signature(
                payload=await request.body(),
                signature=x_hub_signature_256
            )
            if not signature_valid:
                logger.warning("Invalid GitHub webhook signature")
                raise HTTPException(status_code=401, detail="Invalid signature")

        # 处理事件
        result = await github_service.handle_webhook(
            payload=payload,
            event_type=x_github_event or "unknown"
        )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling GitHub webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))