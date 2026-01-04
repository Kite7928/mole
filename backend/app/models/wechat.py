from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class WeChatAccount(Base):
    """
    WeChat account model for managing multiple WeChat official accounts.
    """
    __tablename__ = "wechat_accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    app_id = Column(String(100), unique=True, nullable=False, index=True)
    app_secret = Column(String(200), nullable=False)

    # Account information
    account_type = Column(String(50), nullable=True)  # e.g., "service", "subscription"
    verify_type = Column(String(50), nullable=True)
    principal_name = Column(String(200), nullable=True)
    signature = Column(String(500), nullable=True)

    # Token management
    access_token = Column(String(500), nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    jsapi_ticket = Column(String(500), nullable=True)
    jsapi_ticket_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Account settings
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    settings = Column(JSON, nullable=True)

    # Statistics
    followers_count = Column(Integer, default=0)
    articles_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_sync_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    articles = relationship("Article", back_populates="account")

    def __repr__(self):
        return f"<WeChatAccount(id={self.id}, name='{self.name}', app_id='{self.app_id}')>"


class WeChatMedia(Base):
    """
    WeChat media model for managing uploaded media files.
    """
    __tablename__ = "wechat_media"

    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(String(200), unique=True, nullable=False, index=True)
    media_type = Column(String(50), nullable=False)  # e.g., "image", "video", "voice"
    file_name = Column(String(500), nullable=True)
    file_url = Column(String(1000), nullable=True)
    file_size = Column(Integer, nullable=True)

    # Media metadata
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)  # For video/voice in seconds

    # Account association
    account_id = Column(Integer, ForeignKey("wechat_accounts.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<WeChatMedia(id={self.id}, media_id='{self.media_id}', type='{self.media_type}')>"