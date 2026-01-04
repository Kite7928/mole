from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class ArticleStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    PUBLISHED = "published"
    FAILED = "failed"


class ArticleSource(str, enum.Enum):
    MANUAL = "manual"
    AI_HOTSPOT = "ai_hotspot"
    BAIDU_SEARCH = "baidu_search"
    CUSTOM_RSS = "custom_rss"


class Article(Base):
    """
    Article model for storing generated articles.
    """
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    html_content = Column(Text, nullable=True)

    # Article metadata
    status = Column(Enum(ArticleStatus), default=ArticleStatus.DRAFT, index=True)
    source = Column(Enum(ArticleSource), default=ArticleSource.MANUAL)
    source_topic = Column(String(500), nullable=True)
    source_url = Column(String(1000), nullable=True)

    # AI generation metadata
    ai_model = Column(String(100), nullable=True)
    ai_prompt_tokens = Column(Integer, nullable=True)
    ai_completion_tokens = Column(Integer, nullable=True)
    ai_total_tokens = Column(Integer, nullable=True)

    # Cover image
    cover_image_url = Column(String(1000), nullable=True)
    cover_image_media_id = Column(String(200), nullable=True)

    # WeChat specific
    wechat_draft_id = Column(String(200), nullable=True)
    wechat_publish_time = Column(DateTime(timezone=True), nullable=True)
    wechat_article_id = Column(String(200), nullable=True)

    # Statistics
    read_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)

    # Tags and categories
    tags = Column(JSON, nullable=True)  # List of tags
    category = Column(String(100), nullable=True)

    # Quality metrics
    quality_score = Column(Float, nullable=True)
    predicted_click_rate = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("wechat_accounts.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="articles")
    account = relationship("WeChatAccount", back_populates="articles")
    tasks = relationship("Task", back_populates="article", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title}', status='{self.status}')>"


class ArticleTemplate(Base):
    """
    Article template model for predefined content structures.
    """
    __tablename__ = "article_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(String(50), nullable=False)  # e.g., "tech_news", "product_review"

    # Template structure
    structure = Column(JSON, nullable=False)  # Template structure definition
    prompt_template = Column(Text, nullable=False)  # AI prompt template

    # Default settings
    default_ai_model = Column(String(100), nullable=True)
    default_temperature = Column(Float, nullable=True)
    default_max_tokens = Column(Integer, nullable=True)

    # Usage statistics
    usage_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ArticleTemplate(id={self.id}, name='{self.name}', type='{self.template_type}')>"