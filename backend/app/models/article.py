from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Float, Boolean, Index
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class ArticleStatus(str, enum.Enum):
    DRAFT = "draft"           # 草稿
    GENERATING = "generating" # 生成中
    READY = "ready"           # 已完成
    PUBLISHED = "published"   # 已发布
    FAILED = "failed"         # 失败


class Article(Base):
    """文章模型"""
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    html_content = Column(Text, nullable=True)

    # 文章状态
    status = Column(Enum(ArticleStatus), default=ArticleStatus.DRAFT, index=True)

    # 来源信息
    source_topic = Column(String(500), nullable=True)  # 原始主题
    source_url = Column(String(1000), nullable=True)   # 来源链接

    # AI生成信息
    ai_model = Column(String(100), nullable=True)

    # 封面图
    cover_image_url = Column(String(1000), nullable=True)
    cover_image_media_id = Column(String(200), nullable=True)

    # 微信相关
    wechat_draft_id = Column(String(200), nullable=True)  # 草稿ID
    wechat_publish_time = Column(DateTime, nullable=True)   # 发布时间

    # 质量评分
    quality_score = Column(Float, nullable=True)           # 0-100分

    # 标签系统 - 以逗号分隔的标签字符串
    tags = Column(String(1000), nullable=True, index=True)

    # 阅读统计
    view_count = Column(Integer, default=0)      # 阅读次数
    like_count = Column(Integer, default=0)      # 点赞次数

    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, onupdate=func.now())

    # 定义复合索引以优化查询性能
    __table_args__ = (
        # 状态+创建时间复合索引：用于查询特定状态的文章（如已发布）
        Index('ix_articles_status_created_at', 'status', 'created_at'),
        # 标签+状态复合索引：用于按标签筛选文章
        Index('ix_articles_tags_status', 'tags', 'status'),
        # 点赞数索引：用于热门文章排序
        Index('ix_articles_like_count', 'like_count'),
    )

    def get_tags_list(self) -> list:
        """获取标签列表"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def set_tags_list(self, tags: list):
        """设置标签列表"""
        self.tags = ','.join(tags) if tags else None

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title}', status='{self.status}')>"