"""
多平台图片规格配置
支持各平台的封面图、行内配图尺寸要求
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ImageType(str, Enum):
    """图片类型"""
    COVER = "cover"              # 封面图
    INLINE = "inline"            # 行内配图
    THUMBNAIL = "thumbnail"      # 缩略图
    BANNER = "banner"            # 横幅图


@dataclass
class ImageSpec:
    """图片规格定义"""
    width: int
    height: int
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    max_size_mb: float = 5.0      # 最大文件大小（MB）
    formats: List[str] = None     # 支持的格式
    aspect_ratio: Optional[str] = None  # 宽高比要求，如 "16:9", "1:1"
    
    def __post_init__(self):
        if self.formats is None:
            self.formats = ["jpg", "jpeg", "png", "gif", "webp"]


@dataclass
class PlatformImageSpecs:
    """平台图片规格集合"""
    platform_name: str
    platform_icon: str
    cover: ImageSpec              # 封面图规格
    inline: ImageSpec             # 行内配图规格
    thumbnail: Optional[ImageSpec] = None  # 缩略图规格
    banner: Optional[ImageSpec] = None     # 横幅图规格
    max_images_per_article: int = 50       # 文章最大图片数
    support_gif: bool = True               # 是否支持GIF
    support_webp: bool = True              # 是否支持WebP
    auto_compress: bool = True             # 是否自动压缩


# ==================== 平台图片规格定义 ====================

PLATFORM_IMAGE_SPECS: Dict[str, PlatformImageSpecs] = {
    # 微信公众号
    "wechat": PlatformImageSpecs(
        platform_name="微信公众号",
        platform_icon="💬",
        cover=ImageSpec(
            width=900,
            height=500,
            min_width=300,
            min_height=200,
            max_width=2000,
            max_height=2000,
            max_size_mb=5.0,
            aspect_ratio="1.8:1",
            formats=["jpg", "jpeg", "png", "gif", "bmp"]
        ),
        inline=ImageSpec(
            width=800,
            height=600,
            max_width=2000,
            max_height=2000,
            max_size_mb=10.0,
            formats=["jpg", "jpeg", "png", "gif", "bmp"]
        ),
        max_images_per_article=50,
        support_gif=True,
        support_webp=False,  # 微信不支持WebP
        auto_compress=True
    ),
    
    # 知乎
    "zhihu": PlatformImageSpecs(
        platform_name="知乎",
        platform_icon="📚",
        cover=ImageSpec(
            width=1200,
            height=675,
            min_width=600,
            min_height=338,
            max_width=4000,
            max_height=3000,
            max_size_mb=20.0,
            aspect_ratio="16:9",
            formats=["jpg", "jpeg", "png", "gif", "webp"]
        ),
        inline=ImageSpec(
            width=1200,
            height=800,
            max_width=4000,
            max_height=4000,
            max_size_mb=20.0,
            formats=["jpg", "jpeg", "png", "gif", "webp"]
        ),
        max_images_per_article=100,
        support_gif=True,
        support_webp=True,
        auto_compress=True
    ),
    
    # 掘金
    "juejin": PlatformImageSpecs(
        platform_name="掘金",
        platform_icon="🚀",
        cover=ImageSpec(
            width=1200,
            height=630,
            min_width=600,
            min_height=315,
            max_width=2000,
            max_height=1500,
            max_size_mb=5.0,
            aspect_ratio="1.9:1",
            formats=["jpg", "jpeg", "png", "gif", "webp"]
        ),
        inline=ImageSpec(
            width=1000,
            height=750,
            max_width=2000,
            max_height=2000,
            max_size_mb=10.0,
            formats=["jpg", "jpeg", "png", "gif", "webp"]
        ),
        max_images_per_article=50,
        support_gif=True,
        support_webp=True,
        auto_compress=True
    ),
    
    # 今日头条
    "toutiao": PlatformImageSpecs(
        platform_name="今日头条",
        platform_icon="📰",
        cover=ImageSpec(
            width=1200,
            height=675,
            min_width=500,
            min_height=280,
            max_width=2000,
            max_height=1500,
            max_size_mb=5.0,
            aspect_ratio="16:9",
            formats=["jpg", "jpeg", "png", "gif"]
        ),
        inline=ImageSpec(
            width=800,
            height=600,
            max_width=2000,
            max_height=2000,
            max_size_mb=10.0,
            formats=["jpg", "jpeg", "png", "gif"]
        ),
        max_images_per_article=30,
        support_gif=True,
        support_webp=False,
        auto_compress=True
    ),
    
    # CSDN
    "csdn": PlatformImageSpecs(
        platform_name="CSDN",
        platform_icon="💻",
        cover=ImageSpec(
            width=1000,
            height=560,
            min_width=400,
            min_height=224,
            max_width=2000,
            max_height=1500,
            max_size_mb=5.0,
            aspect_ratio="16:9",
            formats=["jpg", "jpeg", "png", "gif", "webp"]
        ),
        inline=ImageSpec(
            width=800,
            height=600,
            max_width=2000,
            max_height=2000,
            max_size_mb=10.0,
            formats=["jpg", "jpeg", "png", "gif", "webp"]
        ),
        max_images_per_article=50,
        support_gif=True,
        support_webp=True,
        auto_compress=True
    ),
    
    # 简书
    "jianshu": PlatformImageSpecs(
        platform_name="简书",
        platform_icon="📝",
        cover=ImageSpec(
            width=900,
            height=500,
            min_width=300,
            min_height=167,
            max_width=2000,
            max_height=1500,
            max_size_mb=5.0,
            aspect_ratio="1.8:1",
            formats=["jpg", "jpeg", "png", "gif"]
        ),
        inline=ImageSpec(
            width=700,
            height=525,
            max_width=2000,
            max_height=2000,
            max_size_mb=10.0,
            formats=["jpg", "jpeg", "png", "gif"]
        ),
        max_images_per_article=30,
        support_gif=True,
        support_webp=False,
        auto_compress=True
    ),
    
    # SegmentFault 思否
    "segmentfault": PlatformImageSpecs(
        platform_name="SegmentFault",
        platform_icon="🔧",
        cover=ImageSpec(
            width=1200,
            height=630,
            min_width=600,
            min_height=315,
            max_width=2000,
            max_height=1500,
            max_size_mb=5.0,
            aspect_ratio="1.9:1",
            formats=["jpg", "jpeg", "png", "gif", "webp"]
        ),
        inline=ImageSpec(
            width=800,
            height=600,
            max_width=2000,
            max_height=2000,
            max_size_mb=10.0,
            formats=["jpg", "jpeg", "png", "gif", "webp"]
        ),
        max_images_per_article=50,
        support_gif=True,
        support_webp=True,
        auto_compress=True
    ),
    
    # 开源中国
    "oschina": PlatformImageSpecs(
        platform_name="开源中国",
        platform_icon="🌐",
        cover=ImageSpec(
            width=900,
            height=500,
            min_width=400,
            min_height=222,
            max_width=2000,
            max_height=1500,
            max_size_mb=5.0,
            aspect_ratio="1.8:1",
            formats=["jpg", "jpeg", "png", "gif"]
        ),
        inline=ImageSpec(
            width=800,
            height=600,
            max_width=2000,
            max_height=2000,
            max_size_mb=10.0,
            formats=["jpg", "jpeg", "png", "gif"]
        ),
        max_images_per_article=40,
        support_gif=True,
        support_webp=False,
        auto_compress=True
    ),
    
    # B站专栏
    "bilibili": PlatformImageSpecs(
        platform_name="B站专栏",
        platform_icon="📺",
        cover=ImageSpec(
            width=1140,
            height=760,
            min_width=570,
            min_height=380,
            max_width=2000,
            max_height=1500,
            max_size_mb=5.0,
            aspect_ratio="3:2",
            formats=["jpg", "jpeg", "png", "gif", "webp"]
        ),
        inline=ImageSpec(
            width=1140,
            height=760,
            max_width=2000,
            max_height=2000,
            max_size_mb=10.0,
            formats=["jpg", "jpeg", "png", "gif", "webp"]
        ),
        max_images_per_article=100,
        support_gif=True,
        support_webp=True,
        auto_compress=True
    ),
    
    # 小红书
    "xiaohongshu": PlatformImageSpecs(
        platform_name="小红书",
        platform_icon="📕",
        cover=ImageSpec(
            width=1242,
            height=1660,
            min_width=621,
            min_height=830,
            max_width=2000,
            max_height=2667,
            max_size_mb=20.0,
            aspect_ratio="3:4",
            formats=["jpg", "jpeg", "png", "webp"]
        ),
        inline=ImageSpec(
            width=1242,
            height=1660,
            max_width=2000,
            max_height=2667,
            max_size_mb=20.0,
            formats=["jpg", "jpeg", "png", "webp"]
        ),
        max_images_per_article=18,  # 小红书限制最多18张图
        support_gif=False,
        support_webp=True,
        auto_compress=True
    ),
    
    # 微博
    "weibo": PlatformImageSpecs(
        platform_name="微博",
        platform_icon="👁️",
        cover=ImageSpec(
            width=1200,
            height=675,
            min_width=600,
            min_height=338,
            max_width=2000,
            max_height=1500,
            max_size_mb=20.0,
            aspect_ratio="16:9",
            formats=["jpg", "jpeg", "png", "gif", "webp"]
        ),
        inline=ImageSpec(
            width=800,
            height=600,
            max_width=2000,
            max_height=2000,
            max_size_mb=20.0,
            formats=["jpg", "jpeg", "png", "gif", "webp"]
        ),
        max_images_per_article=18,
        support_gif=True,
        support_webp=True,
        auto_compress=True
    ),
}


# ==================== 通用图片规格 ====================

DEFAULT_IMAGE_SPECS = {
    "cover": ImageSpec(
        width=900,
        height=500,
        max_size_mb=5.0,
        aspect_ratio="1.8:1",
        formats=["jpg", "jpeg", "png", "gif", "webp"]
    ),
    "inline": ImageSpec(
        width=800,
        height=600,
        max_size_mb=10.0,
        formats=["jpg", "jpeg", "png", "gif", "webp"]
    ),
    "thumbnail": ImageSpec(
        width=300,
        height=200,
        max_size_mb=1.0,
        formats=["jpg", "jpeg", "png"]
    ),
    "banner": ImageSpec(
        width=1920,
        height=400,
        max_size_mb=5.0,
        aspect_ratio="4.8:1",
        formats=["jpg", "jpeg", "png"]
    )
}


def get_platform_spec(platform: str, image_type: str = "cover") -> Optional[ImageSpec]:
    """
    获取平台的图片规格
    
    Args:
        platform: 平台标识符
        image_type: 图片类型 (cover/inline/thumbnail/banner)
    
    Returns:
        图片规格定义
    """
    specs = PLATFORM_IMAGE_SPECS.get(platform.lower())
    if not specs:
        # 返回默认规格
        return DEFAULT_IMAGE_SPECS.get(image_type)
    
    if image_type == "cover":
        return specs.cover
    elif image_type == "inline":
        return specs.inline
    elif image_type == "thumbnail":
        return specs.thumbnail or DEFAULT_IMAGE_SPECS.get("thumbnail")
    elif image_type == "banner":
        return specs.banner or DEFAULT_IMAGE_SPECS.get("banner")
    
    return None


def get_optimal_image_size(platform: str, image_type: str = "cover") -> Tuple[int, int]:
    """
    获取平台推荐的最佳图片尺寸
    
    Args:
        platform: 平台标识符
        image_type: 图片类型
    
    Returns:
        (width, height) 元组
    """
    spec = get_platform_spec(platform, image_type)
    if spec:
        return (spec.width, spec.height)
    return (900, 500)  # 默认尺寸


def get_supported_platforms() -> List[str]:
    """获取所有支持的平台列表"""
    return list(PLATFORM_IMAGE_SPECS.keys())


def validate_image_for_platform(
    platform: str,
    image_path: str,
    image_type: str = "cover"
) -> Tuple[bool, str]:
    """
    验证图片是否符合平台要求
    
    Args:
        platform: 平台标识符
        image_path: 图片文件路径
        image_type: 图片类型
    
    Returns:
        (是否有效, 错误信息)
    """
    import os
    from PIL import Image
    
    spec = get_platform_spec(platform, image_type)
    if not spec:
        return True, ""  # 没有规格限制，默认通过
    
    try:
        # 检查文件是否存在
        if not os.path.exists(image_path):
            return False, "图片文件不存在"
        
        # 检查文件大小
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        if file_size_mb > spec.max_size_mb:
            return False, f"文件大小 {file_size_mb:.2f}MB 超过限制 {spec.max_size_mb}MB"
        
        # 检查图片尺寸
        with Image.open(image_path) as img:
            width, height = img.size
            
            # 检查最小尺寸
            if spec.min_width and width < spec.min_width:
                return False, f"图片宽度 {width}px 小于最小要求 {spec.min_width}px"
            if spec.min_height and height < spec.min_height:
                return False, f"图片高度 {height}px 小于最小要求 {spec.min_height}px"
            
            # 检查最大尺寸
            if spec.max_width and width > spec.max_width:
                return False, f"图片宽度 {width}px 超过最大限制 {spec.max_width}px"
            if spec.max_height and height > spec.max_height:
                return False, f"图片高度 {height}px 超过最大限制 {spec.max_height}px"
            
            # 检查格式
            img_format = img.format.lower() if img.format else ""
            if img_format not in spec.formats:
                return False, f"图片格式 {img_format} 不被支持，支持的格式: {', '.join(spec.formats)}"
        
        return True, "图片验证通过"
        
    except Exception as e:
        return False, f"验证图片失败: {str(e)}"


def get_platform_image_recommendations(platform: str) -> Dict[str, any]:
    """
    获取平台的图片使用建议
    
    Args:
        platform: 平台标识符
    
    Returns:
        推荐配置字典
    """
    specs = PLATFORM_IMAGE_SPECS.get(platform.lower())
    if not specs:
        return {
            "cover_size": "900×500",
            "inline_max": "10MB",
            "tips": ["使用通用的 900×500 封面图尺寸"]
        }
    
    cover = specs.cover
    inline = specs.inline
    
    tips = []
    
    # 根据平台特点生成建议
    if platform.lower() == "wechat":
        tips.extend([
            "微信公众号封面图建议使用 900×500 尺寸",
            "不支持 WebP 格式，请使用 JPG 或 PNG",
            "GIF 动图仅支持在第一帧显示"
        ])
    elif platform.lower() == "zhihu":
        tips.extend([
            "知乎封面图建议使用 1200×675 尺寸（16:9）",
            "支持 WebP 格式，可以获得更好的压缩率",
            "单篇文章最多支持 100 张图片"
        ])
    elif platform.lower() == "xiaohongshu":
        tips.extend([
            "小红书封面图建议使用 1242×1660 尺寸（3:4）",
            "竖版图片在小红书上展示效果更好",
            "最多支持 18 张图片，适合图文笔记"
        ])
    elif platform.lower() == "bilibili":
        tips.extend([
            "B站专栏封面图建议使用 1140×760 尺寸（3:2）",
            "支持 GIF 动图，适合展示动态效果",
            "可以上传高清大图，系统会自动压缩"
        ])
    
    return {
        "cover_size": f"{cover.width}×{cover.height}",
        "cover_aspect": cover.aspect_ratio or "自适应",
        "inline_max": f"{inline.max_size_mb}MB",
        "max_images": specs.max_images_per_article,
        "support_gif": specs.support_gif,
        "support_webp": specs.support_webp,
        "tips": tips
    }
