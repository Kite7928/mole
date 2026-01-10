from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, enum.Enum):
    ARTICLE_GENERATION = "article_generation"
    IMAGE_GENERATION = "image_generation"
    NEWS_FETCH = "news_fetch"
    WECHAT_PUBLISH = "wechat_publish"
    DATA_SYNC = "data_sync"


class Task(Base):
    """
    Task model for tracking async operations.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), unique=True, nullable=False, index=True)  # Celery task ID
    task_type = Column(Enum(TaskType), nullable=False, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, index=True)

    # Task description and parameters
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)

    # Task result
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)

    # Progress tracking
    progress = Column(Integer, default=0)  # 0-100
    current_step = Column(String(200), nullable=True)
    total_steps = Column(Integer, nullable=True)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in seconds

    # Retry information
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Priority and scheduling
    priority = Column(Integer, default=5)  # 1-10, higher is more important
    scheduled_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="tasks")
    article = relationship("Article", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, task_id='{self.task_id}', type='{self.task_type}', status='{self.status}')>"


class ScheduledTask(Base):
    """
    Scheduled task model for recurring operations.
    """
    __tablename__ = "scheduled_tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Schedule configuration
    task_type = Column(Enum(TaskType), nullable=False)
    cron_expression = Column(String(100), nullable=False)  # e.g., "0 */2 * * *" for every 2 hours
    interval_seconds = Column(Integer, nullable=True)  # Alternative to cron

    # Task parameters
    parameters = Column(JSON, nullable=True)

    # Execution settings
    is_active = Column(Boolean, default=True)
    run_immediately = Column(Boolean, default=False)
    timezone = Column(String(50), default="Asia/Shanghai")

    # Statistics
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<ScheduledTask(id={self.id}, name='{self.name}', cron='{self.cron_expression}')>"