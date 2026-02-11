"""
异步任务队列服务 - 替代Celery的轻量级方案
使用asyncio.Queue实现
"""

import asyncio
import uuid
import time
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.logger import logger


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """异步任务"""
    id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    progress: int = 0  # 0-100
    progress_message: str = ""
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "progress": self.progress,
            "progress_message": self.progress_message,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration": (
                (self.completed_at or time.time()) - 
                (self.started_at or self.created_at)
            ) if self.started_at else None
        }


class AsyncTaskQueue:
    """异步任务队列管理器"""
    
    def __init__(self, max_workers: int = 3, max_size: int = 100):
        """
        初始化任务队列
        
        Args:
            max_workers: 最大并发工作线程数
            max_size: 队列最大容量
        """
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self.tasks: Dict[str, Task] = {}
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}  # 定时任务
        self.max_workers = max_workers
        self._workers: List[asyncio.Task] = []
        self._scheduler: Optional[asyncio.Task] = None
        self._running = False
        self._lock = asyncio.Lock()
        
    async def start(self):
        """启动任务队列处理器"""
        if self._running:
            return
        
        self._running = True
        self._workers = [
            asyncio.create_task(self._worker_loop(f"worker-{i}"))
            for i in range(self.max_workers)
        ]
        
        # 启动定时任务调度器
        self._scheduler = asyncio.create_task(self._scheduler_loop())
        
        logger.info(f"异步任务队列已启动，{self.max_workers} 个工作线程")
    
    async def stop(self):
        """停止任务队列处理器"""
        if not self._running:
            return
        
        self._running = False
        
        # 取消所有工作线程
        for worker in self._workers:
            worker.cancel()
        
        # 取消调度器
        if self._scheduler:
            self._scheduler.cancel()
        
        # 等待所有工作线程结束
        await asyncio.gather(*self._workers, return_exceptions=True)
        if self._scheduler:
            await asyncio.gather(self._scheduler, return_exceptions=True)
        
        self._workers = []
        self._scheduler = None
        
        logger.info("异步任务队列已停止")
    
    async def _worker_loop(self, worker_name: str):
        """工作线程循环"""
        while self._running:
            try:
                # 从队列获取任务
                task = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=1.0
                )
                
                # 执行任务
                await self._execute_task(task)
                
                # 标记任务完成
                self.queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"{worker_name} 处理任务时出错: {e}")
    
    async def _scheduler_loop(self):
        """定时任务调度器循环"""
        logger.info("定时任务调度器已启动")
        
        while self._running:
            try:
                current_time = time.time()
                
                async with self._lock:
                    # 检查是否有到期的定时任务
                    ready_tasks = []
                    for task_id, task_info in list(self.scheduled_tasks.items()):
                        scheduled_time = task_info.get('scheduled_at', 0)
                        
                        if current_time >= scheduled_time:
                            ready_tasks.append((task_id, task_info))
                            # 从定时任务列表中移除
                            del self.scheduled_tasks[task_id]
                
                # 执行到期的定时任务
                for task_id, task_info in ready_tasks:
                    try:
                        logger.info(f"执行定时任务: {task_id}")
                        
                        # 创建任务对象
                        task = Task(
                            id=task_id,
                            name=task_info['name'],
                            func=task_info['func'],
                            args=task_info.get('args', ()),
                            kwargs=task_info.get('kwargs', {})
                        )
                        
                        # 保存任务
                        async with self._lock:
                            self.tasks[task_id] = task
                        
                        # 提交到队列
                        await self.queue.put(task)
                        
                    except Exception as e:
                        logger.error(f"定时任务 {task_id} 执行失败: {e}")
                
                # 等待1秒后再次检查
                await asyncio.sleep(1.0)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"调度器循环出错: {e}")
                await asyncio.sleep(1.0)
        
        logger.info("定时任务调度器已停止")
    
    async def _execute_task(self, task: Task):
        """执行单个任务"""
        async with self._lock:
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
        
        try:
            # 更新进度回调
            async def update_progress(progress: int, message: str = ""):
                task.progress = progress
                task.progress_message = message
                logger.debug(f"任务 {task.id} 进度: {progress}% - {message}")
            
            # 注入进度回调函数
            if 'update_progress' not in task.kwargs:
                task.kwargs['update_progress'] = update_progress
            
            # 执行函数
            if asyncio.iscoroutinefunction(task.func):
                result = await task.func(*task.args, **task.kwargs)
            else:
                result = task.func(*task.args, **task.kwargs)
            
            async with self._lock:
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.progress = 100
                task.completed_at = time.time()
            
            logger.info(f"任务 {task.id} ({task.name}) 完成")
            
        except Exception as e:
            async with self._lock:
                task.error = str(e)
                task.status = TaskStatus.FAILED
                task.completed_at = time.time()
            
            logger.error(f"任务 {task.id} ({task.name}) 失败: {e}")
    
    async def submit(
        self,
        name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> str:
        """
        提交任务到队列
        
        Args:
            name: 任务名称
            func: 任务函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs
        )
        
        async with self._lock:
            self.tasks[task_id] = task
        
        await self.queue.put(task)
        logger.info(f"任务 {task_id} ({name}) 已提交到队列")
        
        return task_id
    
    async def add_task(
        self,
        task_id: str,
        task_type: str,
        params: Dict[str, Any],
        scheduled_at: Optional[float] = None
    ) -> str:
        """
        添加定时任务
        
        Args:
            task_id: 任务ID
            task_type: 任务类型
            params: 任务参数
            scheduled_at: 计划执行时间（时间戳）
            
        Returns:
            任务ID
        """
        # 如果没有指定计划时间，立即执行
        if scheduled_at is None:
            scheduled_at = time.time()
        
        # 检查是否为定时任务
        if scheduled_at > time.time():
            # 定时任务
            async with self._lock:
                self.scheduled_tasks[task_id] = {
                    'name': task_type,
                    'func': self._execute_task_by_type,
                    'args': (),
                    'kwargs': {
                        'task_type': task_type,
                        'params': params
                    },
                    'scheduled_at': scheduled_at
                }
            
            logger.info(f"定时任务 {task_id} 已添加，计划执行时间: {scheduled_at}")
        else:
            # 立即执行
            await self.submit(
                name=task_type,
                func=self._execute_task_by_type,
                task_type=task_type,
                params=params
            )
            logger.info(f"任务 {task_id} 已立即执行")
        
        return task_id
    
    async def _execute_task_by_type(
        self,
        task_type: str,
        params: Dict[str, Any],
        update_progress: Optional[Callable] = None
    ):
        """根据任务类型执行任务"""
        if task_type == "publish":
            # 多平台发布任务
            await self._execute_publish_task(params, update_progress)
        else:
            logger.warning(f"未知的任务类型: {task_type}")
    
    async def _execute_publish_task(
        self,
        params: Dict[str, Any],
        update_progress: Optional[Callable] = None
    ):
        """执行发布任务"""
        try:
            from .multiplatform_service import multiplatform_publisher
            from ..types import ArticleContent
            from sqlalchemy.ext.asyncio import AsyncSession
            from ..core.database import get_db_session
            
            # 获取参数
            platforms_str = params.get('platforms', [])
            article_id = params.get('article_id')
            article_data = params.get('article_data', {})
            
            if update_progress:
                await update_progress(10, "准备发布...")
            
            # 转换平台类型
            from ..models.publish_platform import PlatformType
            platforms = [PlatformType(p) for p in platforms_str]
            
            # 获取数据库会话
            async with get_db_session() as db:
                # 查询文章
                from ..models.article import Article
                from sqlalchemy import select
                query = select(Article).where(Article.id == article_id)
                result = await db.execute(query)
                article = result.scalar_one_or_none()
                
                if not article:
                    logger.error(f"文章不存在: {article_id}")
                    return
                
                # 准备内容
                article_content = ArticleContent(
                    title=article_data.get('title', article.title),
                    content=article_data.get('content', article.content),
                    summary=article_data.get('summary', article.summary),
                    cover_image=article_data.get('cover_image', article.cover_image_url),
                    tags=article_data.get('tags'),
                    category=article_data.get('category'),
                )
                
                if update_progress:
                    await update_progress(30, "开始发布到平台...")
                
                # 发布到平台
                results = await multiplatform_publisher.publish_to_multiple_platforms(
                    platforms=platforms,
                    article=article_content,
                    article_id=article_id,
                    db=db
                )
                
                if update_progress:
                    await update_progress(100, "发布完成！")
                
                success_count = sum(1 for r in results.values() if r.success)
                logger.info(f"定时发布完成: 成功 {success_count}/{len(platforms)}")
            
        except Exception as e:
            logger.error(f"执行发布任务失败: {e}")
            raise
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务信息"""
        async with self._lock:
            return self.tasks.get(task_id)
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = await self.get_task(task_id)
        if task:
            return task.to_dict()
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务（仅对pending状态有效）"""
        async with self._lock:
            task = self.tasks.get(task_id)
            if task and task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                return True
            return False
    
    async def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """列出任务"""
        async with self._lock:
            tasks = list(self.tasks.values())
            
            if status:
                tasks = [t for t in tasks if t.status == status]
            
            # 按创建时间倒序
            tasks.sort(key=lambda t: t.created_at, reverse=True)
            
            return [t.to_dict() for t in tasks[:limit]]
    
    async def clean_old_tasks(self, max_age: int = 86400):
        """清理旧任务（默认保留24小时）"""
        current_time = time.time()
        removed_count = 0
        
        async with self._lock:
            old_ids = [
                task_id for task_id, task in self.tasks.items()
                if task.completed_at and 
                (current_time - task.completed_at) > max_age
            ]
            
            for task_id in old_ids:
                del self.tasks[task_id]
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"清理了 {removed_count} 个旧任务")
        
        return removed_count
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        async with self._lock:
            total = len(self.tasks)
            pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
            running = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
            completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
            failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
            scheduled = len(self.scheduled_tasks)
            
            return {
                "total_tasks": total,
                "pending": pending,
                "running": running,
                "completed": completed,
                "failed": failed,
                "scheduled": scheduled,
                "queue_size": self.queue.qsize(),
                "max_workers": self.max_workers,
                "active_workers": len(self._workers)
            }


# 全局任务队列实例
task_queue = AsyncTaskQueue(max_workers=3, max_size=100)


# 常用任务函数示例
async def generate_article_task(
    topic: str,
    title: Optional[str] = None,
    style: str = "professional",
    update_progress: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    生成文章任务
    
    这是一个示例任务函数，展示如何使用进度回调
    """
    from .unified_ai_service import unified_ai_service
    
    result = {
        "topic": topic,
        "title": title,
        "content": "",
        "status": "generating"
    }
    
    try:
        # 步骤1: 如果没有标题，先生成标题
        if not title:
            if update_progress:
                await update_progress(10, "正在生成标题...")
            
            messages = [
                {"role": "system", "content": "你是一个专业的公众号标题创作专家。"},
                {"role": "user", "content": f"请为主题'{topic}'生成一个吸引人的标题（15-25字）"}
            ]
            
            response = await unified_ai_service.generate(messages, max_tokens=100)
            title = response.content.strip()
            result["title"] = title
        
        # 步骤2: 生成大纲
        if update_progress:
            await update_progress(30, "正在生成文章大纲...")
        
        await asyncio.sleep(0.5)  # 模拟处理时间
        
        # 步骤3: 生成正文
        if update_progress:
            await update_progress(50, "正在撰写正文...")
        
        messages = [
            {"role": "system", "content": "你是一个专业的科技内容创作者。"},
            {"role": "user", "content": f"请为标题'{title}'撰写一篇公众号文章，主题：{topic}"}
        ]
        
        response = await unified_ai_service.generate(messages, max_tokens=4000)
        result["content"] = response.content
        
        if update_progress:
            await update_progress(90, "正在优化内容...")
        
        # 步骤4: SEO优化等后处理
        await asyncio.sleep(0.3)
        
        result["status"] = "completed"
        result["word_count"] = len(response.content)
        
        if update_progress:
            await update_progress(100, "生成完成！")
        
        return result
        
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        raise


async def initialize_task_queue():
    """初始化任务队列"""
    await task_queue.start()


async def close_task_queue():
    """关闭任务队列"""
    await task_queue.stop()


async def get_db_session() -> AsyncSession:
    """获取数据库会话"""
    from ..core.database import async_session_maker
    return async_session_maker()