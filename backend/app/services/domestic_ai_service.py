"""
国内AI模型服务
集成通义千问等国内AI模型
"""
from typing import Dict, List, Optional, Any
import httpx
import json
from ..core.config import settings
from ..core.logger import logger


class DomesticAIService:
    """国内AI模型服务"""

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=60.0)

    async def generate_with_qwen(
        self,
        prompt: str,
        model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        使用通义千问生成内容

        Args:
            prompt: 提示词
            model: 模型名称

        Returns:
            生成的内容列表
        """
        try:
            if not settings.QWEN_API_KEY:
                logger.warning("Qwen API key not configured")
                return await self._get_mock_response(prompt)

            model = model or settings.QWEN_MODEL

            # 调用通义千问API
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

            headers = {
                "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model,
                "input": {
                    "messages": [
                        {"role": "system", "content": "你是一个专业的公众号内容创作者。"},
                        {"role": "user", "content": prompt}
                    ]
                },
                "parameters": {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "max_tokens": 4000,
                    "result_format": "message"
                }
            }

            response = await self.http_client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # 解析响应
            content = data["output"]["choices"][0]["message"]["content"]
            return self._parse_generation_response(content)

        except Exception as e:
            logger.error(f"Error generating with Qwen: {str(e)}")
            raise

    async def generate_titles_with_domestic(
        self,
        topic: str,
        count: int = 5,
        model: str = "qwen"
    ) -> List[Dict[str, Any]]:
        """
        使用国内AI模型生成标题

        Args:
            topic: 主题
            count: 生成数量
            model: 模型类型 (qwen)

        Returns:
            标题列表
        """
        try:
            prompt = f"""作为专业的微信公众号编辑，请为以下主题生成 {count} 个吸引人的标题。

主题：{topic}

要求：
1. 标题要具有吸引力和传播性
2. 适合微信公众号平台
3. 长度控制在 15-30 字之间
4. 包含数字、疑问句或感叹句等技巧
5. 避免过于夸张或虚假

请以 JSON 格式返回，格式如下：
{{
  "titles": [
    {{"title": "标题1", "predicted_click_rate": 0.85, "emotion": "强烈"}},
    {{"title": "标题2", "predicted_click_rate": 0.78, "emotion": "中等"}}
  ]
}}"""

            if model == "qwen":
                result = await self.generate_with_qwen(prompt)
            else:
                raise ValueError(f"Unknown model: {model}")

            return result

        except Exception as e:
            logger.error(f"Error generating titles with domestic AI: {str(e)}")
            raise

    async def generate_content_with_domestic(
        self,
        topic: str,
        title: str,
        style: str = "professional",
        length: str = "medium",
        model: str = "qwen"
    ) -> Dict[str, Any]:
        """
        使用国内AI模型生成文章内容

        Args:
            topic: 主题
            title: 标题
            style: 写作风格
            length: 文章长度
            model: 模型类型 (qwen)

        Returns:
            文章内容
        """
        try:
            length_guide = {
                "short": "800-1200 字",
                "medium": "1500-2500 字",
                "long": "3000-5000 字"
            }

            style_guide = {
                "professional": "专业、严谨、深度分析",
                "casual": "轻松、幽默、通俗易懂",
                "emotional": "情感共鸣、故事性强",
                "technical": "技术性强、数据支撑"
            }

            prompt = f"""作为专业的公众号内容创作者，请根据以下信息撰写一篇高质量的文章。

标题：{title}
主题：{topic}
写作风格：{style_guide.get(style, "专业")}
文章长度：{length_guide.get(length, "1500-2500 字")}

要求：
1. 结构清晰，包含引言、正文、结语
2. 内容有深度，避免泛泛而谈
3. 适当引用数据和案例
4. 语言流畅，符合公众号阅读习惯
5. 段落不宜过长，注意排版

请以 JSON 格式返回，格式如下：
{{
  "content": "文章正文内容",
  "summary": "文章摘要（100-200字）",
  "tags": ["标签1", "标签2", "标签3"],
  "quality_score": 0.85
}}"""

            if model == "qwen":
                result = await self.generate_with_qwen(prompt)
            else:
                raise ValueError(f"Unknown model: {model}")

            return result[0] if result else {}

        except Exception as e:
            logger.error(f"Error generating content with domestic AI: {str(e)}")
            raise

    def _parse_generation_response(self, content: str) -> List[Dict[str, Any]]:
        """解析生成响应"""
        try:
            # 尝试解析JSON
            if content.strip().startswith("{"):
                data = json.loads(content)
                if "titles" in data:
                    return data["titles"]
                elif "content" in data:
                    return [data]
                else:
                    return [{"content": content}]
            else:
                return [{"content": content}]
        except json.JSONDecodeError:
            return [{"content": content}]

    async def _get_mock_response(self, prompt: str) -> List[Dict[str, Any]]:
        """模拟响应"""
        import random
        return [{
            "content": f"这是来自国内AI模型的模拟响应。\n\n提示词：{prompt[:100]}...\n\n在实际使用中，这里会返回真实的AI生成内容。",
            "summary": "模拟响应摘要",
            "tags": ["模拟", "示例"],
            "quality_score": random.uniform(0.7, 0.9)
        }]

    async def close(self):
        """关闭客户端"""
        await self.http_client.aclose()


# 全局实例
domestic_ai_service = DomesticAIService()