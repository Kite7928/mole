from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from ..core.database import get_db
from ..core.logger import logger
from ..models.task import Task, TaskStatus, TaskType

router = APIRouter()


# Pydantic models
class TaskCreateRequest(BaseModel):
    task_type: TaskType = Field(..., description="Task type")
    name: str = Field(..., description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    parameters: Optional[dict] = Field(None, description="Task parameters")
    priority: int = Field(5, ge=1, le=10, description="Task priority")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled execution time")


class TaskResponse(BaseModel):
    id: int
    task_id: str
    task_type: TaskType
    status: TaskStatus
    name: str
    description: Optional[str]
    progress: int
    current_step: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[dict]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Endpoints
@router.post("/", response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    try:
        logger.info(f"Creating task: {request.name}")

        # Generate unique task ID
        import uuid
        task_id = str(uuid.uuid4())

        # Create task record
        task = Task(
            task_id=task_id,
            task_type=request.task_type,
            name=request.name,
            description=request.description,
            parameters=request.parameters,
            priority=request.priority,
            scheduled_at=request.scheduled_at,
            status=TaskStatus.PENDING
        )

        db.add(task)
        await db.commit()
        await db.refresh(task)

        # Execute task in background
        if not request.scheduled_at or request.scheduled_at <= datetime.utcnow():
            background_tasks.add_task(execute_task, task.id, request.parameters)

        return task

    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[TaskStatus] = None,
    task_type: Optional[TaskType] = None,
    db: AsyncSession = Depends(get_db)
):
    """List tasks with filters."""
    try:
        query = select(Task)

        if status:
            query = query.where(Task.status == status)

        if task_type:
            query = query.where(Task.task_type == task_type)

        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        tasks = result.scalars().all()

        return tasks

    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get task by ID."""
    try:
        result = await db.execute(select(Task).where(Task.task_id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a running task."""
    try:
        result = await db.execute(select(Task).where(Task.task_id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            raise HTTPException(status_code=400, detail="Task cannot be cancelled")

        task.status = TaskStatus.CANCELLED
        await db.commit()

        return {"message": "Task cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/running/count")
async def get_running_tasks_count(db: AsyncSession = Depends(get_db)):
    """Get count of currently running tasks."""
    try:
        result = await db.execute(
            select(func.count(Task.id)).where(Task.status == TaskStatus.RUNNING)
        )
        count = result.scalar()

        return {"count": count}

    except Exception as e:
        logger.error(f"Error getting running tasks count: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Task execution function
async def execute_task(task_id: int, parameters: dict):
    """
    Execute a task in the background.

    This is a placeholder implementation. In production, you would:
    1. Use Celery for distributed task execution
    2. Implement proper error handling and retry logic
    3. Update task progress in real-time
    4. Handle different task types appropriately
    """
    from ..core.database import async_session_maker

    async with async_session_maker() as db:
        try:
            # Get task
            result = await db.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()

            if not task:
                logger.error(f"Task not found: {task_id}")
                return

            # Update task status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            await db.commit()

            logger.info(f"Executing task: {task.name} (ID: {task_id})")

            # Simulate task execution
            # TODO: Implement actual task logic based on task_type
            await asyncio.sleep(2)

            # Update progress
            task.progress = 50
            task.current_step = "Processing..."
            await db.commit()

            # Continue execution
            await asyncio.sleep(2)

            # Mark as complete
            task.status = TaskStatus.SUCCESS
            task.progress = 100
            task.completed_at = datetime.utcnow()
            task.result = {"message": "Task completed successfully"}
            await db.commit()

            logger.info(f"Task completed: {task.name} (ID: {task_id})")

        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")

            # Update task with error
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            await db.commit()

import asyncio