from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from ..core.database import Base


class WeChatConfig(Base):
    """微信配置模型（单用户，使用默认配置）"""
    __tablename__ = "wechat_config"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, default="我的公众号")
    app_id = Column(String(100), unique=True, nullable=False, index=True)
    app_secret = Column(String(200), nullable=False)

    # Token管理
    access_token = Column(String(500), nullable=True)
    token_expires_at = Column(DateTime, nullable=True)

    # 是否激活
    is_active = Column(Boolean, default=True)

    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_sync_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<WeChatConfig(id={self.id}, name='{self.name}', app_id='{self.app_id}')>"