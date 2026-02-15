"""
专业的 Prompt 模板系统
用于生成微信公众号文章配图
"""
from typing import Dict, List, Optional, Any
from enum import Enum


class ImageStyle(str, Enum):
    """图片风格枚举"""
    PROFESSIONAL = "professional"  # 专业商务
    CREATIVE = "creative"          # 创意艺术
    MINIMAL = "minimal"            # 极简风格
    VIBRANT = "vibrant"            # 鲜艳活力
    TECH = "tech"                  # 科技感
    NATURE = "nature"              # 自然生态
    ABSTRACT = "abstract"          # 抽象艺术
    CHINESE = "chinese"            # 中国风
    CARTOON = "cartoon"            # 卡通插画
    REALISTIC = "realistic"        # 写实摄影


class ImagePosition(str, Enum):
    """图片位置枚举"""
    COVER = "cover"                # 封面图
    PARAGRAPH = "paragraph"        # 段落配图
    INLINE = "inline"              # 行内插图
    CHART = "chart"                # 数据图表
    QUOTE = "quote"                # 引用配图


class PromptTemplate:
    """Prompt 模板基类"""
    
    # 风格描述词映射
    STYLE_DESCRIPTIONS = {
        ImageStyle.PROFESSIONAL: {
            "zh": "专业商务风格，简洁大气，适合职场和商业场景",
            "en": "professional business style, clean and elegant, suitable for workplace and business scenes",
            "keywords": ["professional", "business", "clean", "modern", "elegant"],
            "tongyi_style": "<photography>"
        },
        ImageStyle.CREATIVE: {
            "zh": "创意艺术风格，色彩丰富，充满想象力",
            "en": "creative artistic style, rich colors, full of imagination",
            "keywords": ["creative", "artistic", "colorful", "dynamic", "expressive"],
            "tongyi_style": "<anime>"
        },
        ImageStyle.MINIMAL: {
            "zh": "极简风格，留白充足，突出主题",
            "en": "minimalist style, ample white space, highlighting the subject",
            "keywords": ["minimal", "simple", "elegant", "clean", "subtle"],
            "tongyi_style": "<flat illustration>"
        },
        ImageStyle.VIBRANT: {
            "zh": "鲜艳活力风格，色彩明快，充满能量",
            "en": "vibrant energetic style, bright colors, full of energy",
            "keywords": ["vibrant", "energetic", "bold", "colorful", "striking"],
            "tongyi_style": "<3d cartoon>"
        },
        ImageStyle.TECH: {
            "zh": "科技感风格，未来主义，数字化元素",
            "en": "tech style, futuristic, digital elements",
            "keywords": ["technology", "futuristic", "digital", "blue tones", "modern"],
            "tongyi_style": "<3d cartoon>"
        },
        ImageStyle.NATURE: {
            "zh": "自然生态风格，清新自然，绿色环保",
            "en": "natural ecological style, fresh and natural, green and eco-friendly",
            "keywords": ["natural", "organic", "green", "peaceful", "ecological"],
            "tongyi_style": "<watercolor>"
        },
        ImageStyle.ABSTRACT: {
            "zh": "抽象艺术风格，几何图形，现代艺术",
            "en": "abstract art style, geometric shapes, modern art",
            "keywords": ["abstract", "geometric", "modern art", "colorful", "artistic"],
            "tongyi_style": "<sketch>"
        },
        ImageStyle.CHINESE: {
            "zh": "中国风，水墨画风格，传统文化元素",
            "en": "Chinese style, ink painting, traditional cultural elements",
            "keywords": ["chinese", "ink painting", "traditional", "cultural", "elegant"],
            "tongyi_style": "<chinese painting>"
        },
        ImageStyle.CARTOON: {
            "zh": "卡通插画风格，可爱生动，适合轻松话题",
            "en": "cartoon illustration style, cute and lively, suitable for light topics",
            "keywords": ["cartoon", "illustration", "cute", "lively", "friendly"],
            "tongyi_style": "<3d cartoon>"
        },
        ImageStyle.REALISTIC: {
            "zh": "写实摄影风格，真实自然，高清晰度",
            "en": "realistic photography style, natural and authentic, high definition",
            "keywords": ["realistic", "photography", "natural", "high definition", "authentic"],
            "tongyi_style": "<photography>"
        }
    }
    
    @classmethod
    def build_cover_prompt(
        cls,
        title: str,
        summary: Optional[str] = None,
        style: ImageStyle = ImageStyle.PROFESSIONAL,
        language: str = "zh",
        provider: str = "tongyi"
    ) -> Dict[str, str]:
        """
        构建封面图 Prompt
        
        Args:
            title: 文章标题
            summary: 文章摘要
            style: 图片风格
            language: 语言（zh/en）
            provider: 提供商（tongyi/dalle/midjourney）
            
        Returns:
            包含完整 prompt 的字典
        """
        style_info = cls.STYLE_DESCRIPTIONS.get(style, cls.STYLE_DESCRIPTIONS[ImageStyle.PROFESSIONAL])
        
        if language == "zh":
            # 中文提示词（通义万相等中文模型）
            base_prompt = f"""为微信公众号文章《{title}》创作一张精美的封面图。

【风格要求】{style_info['zh']}
【画面元素】{', '.join(style_info['keywords'][:3])}
【质量要求】4K高清，构图精美，色彩和谐，适合作为公众号文章封面
【尺寸】16:9横幅比例，900x500像素
"""
            if summary:
                base_prompt += f"\n【文章概要】{summary[:100]}\n"
                
            base_prompt += "\n【要求】画面要突出文章主题，具有视觉吸引力，不要出现文字。"
            
        else:
            # 英文提示词（DALL-E/Midjourney等）
            base_prompt = f"""Create a stunning cover image for a WeChat article titled "{title}".

Style: {style_info['en']}
Elements: {', '.join(style_info['keywords'])}
Quality: 4K high definition, exquisite composition, harmonious colors
Format: 16:9 banner ratio, suitable for WeChat official account cover
"""
            if summary:
                base_prompt += f"\nArticle Summary: {summary[:150]}\n"
                
            base_prompt += "\nRequirements: Highlight the article theme, visually appealing, no text in the image."
        
        return {
            "prompt": base_prompt.strip(),
            "style": style.value,
            "style_description": style_info['zh'] if language == 'zh' else style_info['en'],
            "tongyi_style": style_info['tongyi_style'],
            "position": "cover",
            "language": language
        }
    
    @classmethod
    def build_paragraph_prompt(
        cls,
        paragraph_title: str,
        paragraph_content: str,
        article_title: str,
        style: ImageStyle = ImageStyle.PROFESSIONAL,
        position_index: int = 0,
        language: str = "zh",
        provider: str = "tongyi"
    ) -> Dict[str, str]:
        """
        构建段落配图 Prompt
        
        Args:
            paragraph_title: 段落标题
            paragraph_content: 段落内容摘要
            article_title: 文章主标题
            style: 图片风格
            position_index: 段落位置索引
            language: 语言
            provider: 提供商
            
        Returns:
            包含完整 prompt 的字典
        """
        style_info = cls.STYLE_DESCRIPTIONS.get(style, cls.STYLE_DESCRIPTIONS[ImageStyle.PROFESSIONAL])
        
        # 提取段落核心内容（前150字）
        content_summary = paragraph_content[:150] if len(paragraph_content) > 150 else paragraph_content
        
        if language == "zh":
            base_prompt = f"""为文章《{article_title}》的段落《{paragraph_title}》创作一张配图。

【段落内容】{content_summary}
【风格要求】{style_info['zh']}，与文章封面风格保持一致
【画面尺寸】900x500像素，适合公众号正文插图
【质量要求】高清精美，主题明确，与段落内容高度相关
"""
            base_prompt += "\n【要求】画面要直观表达段落主题，增强文章可读性，不要出现文字。"
            
        else:
            base_prompt = f"""Create an illustration for the paragraph "{paragraph_title}" in the article "{article_title}".

Paragraph Content: {content_summary}
Style: {style_info['en']}, consistent with the article cover
Format: 900x500 pixels, suitable for article body illustration
Quality: High definition, clear theme, highly relevant to paragraph content
"""
            base_prompt += "\nRequirements: Visually express the paragraph theme, enhance readability, no text in the image."
        
        return {
            "prompt": base_prompt.strip(),
            "style": style.value,
            "style_description": style_info['zh'] if language == 'zh' else style_info['en'],
            "tongyi_style": style_info['tongyi_style'],
            "position": f"paragraph_{position_index}",
            "paragraph_title": paragraph_title,
            "language": language
        }
    
    @classmethod
    def analyze_article_for_images(
        cls,
        content: str,
        max_images: int = 5
    ) -> List[Dict[str, Any]]:
        """
        分析文章内容，建议配图位置
        
        Args:
            content: 文章内容（Markdown格式）
            max_images: 最多建议的图片数量
            
        Returns:
            建议的配图位置列表
        """
        import re
        
        suggestions = []
        
        # 1. 封面图（必须）
        suggestions.append({
            "position": "cover",
            "type": "cover",
            "title": "文章封面",
            "description": "文章主封面图",
            "priority": 1
        })
        
        # 2. 分析段落标题（H2/H3）
        # 匹配 Markdown 标题
        heading_pattern = r'^#{2,3}\s+(.+)$'
        headings = re.findall(heading_pattern, content, re.MULTILINE)
        
        for i, heading in enumerate(headings[:max_images-1]):
            # 提取该段落的内容（到下一个标题为止）
            heading_pattern_escape = re.escape(heading)
            section_match = re.search(
                f'^#{2,3}\s+{heading_pattern_escape}$.*?(?=^#{1,3}\s|\Z)',
                content,
                re.MULTILINE | re.DOTALL
            )
            
            section_content = section_match.group(0) if section_match else ""
            # 移除标题本身
            section_content = re.sub(f'^#{2,3}\s+{heading_pattern_escape}$', '', section_content, flags=re.MULTILINE).strip()
            
            suggestions.append({
                "position": f"paragraph_{i+1}",
                "type": "paragraph",
                "title": heading,
                "description": section_content[:200],
                "priority": i + 2
            })
        
        return suggestions[:max_images]
    
    @classmethod
    def build_batch_prompts(
        cls,
        title: str,
        content: str,
        summary: Optional[str] = None,
        style: ImageStyle = ImageStyle.PROFESSIONAL,
        language: str = "zh",
        provider: str = "tongyi"
    ) -> List[Dict[str, Any]]:
        """
        批量构建文章所有配图的 Prompts
        
        Args:
            title: 文章标题
            content: 文章内容
            summary: 文章摘要
            style: 图片风格
            language: 语言
            provider: 提供商
            
        Returns:
            所有配图的 prompts 列表
        """
        # 1. 分析文章结构
        image_positions = cls.analyze_article_for_images(content)
        
        prompts = []
        
        for pos in image_positions:
            if pos["type"] == "cover":
                prompt_data = cls.build_cover_prompt(
                    title=title,
                    summary=summary,
                    style=style,
                    language=language,
                    provider=provider
                )
            else:
                prompt_data = cls.build_paragraph_prompt(
                    paragraph_title=pos["title"],
                    paragraph_content=pos["description"],
                    article_title=title,
                    style=style,
                    position_index=image_positions.index(pos),
                    language=language,
                    provider=provider
                )
            
            prompt_data["priority"] = pos["priority"]
            prompt_data["suggested_position"] = pos["position"]
            prompts.append(prompt_data)
        
        return prompts


# 便捷函数
def get_cover_prompt(
    title: str,
    summary: Optional[str] = None,
    style: str = "professional",
    language: str = "zh"
) -> str:
    """获取封面图 prompt（便捷函数）"""
    try:
        style_enum = ImageStyle(style)
    except ValueError:
        style_enum = ImageStyle.PROFESSIONAL
    
    result = PromptTemplate.build_cover_prompt(title, summary, style_enum, language)
    return result["prompt"]


def get_paragraph_prompt(
    paragraph_title: str,
    paragraph_content: str,
    article_title: str,
    style: str = "professional",
    language: str = "zh"
) -> str:
    """获取段落配图 prompt（便捷函数）"""
    try:
        style_enum = ImageStyle(style)
    except ValueError:
        style_enum = ImageStyle.PROFESSIONAL
    
    result = PromptTemplate.build_paragraph_prompt(
        paragraph_title, paragraph_content, article_title, style_enum, language=language
    )
    return result["prompt"]


def analyze_and_build_prompts(
    title: str,
    content: str,
    summary: Optional[str] = None,
    style: str = "professional",
    max_images: int = 5,
    language: str = "zh"
) -> List[Dict[str, Any]]:
    """分析文章并构建所有配图 prompts"""
    try:
        style_enum = ImageStyle(style)
    except ValueError:
        style_enum = ImageStyle.PROFESSIONAL
    
    return PromptTemplate.build_batch_prompts(title, content, summary, style_enum, language)
