from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    SUPER_ADMIN = "super_admin"  # 超级管理员
    CONTENT_OPERATOR = "content_operator"  # 内容运营
    CONTENT_REVIEWER = "content_reviewer"  # 内容审核
    NORMAL_USER = "normal_user"  # 普通用户


class User(Base):
    """
    User model for authentication and authorization.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # User profile
    full_name = Column(String(200), nullable=True)
    avatar_url = Column(String(1000), nullable=True)
    bio = Column(String(500), nullable=True)

    # User role and permissions
    role = Column(Enum(UserRole), default=UserRole.NORMAL_USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Preferences
    preferences = Column(JSON, nullable=True)  # User preferences and settings

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    articles = relationship("Article", back_populates="user")
    accounts = relationship("WeChatAccount", back_populates="user")
    tasks = relationship("Task", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"