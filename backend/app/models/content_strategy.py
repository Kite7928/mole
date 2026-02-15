"""
内容策略模型
包含发布计划、系列文章、选题库等数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Index, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class ScheduleStatus(str, enum.Enum):
    """发布计划状态"""
    DRAFT = "draft"           # 草稿
    SCHEDULED = "scheduled"   # 已排期
    PUBLISHED = "published"   # 已发布
    CANCELLED = "cancelled"   # 已取消


class PublishPlatform(str, enum.Enum):
    """发布平台"""
    WECHAT = "wechat"         # 微信公众号
    WEIBO = "weibo"           # 微博
    ZHIHU = "zhihu"           # 知乎
    XIAOHONGSHU = "xiaohongshu"  # 小红书
    DOUYIN = "douyin"         # 抖音
    BILIBILI = "bilibili"     # B站
    MULTI = "multi"           # 多平台


class SeriesStatus(str, enum.Enum):
    """系列文章状态"""
    DRAFT = "draft"           # 草稿/策划中
    ONGOING = "ongoing"       # 连载中
    COMPLETED = "completed"   # 已完成
    PAUSED = "paused"         # 暂停


class IdeaStatus(str, enum.Enum):
    """选题状态"""
    NEW = "new"               # 新想法
    EVALUATING = "evaluating" # 评估中
    APPROVED = "approved"     # 已采纳
    IN_PROGRESS = "in_progress"  # 创作中
    PUBLISHED = "published"   # 已发布
    ARCHIVED = "archived"     # 已归档


class IdeaPriority(str, enum.Enum):
    """选题优先级"""
    HIGH = "high"             # 高
    MEDIUM = "medium"         # 中
    LOW = "low"               # 低


class PublishSchedule(Base):
    """发布计划表"""
    __tablename__ = "publish_schedules"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=True)
    title = Column(String(500), nullable=False)  # 计划标题（关联文章前使用）
    description = Column(Text, nullable=True)    # 计划描述
    
    # 发布时间
    scheduled_date = Column(DateTime, nullable=False, index=True)
    scheduled_time = Column(String(10), default="08:00")  # 时间 HH:MM
    
    # 状态与平台
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.DRAFT, index=True)
    platform = Column(Enum(PublishPlatform), default=PublishPlatform.WECHAT)
    
    # 关联文章
    article = relationship("Article", back_populates="schedules")
    
    # 提醒设置
    remind_before = Column(Integer, default=30)  # 提前提醒分钟数
    is_reminded = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 索引
    __table_args__ = (
        Index('ix_schedules_date_status', 'scheduled_date', 'status'),
        Index('ix_schedules_article', 'article_id'),
    )


class ArticleSeries(Base):
    """系列文章表"""
    __tablename__ = "article_series"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)  # 系列名称
    description = Column(Text, nullable=True)               # 系列描述
    cover_image_url = Column(String(1000), nullable=True)   # 封面图
    
    # 系列状态
    status = Column(Enum(SeriesStatus), default=SeriesStatus.DRAFT)
    
    # 文章排序（以逗号分隔的文章ID列表）
    article_order = Column(String(2000), default="")
    
    # 标签
    tags = Column(String(500), nullable=True)
    
    # 分类
    category = Column(String(100), nullable=True)
    
    # 统计
    total_articles = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def get_article_order_list(self) -> list:
        """获取文章顺序列表"""
        if not self.article_order:
            return []
        return [int(id.strip()) for id in self.article_order.split(',') if id.strip().isdigit()]
    
    def set_article_order_list(self, article_ids: list):
        """设置文章顺序"""
        self.article_order = ','.join(str(id) for id in article_ids)
        self.total_articles = len(article_ids)
    
    def get_tags_list(self) -> list:
        """获取标签列表"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def set_tags_list(self, tags: list):
        """设置标签"""
        self.tags = ','.join(tags) if tags else None
    
    # 关联关系
    articles = relationship("Article", back_populates="series")


class TopicIdea(Base):
    """选题库表 - 创作灵感/选题"""
    __tablename__ = "topic_ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)  # 选题标题
    description = Column(Text, nullable=True)                # 详细描述
    
    # 状态与优先级
    status = Column(Enum(IdeaStatus), default=IdeaStatus.NEW, index=True)
    priority = Column(Enum(IdeaPriority), default=IdeaPriority.MEDIUM)
    
    # 来源信息
    source = Column(String(200), nullable=True)      # 来源（如：热点新闻、用户反馈等）
    source_url = Column(String(1000), nullable=True) # 来源链接
    
    # 标签与分类
    tags = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)
    
    # 预估与规划
    estimated_word_count = Column(Integer, nullable=True)  # 预估字数
    target_publish_date = Column(DateTime, nullable=True)  # 目标发布日期
    
    # 关联
    related_article_id = Column(Integer, ForeignKey("articles.id"), nullable=True)
    series_id = Column(Integer, ForeignKey("article_series.id"), nullable=True)
    
    # 备注
    notes = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 索引
    __table_args__ = (
        Index('ix_ideas_status_priority', 'status', 'priority'),
        Index('ix_ideas_category', 'category'),
    )
    
    def get_tags_list(self) -> list:
        """获取标签列表"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def set_tags_list(self, tags: list):
        """设置标签"""
        self.tags = ','.join(tags) if tags else None


class ContentCalendarEvent(Base):
    """内容日历事件表 - 用于日历视图展示"""
    __tablename__ = "content_calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # schedule, idea, series
    reference_id = Column(Integer, nullable=False)  # 关联的ID
    
    # 事件信息
    title = Column(String(500), nullable=False)
    event_date = Column(DateTime, nullable=False, index=True)
    color = Column(String(20), default="#8b5cf6")  # 事件颜色
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    
    # 索引
    __table_args__ = (
        Index('ix_calendar_date_type', 'event_date', 'event_type'),
    )
