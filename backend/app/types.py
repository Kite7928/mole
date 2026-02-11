"""
类型定义模块
提供项目的类型提示和类型别名
"""

from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json


# ============================================================================
# API 相关类型
# ============================================================================

class ArticleStatus(str, Enum):
    """文章状态枚举"""
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    PUBLISHED = "published"
    FAILED = "failed"


class PlatformType(str, Enum):
    """平台类型枚举"""
    WECHAT = "wechat"
    ZHIHU = "zhihu"
    JUEJIN = "juejin"
    TOUTIAO = "toutiao"


class PublishStatus(str, Enum):
    """发布状态枚举"""
    PENDING = "pending"
    PUBLISHING = "publishing"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


# ============================================================================
# 数据模型类型
# ============================================================================

@dataclass
class ArticleSummary:
    """文章摘要"""
    id: int
    title: str
    status: ArticleStatus
    summary: Optional[str]
    cover_image_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    view_count: int = 0
    like_count: int = 0


@dataclass
class PlatformConfig:
    """平台配置"""
    platform: PlatformType
    enabled: bool
    configured: bool
    auto_publish: bool = False
    cookies: Optional[str] = None
    token: Optional[str] = None
    session_data: Optional[str] = None


@dataclass
class PublishRecord:
    """发布记录"""
    id: int
    article_id: int
    platform: PlatformType
    status: PublishStatus
    platform_article_id: Optional[str]
    platform_article_url: Optional[str]
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    created_at: Optional[datetime] = None
    published_at: Optional[datetime] = None


# ============================================================================
# API 请求/响应类型
# ============================================================================

@dataclass
class CreateArticleRequest:
    """创建文章请求"""
    title: str
    content: str
    summary: Optional[str] = None
    cover_image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None


@dataclass
class UpdateArticleRequest:
    """更新文章请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    cover_image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None


@dataclass
class PublishToPlatformsRequest:
    """发布到多平台请求"""
    article_id: int
    platforms: List[PlatformType]
    publish_now: bool = True
    publish_at: Optional[datetime] = None


@dataclass
class SyncStatsRequest:
    """同步统计数据请求"""
    article_id: Optional[int] = None
    platform: Optional[PlatformType] = None
    days: int = 7


# ============================================================================
# 服务层类型
# ============================================================================

@dataclass
class PublishResult:
    """发布结果"""
    success: bool
    platform: PlatformType
    message: str
    article_id: Optional[str] = None
    article_url: Optional[str] = None
    error_code: Optional[str] = None
    need_retry: bool = False
    retry_after: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ArticleContent:
    """文章内容"""
    title: str
    content: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    author: Optional[str] = None


@dataclass
class PlatformStats:
    """平台统计数据"""
    view_count: int
    like_count: int
    comment_count: int
    extra_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.extra_data is None:
            self.extra_data = {}


# ============================================================================
# 响应类型
# ============================================================================

class APIResponse(dict):
    """API响应基类"""
    def __init__(
        self,
        success: bool = True,
        message: str = "",
        data: Optional[Any] = None,
        error: Optional[str] = None,
        code: int = 200
    ):
        super().__init__(
            success=success,
            message=message,
            data=data,
            error=error,
            code=code
        )

    @classmethod
    def success_response(cls, message: str = "操作成功", data: Optional[Any] = None) -> "APIResponse":
        """成功响应"""
        return cls(success=True, message=message, data=data, code=200)

    @classmethod
    def error_response(cls, message: str, error: Optional[str] = None, code: int = 500) -> "APIResponse":
        """错误响应"""
        return cls(success=False, message=message, error=error, code=code)

    @classmethod
    def not_found(cls, message: str = "资源不存在") -> "APIResponse":
        """404响应"""
        return cls(success=False, message=message, code=404)

    @classmethod
    def bad_request(cls, message: str = "请求参数错误") -> "APIResponse":
        """400响应"""
        return cls(success=False, message=message, code=400)


# ============================================================================
# 工具类型
# ============================================================================

def serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    """序列化日期时间为ISO格式字符串"""
    if dt is None:
        return None
    return dt.isoformat()


def deserialize_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """反序列化ISO格式字符串为日期时间"""
    if dt_str is None:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return None


# ============================================================================
# 类型别名
# ============================================================================

# 字典类型别名
ConfigDict = Dict[str, Any]
HeadersDict = Dict[str, str]
QueryParams = Dict[str, Any]

# 列表类型别名
PlatformList = List[PlatformType]
ArticleList = List[ArticleSummary]
PublishRecordList = List[PublishRecord]

# 可选类型别名
OptionalStr = Optional[str]
OptionalInt = Optional[int]
OptionalBool = Optional[bool]

# 联合类型别名
JSONValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]