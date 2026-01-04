from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from ..core.database import get_db
from ..core.logger import logger
from ..models.task import Task, TaskStatus, TaskLog


class LoggingService:
    """
    Logging and monitoring service for tasks and operations.
    """

    async def create_task(
        self,
        task_type: str,
        task_name: str,
        config: Optional[Dict[str, Any]] = None,
        db: AsyncSession = Depends(get_db)
    ) -> Task:
        """
        Create a new task.

        Args:
            task_type: Type of task
            task_name: Name of the task
            config: Task configuration
            db: Database session

        Returns:
            Created Task object
        """
        try:
            task = Task(
                task_type=task_type,
                task_name=task_name,
                status=TaskStatus.PENDING,
                config=config or {},
                progress=0,
                created_at=datetime.utcnow()
            )

            db.add(task)
            await db.commit()
            await db.refresh(task)

            logger.info(f"Task created: {task.id} - {task_name}")
            return task

        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            await db.rollback()
            raise

    async def update_task_status(
        self,
        task_id: int,
        status: TaskStatus,
        progress: Optional[int] = None,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        db: AsyncSession = Depends(get_db)
    ) -> Task:
        """
        Update task status.

        Args:
            task_id: Task ID
            status: New status
            progress: Progress percentage (0-100)
            result: Task result
            error_message: Error message if failed
            db: Database session

        Returns:
            Updated Task object
        """
        try:
            result_obj = await db.execute(select(Task).where(Task.id == task_id))
            task = result_obj.scalar_one_or_none()

            if not task:
                raise ValueError(f"Task not found: {task_id}")

            task.status = status
            task.updated_at = datetime.utcnow()

            if progress is not None:
                task.progress = progress

            if result is not None:
                task.result = result

            if error_message is not None:
                task.error_message = error_message

            if status == TaskStatus.SUCCESS:
                task.completed_at = datetime.utcnow()

            await db.commit()
            await db.refresh(task)

            logger.info(f"Task updated: {task_id} - {status.value}")
            return task

        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            await db.rollback()
            raise

    async def add_task_log(
        self,
        task_id: int,
        level: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        db: AsyncSession = Depends(get_db)
    ) -> TaskLog:
        """
        Add a log entry to a task.

        Args:
            task_id: Task ID
            level: Log level (info, warning, error)
            message: Log message
            metadata: Additional metadata
            db: Database session

        Returns:
            Created TaskLog object
        """
        try:
            log = TaskLog(
                task_id=task_id,
                level=level,
                message=message,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )

            db.add(log)
            await db.commit()
            await db.refresh(log)

            return log

        except Exception as e:
            logger.error(f"Error adding task log: {str(e)}")
            await db.rollback()
            raise

    async def get_task_logs(
        self,
        task_id: int,
        db: AsyncSession = Depends(get_db)
    ) -> List[TaskLog]:
        """
        Get all logs for a task.

        Args:
            task_id: Task ID
            db: Database session

        Returns:
            List of TaskLog objects
        """
        try:
            result = await db.execute(
                select(TaskLog)
                .where(TaskLog.task_id == task_id)
                .order_by(TaskLog.created_at.asc())
            )
            logs = result.scalars().all()

            return list(logs)

        except Exception as e:
            logger.error(f"Error getting task logs: {str(e)}")
            return []

    async def get_recent_tasks(
        self,
        limit: int = 10,
        status: Optional[TaskStatus] = None,
        db: AsyncSession = Depends(get_db)
    ) -> List[Task]:
        """
        Get recent tasks.

        Args:
            limit: Maximum number of tasks to return
            status: Optional status filter
            db: Database session

        Returns:
            List of Task objects
        """
        try:
            query = select(Task)

            if status:
                query = query.where(Task.status == status)

            query = query.order_by(desc(Task.created_at)).limit(limit)

            result = await db.execute(query)
            tasks = result.scalars().all()

            return list(tasks)

        except Exception as e:
            logger.error(f"Error getting recent tasks: {str(e)}")
            return []

    async def get_task_statistics(
        self,
        db: AsyncSession = Depends(get_db)
    ) -> Dict[str, Any]:
        """
        Get task statistics.

        Args:
            db: Database session

        Returns:
            Dictionary with statistics
        """
        try:
            # Count tasks by status
            result = await db.execute(
                select(Task.status, func.count(Task.id))
                .group_by(Task.status)
            )

            status_counts = {}
            for row in result:
                status_counts[row[0].value] = row[1]

            # Get total tasks
            total_result = await db.execute(select(func.count(Task.id)))
            total_tasks = total_result.scalar() or 0

            # Get success rate
            success_count = status_counts.get('success', 0)
            success_rate = (success_count / total_tasks * 100) if total_tasks > 0 else 0

            # Get average completion time
            completed_tasks = await db.execute(
                select(Task)
                .where(Task.status == TaskStatus.SUCCESS)
                .where(Task.completed_at.isnot(None()))
            )

            avg_completion_time = 0
            completed_list = completed_tasks.scalars().all()
            if completed_list:
                total_time = sum(
                    (task.completed_at - task.created_at).total_seconds()
                    for task in completed_list
                )
                avg_completion_time = total_time / len(completed_list)

            return {
                "total_tasks": total_tasks,
                "status_counts": status_counts,
                "success_rate": round(success_rate, 2),
                "avg_completion_time": round(avg_completion_time, 2),
            }

        except Exception as e:
            logger.error(f"Error getting task statistics: {str(e)}")
            return {}

    async def cleanup_old_logs(
        self,
        days: int = 30,
        db: AsyncSession = Depends(get_db)
    ) -> int:
        """
        Clean up old logs.

        Args:
            days: Number of days to keep
            db: Database session

        Returns:
            Number of logs deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            result = await db.execute(
                delete(TaskLog)
                .where(TaskLog.created_at < cutoff_date)
            )

            deleted_count = result.rowcount
            await db.commit()

            logger.info(f"Deleted {deleted_count} old logs")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up old logs: {str(e)}")
            await db.rollback()
            return 0


# Global instance
logging_service = LoggingService()