"""
敏感词审查服务
自动替换平台敏感词，避免限流
"""

from typing import Dict, List
from ..core.logger import logger


# 敏感词映射表
SENSITIVE_WORDS: Dict[str, str] = {
    # 金融相关
    "股票": "权益资产",
    "炒股": "权益资产投资",
    "赚钱": "获取收益",
    "暴富": "实现财务目标",
    "投资回报": "收益表现",
    "理财产品": "资产管理工具",
    
    # 技术相关
    "自动化": "智能联动",
    "AI": "人工智能技术",
    "ChatGPT": "智能对话系统",
    "OpenAI": "智能研究机构",
    "DeepSeek": "深度探索技术",
    
    # 平台相关
    "微信": "社交平台",
    "公众号": "内容平台",
    "朋友圈": "社交圈",
    "抖音": "短视频平台",
    "小红书": "生活方式平台",
    "快手": "视频创作平台",
    
    # 工具相关
    "翻墙": "跨境访问",
    "VPN": "网络加速工具",
    "加速器": "网络优化工具",
    "梯子": "网络连接工具",
    
    # 其他
    "免费": "零成本",
    "破解": "优化",
    "激活码": "授权码",
    "注册码": "授权码",
    "盗版": "非正版",
    "破解版": "优化版",
}


def filter_sensitive_words(content: str) -> str:
    """
    过滤敏感词
    
    Args:
        content: 原始内容
    
    Returns:
        过滤后的内容
    """
    if not content:
        return content
    
    original_content = content
    filtered_content = content
    
    # 遍历敏感词映射表进行替换
    for word, replacement in SENSITIVE_WORDS.items():
        filtered_content = filtered_content.replace(word, replacement)
    
    # 记录替换情况
    if filtered_content != original_content:
        replaced_count = len([word for word in SENSITIVE_WORDS.keys() if word in original_content])
        logger.info(f"敏感词过滤完成，替换了 {replaced_count} 个敏感词")
    
    return filtered_content


def check_sensitive_words(content: str) -> List[str]:
    """
    检查内容中包含的敏感词
    
    Args:
        content: 要检查的内容
    
    Returns:
        包含的敏感词列表
    """
    if not content:
        return []
    
    found_words = []
    for word in SENSITIVE_WORDS.keys():
        if word in content:
            found_words.append(word)
    
    return found_words


def get_replacement(word: str) -> str:
    """
    获取敏感词的替换词
    
    Args:
        word: 敏感词
    
    Returns:
        替换词，如果不在映射表中则返回原词
    """
    return SENSITIVE_WORDS.get(word, word)


def add_sensitive_word(word: str, replacement: str) -> None:
    """
    添加自定义敏感词
    
    Args:
        word: 敏感词
        replacement: 替换词
    """
    SENSITIVE_WORDS[word] = replacement
    logger.info(f"添加自定义敏感词: {word} -> {replacement}")


def remove_sensitive_word(word: str) -> bool:
    """
    移除敏感词
    
    Args:
        word: 要移除的敏感词
    
    Returns:
        是否成功移除
    """
    if word in SENSITIVE_WORDS:
        del SENSITIVE_WORDS[word]
        logger.info(f"移除敏感词: {word}")
        return True
    return False


def get_all_sensitive_words() -> Dict[str, str]:
    """
    获取所有敏感词映射
    
    Returns:
        敏感词映射表
    """
    return SENSITIVE_WORDS.copy()