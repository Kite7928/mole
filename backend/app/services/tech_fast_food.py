"""
科技速食写作人设配置
采用"科技速食"写作风格，快速、简洁、有趣
"""

from typing import Dict, Optional


# 写作风格 Prompt
TECH_FAST_FOOD_PROMPT = """
你是一个专业的科技内容创作者，采用"科技速食"写作风格。

## 写作风格要求

### 1. 开篇风格
- **新闻锚点**：用最新的科技新闻作为开场
- **金句开场**：用简洁有力的金句吸引读者
- **悬念开场**：用问题或反问引发思考

### 2. 段落节奏
- **极短段落**：每段 1-3 句话
- **避免长段落**：不超过 100 字
- **多用换行**：增强可读性

### 3. 重点突出
- **加粗标记**：使用 **加粗** 标记重点
- **符号包裹**：用「」或『』包裹关键词
- **列表展示**：用列表展示要点

### 4. 语言风格
- **口语化**：使用日常语言，避免专业术语
- **生动有趣**：用比喻和拟人化手法
- **简洁有力**：用短句表达，避免长句

### 5. 结尾三件套
- **金句总结**：用金句总结全文
- **下期预告**：预告下一期话题
- **互动提问**：引导读者评论互动

## 文章结构示例

```
# [引人注目的标题]

**[金句开场]** 这就对了！

今天要和大家聊的是...

## 1. [第一个观点]

简单来说，就是这个意思。

**重点：** 这是关键点！

## 2. [第二个观点]

「关键词」到底是什么？

简单来说，就是这么回事。

## 总结

**金句：** [总结全文的金句]

**预告：** 下期聊聊[下一个话题]

**互动：** 你怎么看？评论区见！
```

## 注意事项

1. **字数控制**：正文 1500-2000 字
2. **标题长度**：15-25 字
3. **段落数量**：至少 5 个段落
4. **重点标记**：每段至少 1 个重点
5. **互动引导**：结尾必须有互动提问
"""


# 写作风格模板
WRITING_TEMPLATES = {
    "opening": [
        "**{key_point}** 这就对了！",
        "**{key_point}** 真的没想到！",
        "**{key_point}** 今天必须聊聊！",
        "**{key_point}** 你知道吗？",
    ],
    "transition": [
        "简单来说，",
        "具体来说，",
        "说白了，",
        "简单来讲，",
    ],
    "emphasis": [
        "**重点：**",
        "**关键：**",
        "**记住：**",
        "**注意：**",
    ],
    "summary": [
        "**金句：**",
        "**总结：**",
        "**一句话：**",
    ],
    "interaction": [
        "**互动：** 你怎么看？评论区见！",
        "**互动：** 你有不同意见吗？评论区聊聊！",
        "**互动：** 你用过吗？评论区分享你的体验！",
    ],
}


def get_writing_style_prompt() -> str:
    """
    获取写作风格 Prompt
    
    Returns:
        写作风格 Prompt
    """
    return TECH_FAST_FOOD_PROMPT


def get_writing_template(template_type: str, **kwargs) -> str:
    """
    获取写作模板
    
    Args:
        template_type: 模板类型（opening, transition, emphasis, summary, interaction）
        **kwargs: 模板参数
    
    Returns:
        模板内容
    """
    templates = WRITING_TEMPLATES.get(template_type, [])
    if not templates:
        return ""
    
    # 随机选择一个模板（这里选择第一个）
    template = templates[0]
    
    # 替换占位符
    for key, value in kwargs.items():
        template = template.replace(f"{{{key}}}", str(value))
    
    return template


def apply_writing_style(content: str) -> str:
    """
    应用写作风格到内容
    
    Args:
        content: 原始内容
    
    Returns:
        应用写作风格后的内容
    """
    if not content:
        return content
    
    # 分割内容为段落
    paragraphs = content.split('\n\n')
    
    styled_paragraphs = []
    for paragraph in paragraphs:
        # 如果段落过长，尝试分割
        if len(paragraph) > 100:
            sentences = paragraph.split('。')
            styled_paragraphs.extend([s.strip() + '。' for s in sentences if s.strip()])
        else:
            styled_paragraphs.append(paragraph)
    
    # 重新组合
    styled_content = '\n\n'.join(styled_paragraphs)
    
    return styled_content


# 写作风格示例
WRITING_EXAMPLES = {
    "ai": """
# 人工智能改变生活

**AI 已经无处不在** 这就对了！

今天要和大家聊的是人工智能如何改变我们的生活。

## 1. 智能助手

简单来说，就是帮你解决日常问题。

**重点：** 效率提升 10 倍！

## 2. 自动驾驶

「自动驾驶」到底是什么？

简单来讲，就是车自己开。

## 总结

**金句：** AI 不是要取代人类，而是要赋能人类。

**预告：** 下期聊聊 AI 的未来。

**互动：** 你怎么看？评论区见！
""",
    "blockchain": """
# 区块链技术解析

**区块链是信任机器** 真的没想到！

今天要和大家聊聊区块链技术。

## 1. 什么是区块链

简单来说，就是分布式账本。

**重点：** 去中心化是核心！

## 2. 应用场景

「区块链」能做什么？

具体来说，金融、医疗、物流都能用。

## 总结

**金句：** 区块链不是技术革命，而是信任革命。

**预告：** 下期聊聊 Web3。

**互动：** 你怎么看？评论区见！
""",
}


def get_writing_example(topic: str) -> Optional[str]:
    """
    获取写作示例
    
    Args:
        topic: 主题
    
    Returns:
        写作示例，如果没有则返回 None
    """
    return WRITING_EXAMPLES.get(topic.lower())