"""
文章排版优化服务
针对自媒体文章进行排版优化，提升阅读体验
"""

import re
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel


class FormatOptions(BaseModel):
    """排版选项"""
    add_emoji: bool = True
    highlight_key_points: bool = True
    add_subtitles: bool = True
    optimize_paragraphs: bool = True
    add_reading_guide: bool = False
    wechat_style: bool = True


class ArticleFormatter:
    """文章排版优化器"""
    
    # Emoji映射
    EMOJI_MAP = {
        "重要": "📌",
        "注意": "⚠️",
        "提示": "💡",
        "建议": "✅",
        "警告": "🚨",
        "疑问": "❓",
        "总结": "📝",
        "步骤": "🔢",
        "示例": "📋",
        "好处": "✨",
        "坏处": "❌",
        "对比": "⚖️",
        "技巧": "🎯",
        "秘密": "🤫",
        "真相": "🔍",
    }
    
    # 重点词高亮
    KEYWORDS = [
        "关键", "核心", "重点", "本质", "秘诀",
        "必须", "一定", "绝对", "千万", "记住",
        "注意", "警惕", "小心", "避免",
        "推荐", "建议", "首选", "最佳",
        "真相", "揭秘", "独家", "内部",
    ]
    
    @staticmethod
    def format_for_wechat(content: str, options: FormatOptions = None) -> str:
        """
        格式化为微信文章风格
        
        Args:
            content: 原始内容
            options: 排版选项
        
        Returns:
            格式化后的内容
        """
        if options is None:
            options = FormatOptions()
        
        result = content
        
        # 1. 优化段落长度
        if options.optimize_paragraphs:
            result = ArticleFormatter._optimize_paragraphs(result)
        
        # 2. 添加小标题
        if options.add_subtitles:
            result = ArticleFormatter._add_subtitles(result)
        
        # 3. 高亮重点
        if options.highlight_key_points:
            result = ArticleFormatter._highlight_keywords(result)
        
        # 4. 添加emoji
        if options.add_emoji:
            result = ArticleFormatter._add_emoji(result)
        
        # 5. 微信特殊格式
        if options.wechat_style:
            result = ArticleFormatter._apply_wechat_style(result)
        
        return result
    
    @staticmethod
    def _optimize_paragraphs(content: str) -> str:
        """优化段落长度，适合手机阅读"""
        paragraphs = content.split('\n\n')
        optimized = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 如果段落太长，拆分成多个小段落
            if len(para) > 200:
                sentences = re.split(r'([。！？])', para)
                current_para = ""
                
                for i in range(0, len(sentences), 2):
                    sentence = sentences[i]
                    if i + 1 < len(sentences):
                        sentence += sentences[i + 1]
                    
                    if len(current_para) + len(sentence) > 150:
                        if current_para:
                            optimized.append(current_para)
                        current_para = sentence
                    else:
                        current_para += sentence
                
                if current_para:
                    optimized.append(current_para)
            else:
                optimized.append(para)
        
        return '\n\n'.join(optimized)
    
    @staticmethod
    def _add_subtitles(content: str) -> str:
        """自动添加小标题"""
        paragraphs = content.split('\n\n')
        result = []
        
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue
            
            # 检查是否已经是标题
            if para.startswith('#') or para.startswith('【') or para.startswith('**'):
                result.append(para)
                continue
            
            # 在长内容前添加引导性小标题（每3-4段）
            if i > 0 and i % 3 == 0 and len(para) > 100:
                # 提取关键信息生成小标题
                first_sentence = para.split('。')[0][:20]
                if len(first_sentence) > 10:
                    subtitle = f"**💡 {first_sentence}...**"
                    result.append(subtitle)
            
            result.append(para)
        
        return '\n\n'.join(result)
    
    @staticmethod
    def _highlight_keywords(content: str) -> str:
        """高亮关键词"""
        result = content
        
        for keyword in ArticleFormatter.KEYWORDS:
            # 使用粗体标记关键词
            pattern = f"({keyword})"
            replacement = r"**\1**"
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    @staticmethod
    def _add_emoji(content: str) -> str:
        """在合适位置添加emoji"""
        result = content
        
        # 在段落开头添加相关emoji
        for text, emoji in ArticleFormatter.EMOJI_MAP.items():
            if text in result[:50]:  # 只在文章开头匹配
                result = emoji + " " + result
                break
        
        # 为数字列表添加emoji
        result = re.sub(r'^(\d+)\.\s+', r'🔢 \1. ', result, flags=re.MULTILINE)
        
        return result
    
    @staticmethod
    def _apply_wechat_style(content: str) -> str:
        """应用微信文章特殊格式"""
        # 添加引用框
        content = re.sub(
            r'^(?:引用|原文|摘要)[：:]\s*(.+)$',
            r'> 📌 \1',
            content,
            flags=re.MULTILINE
        )
        
        # 重点标注框
        content = re.sub(
            r'^(?:重点|核心|总结)[：:]\s*(.+)$',
            r'**📝 重点提示**\n\n\1',
            content,
            flags=re.MULTILINE
        )
        
        return content
    
    @staticmethod
    def extract_keywords(content: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        提取文章关键词
        
        Args:
            content: 文章内容
            top_n: 返回关键词数量
        
        Returns:
            关键词列表
        """
        # 简单的关键词提取（基于词频）
        import jieba
        
        # 分词
        words = jieba.lcut(content)
        
        # 过滤停用词和短词
        stop_words = set(['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'])
        filtered_words = [w for w in words if len(w) > 1 and w not in stop_words]
        
        # 统计词频
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 排序并返回top_n
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        keywords = []
        for word, freq in sorted_words[:top_n]:
            keywords.append({
                "word": word,
                "frequency": freq,
                "suitable_for_tag": len(word) <= 10  # 适合作为标签
            })
        
        return keywords
    
    @staticmethod
    def generate_tags(content: str, title: str = "") -> List[str]:
        """
        生成文章标签/话题
        
        Args:
            content: 文章内容
            title: 文章标题
        
        Returns:
            标签列表
        """
        tags = []
        
        # 基于标题提取标签
        if title:
            # 使用jieba提取关键词
            import jieba.analyse
            title_tags = jieba.analyse.extract_tags(title, topK=3, allowPOS=('n', 'ns', 'nt', 'nw', 'nz'))
            tags.extend(title_tags)
        
        # 基于内容提取
        import jieba.analyse
        content_tags = jieba.analyse.extract_tags(content, topK=5, allowPOS=('n', 'ns', 'nt', 'nw', 'nz'))
        tags.extend(content_tags)
        
        # 去重并限制数量
        unique_tags = list(set(tags))[:8]
        
        return unique_tags
    
    @staticmethod
    def calculate_reading_time(content: str) -> Dict[str, Any]:
        """
        计算阅读时间
        
        Args:
            content: 文章内容
        
        Returns:
            阅读时间信息
        """
        # 统计字数
        char_count = len(content.replace(' ', '').replace('\n', ''))
        word_count = len(content.split())
        
        # 计算阅读时间（按300字/分钟）
        reading_minutes = max(1, round(char_count / 300))
        
        return {
            "char_count": char_count,
            "word_count": word_count,
            "reading_minutes": reading_minutes,
            "reading_time_text": f"约{reading_minutes}分钟",
            "difficulty": "简单" if char_count < 800 else "适中" if char_count < 2000 else "深度"
        }
    
    @staticmethod
    def generate_summary(content: str, max_length: int = 150) -> str:
        """
        生成文章摘要
        
        Args:
            content: 文章内容
            max_length: 最大长度
        
        Returns:
            摘要
        """
        # 简单的摘要生成（取前几个句子）
        sentences = re.split(r'[。！？]', content)
        summary = ""
        
        for sentence in sentences:
            if len(summary) + len(sentence) > max_length:
                break
            summary += sentence + "。"
        
        return summary[:max_length] + "..." if len(summary) > max_length else summary


# 服务实例
article_formatter = ArticleFormatter()
