from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Enum, Boolean
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class NewsSource(str, enum.Enum):
    ITHOME = "ithome"       # IT之家
    BAIDU = "baidu"         # 百度资讯
    OTHER = "other"         # 其他


class NewsItem(Base):
    """热点新闻模型"""
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    url = Column(String(1000), nullable=False, unique=True, index=True)

    # 来源信息
    source = Column(Enum(NewsSource), nullable=False, index=True)
    source_name = Column(String(100), nullable=True)  # 来源名称

    # 热度指标
    hot_score = Column(Float, default=0.0, index=True)  # 热度分数

    # 封面图
    cover_image_url = Column(String(1000), nullable=True)

    # 时间信息
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # 处理状态
    is_used = Column(Boolean, default=False)  # 是否已使用

    def __repr__(self):
        return f"<NewsItem(id={self.id}, title='{self.title}', source='{self.source}')>"