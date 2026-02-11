"""
定时任务数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum
from datetime import datetime
from enum import Enum
import json
from ..core.database import Base


class TaskType(str, Enum):
    """任务类型"""
    GENERATE_ARTICLE = "generate_article"
    PUBLISH_ARTICLE = "publish_article"
    REFRESH_HOTSPOTS = "refresh_hotspots"
    BATCH_GENERATE = "batch_generate"
    BATCH_PUBLISH = "batch_publish"


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(Base):
    """定时任务模型"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="任务名称")
    description = Column(Text, nullable=True, comment="任务描述")
    task_type = Column(SQLEnum(TaskType), nullable=False, comment="任务类型")
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, comment="任务状态")

    # 任务配置
    config = Column(Text, nullable=True, comment="任务配置（JSON格式）")
    schedule_time = Column(DateTime, nullable=True, comment="计划执行时间")
    cron_expression = Column(String(100), nullable=True, comment="Cron表达式")

    # 执行结果
    result = Column(Text, nullable=True, comment="执行结果（JSON格式）")
    error_message = Column(Text, nullable=True, comment="错误信息")
    retry_count = Column(Integer, default=0, comment="重试次数")
    max_retries = Column(Integer, default=3, comment="最大重试次数")

    # 关联数据
    article_id = Column(Integer, nullable=True, comment="关联文章ID")
    batch_id = Column(Integer, nullable=True, comment="关联批量任务ID")

    # 执行统计
    total_runs = Column(Integer, default=0, comment="总执行次数")
    success_runs = Column(Integer, default=0, comment="成功次数")
    failed_runs = Column(Integer, default=0, comment="失败次数")
    last_run_at = Column(DateTime, nullable=True, comment="最后执行时间")
    next_run_at = Column(DateTime, nullable=True, comment="下次执行时间")

    # 控制
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    is_recurring = Column(Boolean, default=False, comment="是否循环执行")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type.value if self.task_type else None,
            "status": self.status.value if self.status else None,
            "config": json.loads(self.config) if self.config else None,
            "schedule_time": self.schedule_time.isoformat() if self.schedule_time else None,
            "cron_expression": self.cron_expression,
            "result": json.loads(self.result) if self.result else None,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "article_id": self.article_id,
            "batch_id": self.batch_id,
            "total_runs": self.total_runs,
            "success_runs": self.success_runs,
            "failed_runs": self.failed_runs,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "is_enabled": self.is_enabled,
            "is_recurring": self.is_recurring,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }