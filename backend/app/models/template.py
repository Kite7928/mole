"""
模板数据模型
支持10+分类模板管理，包括科技、财经、教育、健康、美食等
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Template(Base):
    """文章模板模型"""

    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="模板名称")
    category = Column(String(100), nullable=False, comment="模板分类")
    description = Column(Text, nullable=True, comment="模板描述")
    html_content = Column(Text, nullable=False, comment="HTML内容")
    css_content = Column(Text, nullable=True, comment="CSS样式")
    preview_image = Column(String(500), nullable=True, comment="预览图片URL")
    thumbnail = Column(String(500), nullable=True, comment="缩略图URL")
    is_default = Column(Boolean, default=False, comment="是否为默认模板")
    is_active = Column(Boolean, default=True, comment="是否启用")
    version = Column(String(50), default="1.0", comment="版本号")
    tags = Column(Text, nullable=True, comment="标签（JSON格式）")
    meta = Column(Text, nullable=True, comment="元数据（JSON格式）")

    # 排序和统计
    sort_order = Column(Integer, default=0, comment="排序顺序")
    usage_count = Column(Integer, default=0, comment="使用次数")
    like_count = Column(Integer, default=0, comment="点赞次数")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "html_content": self.html_content,
            "css_content": self.css_content,
            "preview_image": self.preview_image,
            "thumbnail": self.thumbnail,
            "is_default": self.is_default,
            "is_active": self.is_active,
            "version": self.version,
            "tags": self.tags,
            "meta": self.meta,
            "sort_order": self.sort_order,
            "usage_count": self.usage_count,
            "like_count": self.like_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }