from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Enum, JSON, Boolean
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class NewsSource(str, enum.Enum):
    ITHOME = "ithome"
    KR36 = "36kr"
    BAIDU = "baidu"
    ZHIHU = "zhihu"
    WEIBO = "weibo"
    CUSTOM = "custom"


class NewsCategory(str, enum.Enum):
    AI = "ai"
    TECH = "tech"
    BUSINESS = "business"
    FINANCE = "finance"
    ENTERTAINMENT = "entertainment"
    SPORTS = "sports"
    AUTO = "auto"
    GAMING = "gaming"
    OTHER = "other"


class NewsItem(Base):
    """
    News item model for storing fetched news from various sources.
    """
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(1000), nullable=False, unique=True, index=True)

    # Source information
    source = Column(Enum(NewsSource), nullable=False, index=True)
    source_name = Column(String(100), nullable=True)
    author = Column(String(200), nullable=True)

    # Category and tags
    category = Column(Enum(NewsCategory), nullable=True, index=True)
    tags = Column(JSON, nullable=True)  # List of tags

    # Popularity metrics
    hot_score = Column(Float, default=0.0, index=True)
    read_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)

    # Media
    cover_image_url = Column(String(1000), nullable=True)
    images = Column(JSON, nullable=True)  # List of image URLs

    # Timestamps
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Processing status
    is_processed = Column(Boolean, default=False)
    is_used = Column(Boolean, default=False)  # Whether this news has been used for article generation
    used_article_id = Column(Integer, nullable=True)

    # Quality assessment
    quality_score = Column(Float, nullable=True)  # 0-1 score
    relevance_score = Column(Float, nullable=True)  # 0-1 score for relevance to target audience

    def __repr__(self):
        return f"<NewsItem(id={self.id}, title='{self.title}', source='{self.source}', hot_score={self.hot_score})>"


class NewsSourceConfig(Base):
    """
    Configuration for news sources.
    """
    __tablename__ = "news_source_configs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(Enum(NewsSource), unique=True, nullable=False)

    # Source configuration
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    rss_url = Column(String(1000), nullable=True)
    api_url = Column(String(1000), nullable=True)
    api_key = Column(String(200), nullable=True)

    # Fetch settings
    is_active = Column(Boolean, default=True)
    fetch_interval = Column(Integer, default=1800)  # seconds
    max_items_per_fetch = Column(Integer, default=50)
    retry_limit = Column(Integer, default=3)

    # Filtering
    min_hot_score = Column(Float, default=0.0)
    allowed_categories = Column(JSON, nullable=True)  # List of allowed categories
    blocked_keywords = Column(JSON, nullable=True)  # List of blocked keywords

    # Statistics
    total_fetched = Column(Integer, default=0)
    last_fetch_at = Column(DateTime(timezone=True), nullable=True)
    last_fetch_status = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<NewsSourceConfig(id={self.id}, source='{self.source}', name='{self.name}', is_active={self.is_active})>"