"""
图片生成API服务
集成DALL-E、Midjourney、Stable Diffusion等图片生成平台
"""
from typing import Dict, List, Optional, Any
import httpx
from ..core.config import settings
from ..core.logger import logger


class ImageGenerationService:
    """图片生成服务"""

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=120.0)

    async def generate_with_dalle(
        self,
        prompt: str,
        size: Optional[str] = None,
        quality: Optional[str] = None,
        n: int = 1
    ) -> List[Dict[str, Any]]:
        """
        使用DALL-E生成图片

        Args:
            prompt: 提示词
            size: 图片尺寸 (256x256, 512x512, 1024x1024, 1792x1024, 1024x1792)
            quality: 图片质量 (standard, hd)
            n: 生成数量

        Returns:
            生成的图片列表
        """
        try:
            if not settings.DALL_E_API_KEY:
                logger.warning("DALL-E API key not configured")
                return await self._get_mock_images(prompt, n)

            size = size or settings.DALL_E_SIZE
            quality = quality or settings.DALL_E_QUALITY

            # 调用DALL-E API
            url = "https://api.openai.com/v1/images/generations"

            headers = {
                "Authorization": f"Bearer {settings.DALL_E_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": settings.DALL_E_MODEL,
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "n": n
            }

            response = await self.http_client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # 解析响应
            images = []
            for item in data.get("data", []):
                images.append({
                    "url": item.get("url"),
                    "revised_prompt": item.get("revised_prompt"),
                    "size": size,
                    "quality": quality,
                    "provider": "dalle"
                })

            return images

        except Exception as e:
            logger.error(f"Error generating with DALL-E: {str(e)}")
            raise

    async def generate_with_midjourney(
        self,
        prompt: str,
        size: str = "1024x1024",
        n: int = 1
    ) -> List[Dict[str, Any]]:
        """
        使用Midjourney生成图片

        Args:
            prompt: 提示词
            size: 图片尺寸
            n: 生成数量

        Returns:
            生成的图片列表
        """
        try:
            if not settings.MIDJOURNEY_API_KEY:
                logger.warning("Midjourney API key not configured")
                return await self._get_mock_images(prompt, n)

            # 调用Midjourney API
            url = f"{settings.MIDJOURNEY_BASE_URL}/imagine"

            headers = {
                "Authorization": f"Bearer {settings.MIDJOURNEY_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "prompt": prompt,
                "size": size,
                "n": n
            }

            response = await self.http_client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # 解析响应
            images = []
            for item in data.get("images", []):
                images.append({
                    "url": item.get("url"),
                    "size": size,
                    "provider": "midjourney"
                })

            return images

        except Exception as e:
            logger.error(f"Error generating with Midjourney: {str(e)}")
            raise

    async def generate_with_stable_diffusion(
        self,
        prompt: str,
        size: str = "1024x1024",
        steps: int = 30,
        cfg_scale: float = 7.5,
        n: int = 1
    ) -> List[Dict[str, Any]]:
        """
        使用Stable Diffusion生成图片

        Args:
            prompt: 提示词
            size: 图片尺寸
            steps: 生成步数
            cfg_scale: CFG缩放因子
            n: 生成数量

        Returns:
            生成的图片列表
        """
        try:
            if not settings.STABLE_DIFFUSION_API_KEY:
                logger.warning("Stable Diffusion API key not configured")
                return await self._get_mock_images(prompt, n)

            # 调用Stable Diffusion API
            url = f"{settings.STABLE_DIFFUSION_BASE_URL}/text-to-image/{settings.STABLE_DIFFUSION_MODEL}"

            headers = {
                "Authorization": f"Bearer {settings.STABLE_DIFFUSION_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": cfg_scale,
                "height": int(size.split("x")[1]),
                "width": int(size.split("x")[0]),
                "steps": steps,
                "samples": n
            }

            response = await self.http_client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # 解析响应
            images = []
            for item in data.get("artifacts", []):
                images.append({
                    "base64": item.get("base64"),
                    "size": size,
                    "steps": steps,
                    "provider": "stable-diffusion"
                })

            return images

        except Exception as e:
            logger.error(f"Error generating with Stable Diffusion: {str(e)}")
            raise

    async def generate_article_cover(
        self,
        topic: str,
        style: str = "professional",
        provider: str = "dalle"
    ) -> Dict[str, Any]:
        """
        生成文章封面图

        Args:
            topic: 文章主题
            style: 风格 (professional, creative, minimal, vibrant)
            provider: 提供商 (dalle, midjourney, stable-diffusion)

        Returns:
            生成的封面图
        """
        try:
            # 构建提示词
            style_prompts = {
                "professional": "professional, clean, modern, minimalist, business",
                "creative": "creative, artistic, colorful, dynamic, expressive",
                "minimal": "minimal, simple, elegant, clean, subtle",
                "vibrant": "vibrant, energetic, bold, colorful, striking"
            }

            prompt = f"Create a professional article cover image about {topic}. Style: {style_prompts.get(style, 'professional')}. High quality, 4K resolution."

            if provider == "dalle":
                images = await self.generate_with_dalle(prompt, size="1024x1024", quality="hd", n=1)
            elif provider == "midjourney":
                images = await self.generate_with_midjourney(prompt, size="1024x1024", n=1)
            elif provider == "stable-diffusion":
                images = await self.generate_with_stable_diffusion(prompt, size="1024x1024", n=1)
            else:
                raise ValueError(f"Unknown provider: {provider}")

            return images[0] if images else {}

        except Exception as e:
            logger.error(f"Error generating article cover: {str(e)}")
            raise

    async def generate_infographic(
        self,
        data: Dict[str, Any],
        style: str = "modern"
    ) -> Dict[str, Any]:
        """
        生成信息图

        Args:
            data: 数据内容
            style: 风格

        Returns:
            生成的信息图
        """
        try:
            # 构建提示词
            prompt = f"Create a professional infographic with the following data: {data}. Style: {style}, clean, modern, easy to understand."

            images = await self.generate_with_dalle(prompt, size="1792x1024", quality="hd", n=1)

            return images[0] if images else {}

        except Exception as e:
            logger.error(f"Error generating infographic: {str(e)}")
            raise

    async def edit_image(
        self,
        image_url: str,
        prompt: str,
        provider: str = "dalle"
    ) -> Dict[str, Any]:
        """
        编辑图片

        Args:
            image_url: 原始图片URL
            prompt: 编辑提示词
            provider: 提供商

        Returns:
            编辑后的图片
        """
        try:
            if provider == "dalle":
                # DALL-E的图片编辑功能
                url = "https://api.openai.com/v1/images/edits"

                headers = {
                    "Authorization": f"Bearer {settings.DALL_E_API_KEY}",
                }

                # 需要下载图片并上传
                # 这里简化处理，实际使用时需要下载图片
                logger.info(f"Editing image with DALL-E: {prompt}")
                return await self._get_mock_images(prompt, 1)[0]

            else:
                raise ValueError(f"Image editing not supported for provider: {provider}")

        except Exception as e:
            logger.error(f"Error editing image: {str(e)}")
            raise

    async def _get_mock_images(
        self,
        prompt: str,
        n: int
    ) -> List[Dict[str, Any]]:
        """模拟图片生成"""
        import random

        mock_images = []
        for i in range(n):
            mock_images.append({
                "url": f"https://via.placeholder.com/1024x1024?text=Mock+Image+{i+1}",
                "prompt": prompt,
                "provider": "mock",
                "size": "1024x1024"
            })

        return mock_images

    async def close(self):
        """关闭客户端"""
        await self.http_client.aclose()


# 全局实例
image_generation_service = ImageGenerationService()