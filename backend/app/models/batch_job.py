"""
批量任务数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum
from datetime import datetime
from enum import Enum
import json
from ..core.database import Base


class BatchJobType(str, Enum):
    """批量任务类型"""
    GENERATE_ARTICLES = "generate_articles"
    PUBLISH_ARTICLES = "publish_articles"


class BatchJobStatus(str, Enum):
    """批量任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class BatchJob(Base):
    """批量任务模型"""

    __tablename__ = "batch_jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="批量任务名称")
    description = Column(Text, nullable=True, comment="任务描述")
    job_type = Column(SQLEnum(BatchJobType), nullable=False, comment="批量任务类型")
    status = Column(SQLEnum(BatchJobStatus), default=BatchJobStatus.PENDING, comment="任务状态")

    # 任务配置
    config = Column(Text, nullable=True, comment="任务配置（JSON格式）")
    items = Column(Text, nullable=False, comment="任务项列表（JSON格式）")

    # 执行统计
    total_items = Column(Integer, default=0, comment="总项目数")
    completed_items = Column(Integer, default=0, comment="已完成项目数")
    failed_items = Column(Integer, default=0, comment="失败项目数")
    success_items = Column(Integer, default=0, comment="成功项目数")
    progress = Column(Integer, default=0, comment="进度（0-100）")

    # 执行结果
    result = Column(Text, nullable=True, comment="执行结果（JSON格式）")
    error_message = Column(Text, nullable=True, comment="错误信息")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "job_type": self.job_type.value if self.job_type else None,
            "status": self.status.value if self.status else None,
            "config": json.loads(self.config) if self.config else None,
            "items": json.loads(self.items) if self.items else [],
            "total_items": self.total_items,
            "completed_items": self.completed_items,
            "failed_items": self.failed_items,
            "success_items": self.success_items,
            "progress": self.progress,
            "result": json.loads(self.result) if self.result else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }