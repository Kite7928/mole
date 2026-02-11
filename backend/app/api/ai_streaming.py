"""
AI流式生成API - 支持SSE(Server-Sent Events)
提供实时流式输出和异步任务管理
"""

import json
import asyncio
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.database import get_db
from ..core.logger import logger
from ..models.config import AppConfig
from ..models.article import Article
from ..services.unified_ai_service import unified_ai_service
from ..services.async_task_queue import task_queue, generate_article_task, TaskStatus
from ..services.providers import AIProvider

router = APIRouter()


# ==================== 请求模型 ====================

class StreamGenerateRequest(BaseModel):
    """流式生成请求"""
    topic: str = Field(..., description="写作主题", min_length=1, max_length=500)
    title: Optional[str] = Field(None, description="文章标题（可选）")
    style: str = Field(default="professional", description="写作风格")
    provider: Optional[str] = Field(None, description="AI提供商")
    model: Optional[str] = Field(None, description="模型名称")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, ge=100, le=8000)


class AsyncGenerateRequest(BaseModel):
    """异步生成请求"""
    topic: str = Field(..., description="写作主题", min_length=1, max_length=500)
    title: Optional[str] = Field(None, description="文章标题（可选）")
    style: str = Field(default="professional", description="写作风格")
    provider: Optional[str] = Field(None, description="AI提供商")
    model: Optional[str] = Field(None, description="模型名称")
    auto_save: bool = Field(default=True, description="是否自动保存到数据库")


class StreamChatRequest(BaseModel):
    """流式对话请求"""
    messages: List[Dict[str, str]] = Field(..., description="消息列表")
    provider: Optional[str] = Field(None, description="AI提供商")
    model: Optional[str] = Field(None, description="模型名称")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, ge=100, le=8000)


# ==================== 辅助函数 ====================

async def get_config(db: AsyncSession) -> AppConfig:
    """获取系统配置"""
    query = select(AppConfig).order_by(AppConfig.id.desc())
    result = await db.execute(query)
    config = result.scalar_one_or_none()
    
    if not config or not config.api_key:
        raise HTTPException(status_code=400, detail="请先在设置中配置AI API Key")
    
    return config


def format_sse(data: Dict[str, Any], event: Optional[str] = None) -> str:
    """格式化SSE消息"""
    message = ""
    if event:
        message += f"event: {event}\n"
    message += f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    return message


# ==================== API路由 ====================

@router.post("/stream-generate")
async def stream_generate(
    request: StreamGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    流式生成文章
    
    使用SSE协议实时返回生成内容，支持进度显示
    """
    config = await get_config(db)
    
    async def generate_stream():
        try:
            # 发送开始事件
            yield format_sse({
                "type": "start",
                "message": "开始生成文章..."
            }, event="start")
            
            # 步骤1: 生成标题（如果没有提供）
            title = request.title
            if not title:
                yield format_sse({
                    "type": "progress",
                    "progress": 10,
                    "message": "正在生成标题..."
                }, event="progress")
                
                messages = [
                    {"role": "system", "content": "你是一个专业的公众号标题创作专家。"},
                    {"role": "user", "content": f"请为主题'{request.topic}'生成一个吸引人的标题（15-25字），只返回标题本身，不要任何解释。"}
                ]
                
                response = await unified_ai_service.generate(
                    messages=messages,
                    provider=AIProvider(request.provider) if request.provider else None,
                    model=request.model or config.model,
                    temperature=request.temperature,
                    max_tokens=100
                )
                title = response.content.strip()
                
                yield format_sse({
                    "type": "title",
                    "title": title
                }, event="title")
            
            # 步骤2: 流式生成正文
            yield format_sse({
                "type": "progress",
                "progress": 30,
                "message": "正在撰写正文..."
            }, event="progress")
            
            style_desc = {
                "professional": "专业严谨，深度分析",
                "casual": "轻松活泼，通俗易懂",
                "humor": "幽默风趣，生动有趣"
            }.get(request.style, "专业严谨，深度分析")
            
            messages = [
                {"role": "system", "content": f"你是一个专业的科技内容创作者，写作风格：{style_desc}"},
                {"role": "user", "content": f"请为标题'{title}'撰写一篇公众号文章。\n\n主题：{request.topic}\n\n要求：\n1. 开头要有吸引人的引言\n2. 正文结构清晰，有小标题\n3. 内容要有深度和见解\n4. 结尾要有总结和展望\n5. 适合手机阅读，段落不宜过长\n6. 字数1500-2000字"}
            ]
            
            # 使用流式生成
            content_parts = []
            provider = AIProvider(request.provider) if request.provider else None
            provider_instance = unified_ai_service.providers.get(provider or unified_ai_service._get_next_provider())
            
            if not provider_instance:
                raise HTTPException(status_code=500, detail="没有可用的AI提供商")
            
            async for chunk in provider_instance.generate_stream(
                messages=messages,
                model=request.model or config.model or provider_instance.get_default_model(),
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                content_parts.append(chunk)
                yield format_sse({
                    "type": "content",
                    "chunk": chunk,
                    "content": "".join(content_parts)
                }, event="content")
            
            # 完成
            full_content = "".join(content_parts)
            
            yield format_sse({
                "type": "progress",
                "progress": 90,
                "message": "正在优化内容..."
            }, event="progress")
            
            # 简单的SEO优化
            summary = full_content[:150] + "..." if len(full_content) > 150 else full_content
            word_count = len(full_content)
            
            yield format_sse({
                "type": "complete",
                "progress": 100,
                "data": {
                    "title": title,
                    "content": full_content,
                    "summary": summary,
                    "word_count": word_count,
                    "style": request.style
                }
            }, event="complete")
            
        except Exception as e:
            logger.error(f"流式生成失败: {e}")
            yield format_sse({
                "type": "error",
                "error": str(e)
            }, event="error")
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/async-generate")
async def async_generate(
    request: AsyncGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    异步生成文章
    
    提交任务到队列，立即返回任务ID，通过任务状态接口查询进度
    """
    config = await get_config(db)
    
    # 提交异步任务
    task_id = await task_queue.submit(
        name="生成文章",
        func=generate_article_task,
        topic=request.topic,
        title=request.title,
        style=request.style
    )
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "文章生成任务已提交，请通过任务状态接口查询进度"
    }


@router.post("/stream-chat")
async def stream_chat(
    request: StreamChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    流式AI对话
    
    支持多轮对话的流式输出
    """
    config = await get_config(db)
    
    async def chat_stream():
        try:
            yield format_sse({
                "type": "start",
                "message": "开始对话..."
            }, event="start")
            
            provider = AIProvider(request.provider) if request.provider else None
            provider_instance = unified_ai_service.providers.get(provider or unified_ai_service._get_next_provider())
            
            if not provider_instance:
                raise HTTPException(status_code=500, detail="没有可用的AI提供商")
            
            content_parts = []
            async for chunk in provider_instance.generate_stream(
                messages=request.messages,
                model=request.model or config.model or provider_instance.get_default_model(),
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                content_parts.append(chunk)
                yield format_sse({
                    "type": "content",
                    "chunk": chunk,
                    "content": "".join(content_parts)
                }, event="content")
            
            yield format_sse({
                "type": "complete",
                "content": "".join(content_parts)
            }, event="complete")
            
        except Exception as e:
            logger.error(f"流式对话失败: {e}")
            yield format_sse({
                "type": "error",
                "error": str(e)
            }, event="error")
    
    return StreamingResponse(
        chat_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    获取异步任务状态
    
    查询任务进度和结果
    """
    status = await task_queue.get_task_status(task_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return status


@router.get("/tasks")
async def list_tasks(
    status: Optional[str] = Query(None, description="任务状态过滤"),
    limit: int = Query(50, ge=1, le=100)
):
    """
    列出异步任务
    
    获取最近的任务列表
    """
    task_status = TaskStatus(status) if status else None
    tasks = await task_queue.list_tasks(status=task_status, limit=limit)
    
    return {
        "tasks": tasks,
        "total": len(tasks)
    }


@router.delete("/task/{task_id}")
async def cancel_task(task_id: str):
    """
    取消异步任务
    
    只能取消pending状态的任务
    """
    success = await task_queue.cancel_task(task_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="任务不存在或无法取消（只能取消pending状态的任务）"
        )
    
    return {"message": "任务已取消", "task_id": task_id}


@router.get("/task-stats")
async def get_task_stats():
    """获取任务队列统计信息"""
    return await task_queue.get_stats()


@router.post("/auto-save-draft")
async def auto_save_draft(
    article_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    自动保存草稿
    
    前端可以定期调用此接口自动保存写作进度
    """
    try:
        article = Article(
            title=article_data.get("title", "未命名草稿"),
            content=article_data.get("content", ""),
            summary=article_data.get("summary", ""),
            status="draft",
            topic=article_data.get("topic"),
            style=article_data.get("style", "professional")
        )
        
        db.add(article)
        await db.commit()
        await db.refresh(article)
        
        return {
            "success": True,
            "article_id": article.id,
            "message": "草稿已保存"
        }
        
    except Exception as e:
        logger.error(f"自动保存失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")