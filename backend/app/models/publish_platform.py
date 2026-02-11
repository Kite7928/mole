"""
多平台发布模型
支持知乎、掘金、头条等多平台文章发布
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class PublishStatus(str, enum.Enum):
    """发布状态"""
    PENDING = "pending"         # 待发布
    PUBLISHING = "publishing"   # 发布中
    SUCCESS = "success"         # 发布成功
    FAILED = "failed"           # 发布失败
    PARTIAL = "partial"         # 部分成功


class PlatformType(str, enum.Enum):
    """平台类型"""
    WECHAT = "wechat"           # 微信公众号
    ZHIHU = "zhihu"             # 知乎
    JUEJIN = "juejin"           # 掘金
    TOUTIAO = "toutiao"         # 今日头条
    CSDN = "csdn"               # CSDN
    JIANSHU = "jianshu"         # 简书
    SEGMENTFAULT = "segmentfault"  # SegmentFault
    OSCHINA = "oschina"         # 开源中国
    BILIBILI = "bilibili"       # B站专栏


class PlatformConfig(Base):
    """平台配置模型 - 存储各平台的登录配置"""
    __tablename__ = "platform_configs"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(Enum(PlatformType), nullable=False, index=True)
    
    # 登录配置（加密存储）
    cookies = Column(Text, nullable=True)           # Cookie数据（JSON格式）
    token = Column(String(1000), nullable=True)     # API Token
    session_data = Column(Text, nullable=True)      # 其他会话数据
    
    # 状态
    is_enabled = Column(Boolean, default=False)     # 是否启用
    is_configured = Column(Boolean, default=False)  # 是否已配置
    last_login_at = Column(DateTime, nullable=True) # 最后登录时间
    
    # 发布配置
    default_category = Column(String(200), nullable=True)  # 默认分类
    default_tags = Column(String(500), nullable=True)      # 默认标签
    auto_publish = Column(Boolean, default=False)          # 是否自动发布（还是保存草稿）
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<PlatformConfig(platform='{self.platform.value}', enabled={self.is_enabled})>"


class PublishRecord(Base):
    """发布记录模型 - 记录文章发布到各平台的历史"""
    __tablename__ = "publish_records"

    id = Column(Integer, primary_key=True, index=True)
    
    # 关联文章
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, index=True)
    
    # 目标平台
    platform = Column(Enum(PlatformType), nullable=False, index=True)
    
    # 发布状态
    status = Column(Enum(PublishStatus), default=PublishStatus.PENDING)
    error_message = Column(Text, nullable=True)      # 错误信息
    
    # 平台返回信息
    platform_article_id = Column(String(200), nullable=True)   # 平台文章ID
    platform_article_url = Column(String(1000), nullable=True) # 平台文章URL
    platform_status = Column(String(100), nullable=True)       # 平台状态（审核中、已发布等）
    
    # 统计数据（从平台同步）
    view_count = Column(Integer, default=0)          # 阅读量
    like_count = Column(Integer, default=0)          # 点赞数
    comment_count = Column(Integer, default=0)       # 评论数
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    published_at = Column(DateTime, nullable=True)   # 实际发布时间
    
    # 发布内容快照（防止原文被修改后无法追溯）
    title_snapshot = Column(String(500), nullable=True)
    content_snapshot = Column(Text, nullable=True)

    def __repr__(self):
        return f"<PublishRecord(article_id={self.article_id}, platform='{self.platform.value}', status='{self.status.value}')>"


# 定义复合索引以优化查询性能
__table_args__ = (
    # 文章ID+平台复合索引：用于查询某文章的所有发布记录
    # 优化场景：获取文章的多平台发布状态
    ('ix_publish_records_article_platform', 'article_id', 'platform'),
    
    # 平台+状态+创建时间复合索引：用于查询平台的成功发布记录
    # 优化场景：获取某平台成功发布的文章列表
    ('ix_publish_records_platform_status_created', 'platform', 'status', 'created_at'),
    
    # 文章ID+状态复合索引：用于查询文章的发布状态
    # 优化场景：查询文章是否已成功发布到某平台
    ('ix_publish_records_article_status', 'article_id', 'status'),
)


class PublishTask(Base):
    """发布任务模型 - 批量发布任务"""
    __tablename__ = "publish_tasks"

    id = Column(Integer, primary_key=True, index=True)
    
    # 任务名称
    name = Column(String(200), nullable=False)
    
    # 关联文章
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    
    # 目标平台列表（JSON数组）
    target_platforms = Column(Text, nullable=False)
    
    # 任务状态
    status = Column(Enum(PublishStatus), default=PublishStatus.PENDING)
    
    # 执行结果
    total_count = Column(Integer, default=0)         # 总平台数
    success_count = Column(Integer, default=0)       # 成功数
    failed_count = Column(Integer, default=0)        # 失败数
    
    # 错误信息
    error_log = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<PublishTask(name='{self.name}', status='{self.status.value}')>"


# 平台信息常量
PLATFORM_INFO = {
    PlatformType.WECHAT: {
        "name": "微信公众号",
        "icon": "💬",
        "description": "发布到微信公众号草稿箱",
        "support_html": True,
        "support_markdown": False,
        "need_login": True,
    },
    PlatformType.ZHIHU: {
        "name": "知乎",
        "icon": "📚",
        "description": "发布到知乎专栏",
        "support_html": True,
        "support_markdown": True,
        "need_login": True,
    },
    PlatformType.JUEJIN: {
        "name": "掘金",
        "icon": "🚀",
        "description": "发布到掘金社区",
        "support_html": False,
        "support_markdown": True,
        "need_login": True,
    },
    PlatformType.TOUTIAO: {
        "name": "今日头条",
        "icon": "📰",
        "description": "发布到头条号",
        "support_html": True,
        "support_markdown": False,
        "need_login": True,
    },
    PlatformType.CSDN: {
        "name": "CSDN",
        "icon": "💻",
        "description": "发布到CSDN博客",
        "support_html": True,
        "support_markdown": True,
        "need_login": True,
    },
    PlatformType.JIANSHU: {
        "name": "简书",
        "icon": "📝",
        "description": "发布到简书",
        "support_html": False,
        "support_markdown": True,
        "need_login": True,
    },
    PlatformType.SEGMENTFAULT: {
        "name": "SegmentFault",
        "icon": "🔧",
        "description": "发布到思否社区",
        "support_html": True,
        "support_markdown": True,
        "need_login": True,
    },
    PlatformType.OSCHINA: {
        "name": "开源中国",
        "icon": "🌐",
        "description": "发布到开源中国",
        "support_html": True,
        "support_markdown": True,
        "need_login": True,
    },
    PlatformType.BILIBILI: {
        "name": "B站专栏",
        "icon": "📺",
        "description": "发布到Bilibili专栏",
        "support_html": True,
        "support_markdown": False,
        "need_login": True,
    },
}
