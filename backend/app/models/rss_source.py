"""RSS源数据模型"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..core.database import Base


class RssSource(Base):
    """RSS源模型"""
    __tablename__ = "rss_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)  # 源名称
    url = Column(String(1000), nullable=False, unique=True, index=True)  # RSS URL
    description = Column(String(500), nullable=True)  # 描述
    category = Column(String(100), nullable=True, index=True)  # 分类

    # 状态控制
    is_active = Column(Boolean, default=True, index=True)  # 是否启用
    is_official = Column(Boolean, default=False)  # 是否为官方源

    # 统计信息
    fetch_count = Column(Integer, default=0)  # 抓取次数
    last_fetched_at = Column(DateTime, nullable=True)  # 最后抓取时间
    last_error = Column(String(500), nullable=True)  # 最后错误信息

    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<RssSource(id={self.id}, name='{self.name}', url='{self.url}', active={self.is_active})>"