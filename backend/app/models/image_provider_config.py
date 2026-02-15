"""
图片生成服务配置模型
支持多种AI图片生成平台的配置管理
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from ..core.database import Base


class ImageProviderConfig(Base):
    """图片生成服务提供商配置"""
    __tablename__ = "image_provider_configs"

    id = Column(Integer, primary_key=True, index=True)
    
    # 提供商类型
    provider_type = Column(String(50), nullable=False, index=True, comment="提供商类型")
    # 可选值: tongyi_wanxiang, pexels, leonardo, pollinations, stable_diffusion, cogview, dalle, gemini
    
    # 配置名称（用户自定义）
    name = Column(String(100), nullable=False, default="默认配置")
    
    # 是否启用
    is_enabled = Column(Boolean, default=True)
    
    # 是否设为默认
    is_default = Column(Boolean, default=False)
    
    # API配置（JSON格式存储）
    api_config = Column(Text, nullable=True, comment="API配置JSON")
    # 例如: {"api_key": "xxx", "base_url": "xxx", "model": "xxx"}
    
    # 默认生成参数
    default_params = Column(Text, nullable=True, comment="默认生成参数JSON")
    # 例如: {"width": 900, "height": 500, "style": "professional"}
    
    # 优先级（数字越小优先级越高）
    priority = Column(Integer, default=0)
    
    # 创建和更新时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ImageProviderConfig(id={self.id}, provider='{self.provider_type}', name='{self.name}')>"