from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
import anthropic
import httpx
from ..core.config import settings
from ..core.logger import logger


class AIWriterService:
    """
    AI writing service supporting multiple LLM providers.
    """

    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.http_client = None

        # Initialize clients based on configuration
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )
            logger.info("OpenAI client initialized")

        if settings.CLAUDE_API_KEY:
            self.anthropic_client = anthropic.AsyncAnthropic(
                api_key=settings.CLAUDE_API_KEY,
                base_url=settings.CLAUDE_BASE_URL
            )
            logger.info("Anthropic client initialized")

        # HTTP client for other APIs
        self.http_client = httpx.AsyncClient(timeout=60.0)

    async def generate_titles(
        self,
        topic: str,
        count: int = 5,
        model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple article titles based on topic.
        """
        try:
            prompt = self._build_title_prompt(topic, count)

            if model == "deepseek" or (not model and settings.DEEPSEEK_API_KEY):
                titles = await self._generate_with_deepseek(prompt, count)
            elif model == "claude" or (not model and settings.CLAUDE_API_KEY):
                titles = await self._generate_with_claude(prompt, count)
            elif model == "gemini" or (not model and settings.GEMINI_API_KEY):
                titles = await self._generate_with_gemini(prompt, count)
            else:
                titles = await self._generate_with_openai(prompt, count)

            return titles

        except Exception as e:
            logger.error(f"Error generating titles: {str(e)}")
            raise

    async def generate_content(
        self,
        topic: str,
        title: str,
        style: str = "professional",
        length: str = "medium",
        enable_research: bool = False,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate article content based on topic and title.
        """
        try:
            prompt = self._build_content_prompt(topic, title, style, length, enable_research)

            if model == "deepseek" or (not model and settings.DEEPSEEK_API_KEY):
                content = await self._generate_with_deepseek(prompt, 1)
            elif model == "claude" or (not model and settings.CLAUDE_API_KEY):
                content = await self._generate_with_claude(prompt, 1)
            elif model == "gemini" or (not model and settings.GEMINI_API_KEY):
                content = await self._generate_with_gemini(prompt, 1)
            else:
                content = await self._generate_with_openai(prompt, 1)

            return content[0] if content else {}

        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise

    async def optimize_content(
        self,
        content: str,
        optimization_type: str = "enhance",
        model: Optional[str] = None
    ) -> str:
        """
        Optimize or modify content based on type.
        """
        try:
            prompt = self._build_optimization_prompt(content, optimization_type)

            if model == "deepseek" or (not model and settings.DEEPSEEK_API_KEY):
                result = await self._generate_with_deepseek(prompt, 1)
            elif model == "claude" or (not model and settings.CLAUDE_API_KEY):
                result = await self._generate_with_claude(prompt, 1)
            elif model == "gemini" or (not model and settings.GEMINI_API_KEY):
                result = await self._generate_with_gemini(prompt, 1)
            else:
                result = await self._generate_with_openai(prompt, 1)

            return result[0].get("content", content) if result else content

        except Exception as e:
            logger.error(f"Error optimizing content: {str(e)}")
            return content

    def _build_title_prompt(self, topic: str, count: int) -> str:
        """Build prompt for title generation."""
        return f"""作为专业的微信公众号编辑，请为以下主题生成 {count} 个吸引人的标题。

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

    def _build_content_prompt(
        self,
        topic: str,
        title: str,
        style: str,
        length: str,
        enable_research: bool
    ) -> str:
        """Build prompt for content generation."""
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

        research_note = ""
        if enable_research:
            research_note = "请结合最新的行业数据和案例，进行深度研究和分析。"

        return f"""作为专业的公众号内容创作者，请根据以下信息撰写一篇高质量的文章。

标题：{title}
主题：{topic}
写作风格：{style_guide.get(style, "专业")}
文章长度：{length_guide.get(length, "1500-2500 字")}
{research_note}

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

    def _build_optimization_prompt(self, content: str, optimization_type: str) -> str:
        """Build prompt for content optimization."""
        instructions = {
            "enhance": "增强文章的可读性和吸引力，优化语言表达",
            "shorten": "精简文章内容，去除冗余，保留核心信息",
            "expand": "扩展文章内容，增加更多细节和案例",
            "polish": "润色文章，改善语言流畅度和专业性",
            "add_data": "在适当位置添加数据支撑和事实依据"
        }

        return f"""请对以下文章进行优化。

优化目标：{instructions.get(optimization_type, "增强文章质量")}

文章内容：
{content}

请直接返回优化后的文章内容，不要包含任何解释或说明。"""

    async def _generate_with_openai(
        self,
        prompt: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate content using OpenAI API."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")

        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的公众号内容创作者。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            import json
            result = json.loads(content)

            if "titles" in result:
                return result["titles"]
            elif "content" in result:
                return [result]
            else:
                return []

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    async def _generate_with_deepseek(
        self,
        prompt: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate content using DeepSeek API."""
        if not settings.DEEPSEEK_API_KEY:
            raise ValueError("DeepSeek API key not configured")

        try:
            response = await self.http_client.post(
                f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.DEEPSEEK_MODEL,
                    "messages": [
                        {"role": "system", "content": "你是一个专业的公众号内容创作者。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4000,
                    "response_format": {"type": "json_object"}
                },
                timeout=60.0
            )

            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

            import json
            result = json.loads(content)

            if "titles" in result:
                return result["titles"]
            elif "content" in result:
                return [result]
            else:
                return []

        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            raise

    async def _generate_with_claude(
        self,
        prompt: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate content using Claude API."""
        if not self.anthropic_client:
            raise ValueError("Claude client not initialized")

        try:
            response = await self.anthropic_client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = response.content[0].text
            import json
            result = json.loads(content)

            if "titles" in result:
                return result["titles"]
            elif "content" in result:
                return [result]
            else:
                return []

        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise

    async def _generate_with_gemini(
        self,
        prompt: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate content using Gemini API."""
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")

        try:
            response = await self.http_client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 4000
                    }
                },
                timeout=60.0
            )

            response.raise_for_status()
            data = response.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"]

            import json
            result = json.loads(content)

            if "titles" in result:
                return result["titles"]
            elif "content" in result:
                return [result]
            else:
                return []

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise

    async def close(self):
        """Close all clients."""
        if self.http_client:
            await self.http_client.aclose()


# Global instance
ai_writer_service = AIWriterService()