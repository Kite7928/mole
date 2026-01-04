from celery import Task
from datetime import datetime, timedelta
from ..celery_app import celery_app
from ..services.logging_service import logging_service
from ..core.database import get_db
from ..core.logger import logger


class DatabaseTask(Task):
    """Base task with database session."""
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_db().__anext__()
        return self._db


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.maintenance_tasks.cleanup_old_logs")
def cleanup_old_logs(self, days: int = 30):
    """Clean up old task logs."""
    logger.info(f"Starting cleanup_old_logs task (keep {days} days)")

    try:
        # Create task
        task = logging_service.create_task(
            task_type="maintenance",
            task_name=f"Clean up old logs (keep {days} days)",
            db=self.db
        )

        # Update status
        logging_service.update_task_status(
            task.id,
            "running",
            progress=50,
            db=self.db
        )

        # Clean up logs
        deleted_count = logging_service.cleanup_old_logs(days=days, db=self.db)

        # Mark as complete
        logging_service.update_task_status(
            task.id,
            "success",
            progress=100,
            result={"deleted_count": deleted_count},
            db=self.db
        )

        logger.info(f"cleanup_old_logs task completed: {deleted_count} logs deleted")
        return {"deleted_count": deleted_count}

    except Exception as e:
        logger.error(f"Error in cleanup_old_logs task: {str(e)}")
        logging_service.update_task_status(
            task.id,
            "failed",
            error_message=str(e),
            db=self.db
        )
        raise


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.maintenance_tasks.health_check")
def health_check(self):
    """Perform system health check."""
    logger.info("Starting health_check task")

    try:
        # Create task
        task = logging_service.create_task(
            task_type="maintenance",
            task_name="System health check",
            db=self.db
        )

        # Update status
        logging_service.update_task_status(
            task.id,
            "running",
            progress=50,
            db=self.db
        )

        # Check database connection
        try:
            await self.db.execute("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"

        # Check Redis connection
        redis_status = "healthy"  # TODO: Implement actual Redis check

        # Get task statistics
        stats = logging_service.get_task_statistics(db=self.db)

        # Mark as complete
        logging_service.update_task_status(
            task.id,
            "success",
            progress=100,
            result={
                "database": db_status,
                "redis": redis_status,
                "statistics": stats
            },
            db=self.db
        )

        logger.info("health_check task completed")
        return {
            "database": db_status,
            "redis": redis_status,
            "statistics": stats
        }

    except Exception as e:
        logger.error(f"Error in health_check task: {str(e)}")
        logging_service.update_task_status(
            task.id,
            "failed",
            error_message=str(e),
            db=self.db
        )
        raise