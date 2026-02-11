"""
热门话题数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from ..core.database import Base


class Hotspot(Base):
    """热门话题模型"""

    __tablename__ = "hotspots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rank = Column(Integer, nullable=False, comment="排名")
    title = Column(String(500), nullable=False, comment="话题标题")
    url = Column(String(1000), nullable=True, comment="话题链接")
    source = Column(String(50), nullable=False, comment="来源（weibo/zhihu/bilibili等）")
    category = Column(String(100), nullable=True, comment="分类")
    tags = Column(Text, nullable=True, comment="标签（JSON格式）")
    heat = Column(Integer, default=0, comment="热度值")
    heat_trend = Column(Float, default=0.0, comment="热度趋势（正数上升，负数下降）")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "rank": self.rank,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "category": self.category,
            "tags": self.tags,
            "heat": self.heat,
            "heat_trend": self.heat_trend,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }