"""
应用配置模型
用于保存用户在界面填写的配置
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from ..core.database import Base


class AppConfig(Base):
    """应用配置模型"""
    __tablename__ = "app_config"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # AI配置
    ai_provider = Column(String(50), default="deepseek")  # AI提供商
    api_key = Column(String(500), nullable=True)  # API密钥（加密存储）
    base_url = Column(String(500), default="https://api.deepseek.com/v1")  # API基础URL
    model = Column(String(100), default="deepseek-chat")  # 模型名称
    
    # 微信配置
    wechat_app_id = Column(String(200), nullable=True)  # 微信AppID
    wechat_app_secret = Column(String(500), nullable=True)  # 微信AppSecret（加密存储）
    
    # 其他配置
    enable_auto_publish = Column(Boolean, default=False)  # 是否自动发布
    max_news_count = Column(Integer, default=20)  # 最大新闻数量
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AppConfig(id={self.id}, ai_provider={self.ai_provider})>"