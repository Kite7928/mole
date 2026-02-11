"""
自媒体写作模板服务
提供多种类型的文章模板和爆款标题生成策略
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import random


class WritingTemplate(BaseModel):
    """写作模板"""
    id: str
    name: str
    description: str
    category: str
    structure: List[Dict[str, str]]
    tips: List[str]
    example: str


class TitleFormula(BaseModel):
    """标题公式"""
    id: str
    name: str
    description: str
    formula: str
    examples: List[str]
    click_boost: int  # 预估点击率提升百分比


class WritingTemplateService:
    """写作模板服务"""
    
    # 写作模板库
    TEMPLATES = {
        "tech_review": WritingTemplate(
            id="tech_review",
            name="科技评测",
            description="适合产品评测、科技测评类文章",
            category="科技",
            structure=[
                {"section": "开篇引入", "content": "用场景或痛点引入产品，制造期待感", "length": "100-150字"},
                {"section": "产品概述", "content": "介绍产品基本信息、定位、核心卖点", "length": "150-200字"},
                {"section": "详细体验", "content": "分维度详细描述使用体验（外观/功能/性能）", "length": "400-600字"},
                {"section": "优缺点分析", "content": "客观分析产品优势和不足", "length": "200-300字"},
                {"section": "购买建议", "content": "给出明确的购买建议和适用人群", "length": "100-150字"},
                {"section": "互动引导", "content": "引导评论、提问或分享", "length": "50字"},
            ],
            tips=[
                "多用数据对比，增加说服力",
                "配图要精美，展示产品细节",
                "避免过于专业的术语，让普通用户能看懂",
                "真实体验最重要，不要硬吹",
            ],
            example="""【开头】作为一个每天通勤2小时的打工人，我一直在找一款能真正降噪的耳机...
【概述】今天测评的是XXX品牌的最新款降噪耳机，售价999元...
【体验】首先说降噪效果，我在地铁上实测..."""
        ),
        "tutorial": WritingTemplate(
            id="tutorial",
            name="干货教程",
            description="适合技能教学、方法分享类文章",
            category="教育",
            structure=[
                {"section": "痛点引入", "content": "描述目标用户的问题和痛点", "length": "100-150字"},
                {"section": "方法预告", "content": "简要介绍今天要分享的方法和预期效果", "length": "100-150字"},
                {"section": "原理解析", "content": "解释为什么要这样做，建立信任", "length": "200-300字"},
                {"section": "详细步骤", "content": "分步骤详细讲解操作方法，配图说明", "length": "400-600字"},
                {"section": "案例展示", "content": "展示实际应用效果和成功案例", "length": "150-200字"},
                {"section": "注意事项", "content": "提醒常见错误和注意事项", "length": "100-150字"},
                {"section": "总结", "content": "总结要点，鼓励行动", "length": "100字"},
            ],
            tips=[
                "步骤要详细到小白也能看懂",
                "多用截图或图示辅助说明",
                "提供可操作的行动清单",
                "分享真实案例增加可信度",
            ],
            example="""【痛点】很多人做PPT总是花很多时间，效果还不行...
【方法】今天分享一个3分钟做出高级感PPT的方法...
【步骤】第一步，打开XXX工具..."""
        ),
        "hot_comment": WritingTemplate(
            id="hot_comment",
            name="热点评论",
            description="适合时事热点、行业动态评论",
            category="观点",
            structure=[
                {"section": "事件回顾", "content": "简要回顾热点事件，确保读者了解背景", "length": "150-200字"},
                {"section": "观点表达", "content": "明确表达自己的观点或立场", "length": "100-150字"},
                {"section": "论据支撑", "content": "用数据、案例、专家观点支撑论点", "length": "300-400字"},
                {"section": "深度分析", "content": "分析事件背后的原因和影响", "length": "200-300字"},
                {"section": "趋势预测", "content": "预测后续发展趋势", "length": "100-150字"},
                {"section": "互动引导", "content": "邀请读者表达观点", "length": "50字"},
            ],
            tips=[
                "观点要明确，不要模棱两可",
                "论据要真实可靠，不要造谣",
                "避免极端言论，保持理性",
                "及时发布，热点不等人",
            ],
            example="""【回顾】昨天，XXX公司突然宣布...
【观点】我认为这次事件背后反映出..."""
        ),
        "story": WritingTemplate(
            id="story",
            name="情感故事",
            description="适合个人经历、情感故事分享",
            category="情感",
            structure=[
                {"section": "场景设定", "content": "用生动的场景描写吸引读者", "length": "150-200字"},
                {"section": "人物介绍", "content": "介绍故事主角和背景", "length": "100-150字"},
                {"section": "冲突发展", "content": "描述遇到的困难或矛盾", "length": "200-300字"},
                {"section": "高潮转折", "content": "故事的高潮部分，情绪最强烈的点", "length": "200-300字"},
                {"section": "结局收束", "content": "故事的结局和后续", "length": "150-200字"},
                {"section": "感悟升华", "content": "分享感悟和人生道理", "length": "100-150字"},
            ],
            tips=[
                "开头要有画面感，让读者身临其境",
                "情感要真实，不要刻意煽情",
                "多用对话增加真实感",
                "结尾升华要自然，不要生硬说教",
            ],
            example="""【场景】那是一个下雨的傍晚，我独自站在..."""
        ),
        "list": WritingTemplate(
            id="list",
            name="清单体",
            description="适合推荐、盘点、合集类文章",
            category="实用",
            structure=[
                {"section": "痛点引入", "content": "说明为什么需要这份清单", "length": "100-150字"},
                {"section": "清单预告", "content": "简要介绍清单内容和价值", "length": "100字"},
                {"section": "清单内容", "content": "分点详细介绍每个项目", "length": "500-800字"},
                {"section": "总结推荐", "content": "总结并给出选择建议", "length": "100-150字"},
            ],
            tips=[
                "数字明确，让读者有预期",
                "每个点要有信息量，不要凑数",
                "配图精美，视觉效果好",
                "最后给出明确的选择建议",
            ],
            example="""【引入】很多人都在问，2024年最值得买的手机有哪些？
【清单】1. iPhone 15 Pro - 适合..."""
        ),
    }
    
    # 爆款标题公式
    TITLE_FORMULAS = [
        TitleFormula(
            id="number",
            name="数字法",
            description="用具体数字增加可信度和吸引力",
            formula="数字 + 结果/方法 + 人群",
            examples=[
                "3个技巧让你在30天内涨粉10000",
                "5款2024年最值得买的手机",
                "10年经验总结：8个职场晋升秘诀",
            ],
            click_boost=35
        ),
        TitleFormula(
            id="suspense",
            name="悬念法",
            description="制造悬念引发好奇心",
            formula="省略关键信息 + 强调重要性",
            examples=[
                "原来这才是高效学习的正确姿势...",
                "看完这个，我终于明白为什么你总是加班",
                "这个方法让我收入翻倍，后悔没早知道",
            ],
            click_boost=45
        ),
        TitleFormula(
            id="contrast",
            name="对比法",
            description="通过对比制造冲突感",
            formula="A vs B + 结果差异",
            examples=[
                "月薪3000和月薪30000的人，区别就在这3点",
                "同样是努力，为什么别人成功了你还原地踏步？",
                "聪明人都在做这件事，只有你还在...",
            ],
            click_boost=40
        ),
        TitleFormula(
            id="pain_point",
            name="痛点法",
            description="直击用户痛点引发共鸣",
            formula="痛点描述 + 解决方案暗示",
            examples=[
                "为什么你总是存不下钱？看完这篇你就懂了",
                "工作效率低？这5个工具让你事半功倍",
                "总是失眠怎么办？这个方法亲测有效",
            ],
            click_boost=38
        ),
        TitleFormula(
            id="authority",
            name="权威法",
            description="借助权威增加可信度",
            formula="权威背书 + 核心内容",
            examples=[
                "马云都在用的学习方法，效率提升300%",
                "哈佛研究：成功人士都有这5个习惯",
                "百万博主都在用的涨粉秘籍",
            ],
            click_boost=42
        ),
        TitleFormula(
            id="how_to",
            name="How to法",
            description="直接告诉读者能获得什么",
            formula="如何 + 获得某个结果",
            examples=[
                "如何在30天内学会Python？",
                "如何写出阅读量10万+的文章？",
                "如何在不加班的情况下完成工作？",
            ],
            click_boost=33
        ),
        TitleFormula(
            id="emotional",
            name="情绪法",
            description="激发读者情绪共鸣",
            formula="强烈情绪词 + 事件/观点",
            examples=[
                "太震惊了！原来我们一直被误导",
                "扎心了！这才是成年人世界的真相",
                "愤怒！这种套路你还在上当吗？",
            ],
            click_boost=50
        ),
        TitleFormula(
            id="exclusive",
            name="独家法",
            description="制造稀缺感和独家感",
            formula="独家/内部/揭秘 + 核心内容",
            examples=[
                "内部资料流出：2024年行业趋势预测",
                "独家揭秘：网红背后的真实生活",
                "只有1%的人知道的赚钱方法",
            ],
            click_boost=47
        ),
    ]
    
    @classmethod
    def get_template(cls, template_id: str) -> Optional[WritingTemplate]:
        """获取指定模板"""
        return cls.TEMPLATES.get(template_id)
    
    @classmethod
    def get_all_templates(cls) -> List[WritingTemplate]:
        """获取所有模板"""
        return list(cls.TEMPLATES.values())
    
    @classmethod
    def get_templates_by_category(cls, category: str) -> List[WritingTemplate]:
        """按分类获取模板"""
        return [t for t in cls.TEMPLATES.values() if t.category == category]
    
    @classmethod
    def get_title_formulas(cls) -> List[TitleFormula]:
        """获取所有标题公式"""
        return cls.TITLE_FORMULAS
    
    @classmethod
    def generate_title_suggestions(cls, topic: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        基于爆款公式生成标题建议
        
        Args:
            topic: 文章主题
            count: 生成数量
        
        Returns:
            标题建议列表
        """
        suggestions = []
        
        # 随机选择不同的公式
        selected_formulas = random.sample(cls.TITLE_FORMULAS, min(count, len(cls.TITLE_FORMULAS)))
        
        for formula in selected_formulas:
            # 根据公式生成标题
            title = cls._apply_title_formula(topic, formula)
            suggestions.append({
                "title": title,
                "formula": formula.name,
                "formula_id": formula.id,
                "description": formula.description,
                "click_rate": 70 + formula.click_boost + random.randint(-10, 10),
                "tips": f"使用{formula.name}，预估点击率提升{formula.click_boost}%"
            })
        
        # 按点击率排序
        suggestions.sort(key=lambda x: x["click_rate"], reverse=True)
        return suggestions
    
    @classmethod
    def _apply_title_formula(cls, topic: str, formula: TitleFormula) -> str:
        """应用标题公式生成标题"""
        if formula.id == "number":
            numbers = [3, 5, 7, 10]
            return f"{random.choice(numbers)}个{topic}技巧，让你事半功倍"
        elif formula.id == "suspense":
            return f"原来这才是{topic}的真相..."
        elif formula.id == "contrast":
            return f"懂{topic}和不懂{topic}的人，差距竟然这么大"
        elif formula.id == "pain_point":
            return f"{topic}总是做不好？这个方法让你轻松解决"
        elif formula.id == "authority":
            authorities = ["专家", "百万博主", "行业大咖", "成功人士"]
            return f"{random.choice(authorities)}都在用的{topic}方法"
        elif formula.id == "how_to":
            return f"如何快速掌握{topic}？"
        elif formula.id == "emotional":
            emotions = ["震惊", "扎心", "太真实了", "后悔没早知道"]
            return f"{random.choice(emotions)}！关于{topic}的真相"
        elif formula.id == "exclusive":
            return f"独家揭秘：{topic}行业不为人知的秘密"
        else:
            return f"关于{topic}，你必须知道的事"
    
    @classmethod
    def get_template_prompt(cls, template_id: str, topic: str) -> str:
        """
        根据模板生成AI写作提示词
        
        Args:
            template_id: 模板ID
            topic: 写作主题
        
        Returns:
            AI提示词
        """
        template = cls.get_template(template_id)
        if not template:
            return f"请写一篇关于{topic}的文章"
        
        prompt = f"请按照以下结构写一篇关于'{topic}'的{template.name}类文章：\n\n"
        
        for i, section in enumerate(template.structure, 1):
            prompt += f"{i}. {section['section']}（{section['length']}）：{section['content']}\n"
        
        prompt += f"\n写作要求：\n"
        for tip in template.tips:
            prompt += f"- {tip}\n"
        
        prompt += f"\n参考示例：\n{template.example}\n"
        prompt += f"\n注意：文章要适合微信公众号发布，语言通俗易懂，段落不要太长，适合手机阅读。"
        
        return prompt


# 服务实例
writing_template_service = WritingTemplateService()
