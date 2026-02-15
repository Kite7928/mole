"""
图片生成API服务
集成DALL-E、Midjourney、Stable Diffusion等图片生成平台
"""
from typing import Dict, List, Optional, Any
import httpx
import hashlib
from ..core.config import settings
from ..core.logger import logger
from .cache import ai_response_cache
from .image_provider_manager import image_provider_manager


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
            logger.warning(f"DALL-E API 失败，降级到本地图片生成")
            return await self._get_mock_images(prompt, n)

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
            logger.warning(f"Midjourney API 失败，降级到本地图片生成")
            return await self._get_mock_images(prompt, n)

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
            logger.warning(f"Stable Diffusion API 失败，降级到本地图片生成")
            return await self._get_mock_images(prompt, n)

    async def generate_with_gemini(
        self,
        prompt: str,
        size: str = "1024x1024",
        n: int = 1
    ) -> List[Dict[str, Any]]:
        """
        使用 Gemini 生成图片（通过第三方API）

        Args:
            prompt: 提示词
            size: 图片尺寸
            n: 生成数量

        Returns:
            生成的图片列表
        """
        try:
            if not settings.GEMINI_API_KEY:
                logger.warning("Gemini API key not configured")
                return await self._get_mock_images(prompt, n)

            # 调用第三方 Gemini API（兼容 OpenAI 格式）
            url = f"{settings.GEMINI_BASE_URL}/images/generations"

            headers = {
                "Authorization": f"Bearer {settings.GEMINI_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": settings.GEMINI_MODEL,
                "prompt": prompt,
                "size": size,
                "n": n
            }

            response = await self.http_client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # 解析响应（OpenAI 格式）
            images = []
            for item in data.get("data", []):
                images.append({
                    "url": item.get("url"),
                    "revised_prompt": item.get("revised_prompt"),
                    "size": size,
                    "provider": "gemini"
                })

            return images

        except Exception as e:
            logger.error(f"Error generating with Gemini: {str(e)}")
            logger.warning(f"Gemini API 失败，降级到本地图片生成")
            return await self._get_mock_images(prompt, n)

    async def generate_with_cogview(
        self,
        prompt: str,
        size: str = "1024x1024",
        n: int = 1
    ) -> List[Dict[str, Any]]:
        """
        使用 Cogview-3-Flash 生成图片（智谱AI）

        Args:
            prompt: 提示词
            size: 图片尺寸 (支持的尺寸: 1024x1024, 768x1344, 864x864, 1344x768)
            n: 生成数量 (目前仅支持1)

        Returns:
            生成的图片列表
        """
        try:
            if not settings.COGVIEW_API_KEY:
                logger.warning("Cogview API key not configured")
                return await self._get_mock_images(prompt, n)

            # 智谱AI的API格式
            url = settings.COGVIEW_BASE_URL

            headers = {
                "Authorization": f"Bearer {settings.COGVIEW_API_KEY}",
                "Content-Type": "application/json"
            }

            # Cogview-3-Flash 支持的参数
            payload = {
                "model": settings.COGVIEW_MODEL,
                "prompt": prompt,
                "size": size,
                "n": n
            }

            response = await self.http_client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # 解析响应
            images = []
            if "data" in data:
                for item in data.get("data", []):
                    images.append({
                        "url": item.get("url") or item.get("b64_json"),
                        "revised_prompt": item.get("revised_prompt"),
                        "size": size,
                        "provider": "cogview"
                    })

            return images

        except Exception as e:
            logger.error(f"Error generating with Cogview: {str(e)}")
            logger.warning(f"Cogview API 失败，降级到本地图片生成")
            # 降级到本地图片生成
            return await self._get_mock_images(prompt, n)

    async def generate_article_cover(
        self,
        topic: str,
        style: str = "professional",
        provider: str = "dalle"
    ) -> Dict[str, Any]:
        """
        生成文章封面图（带缓存）

        Args:
            topic: 文章主题
            style: 风格 (professional, creative, minimal, vibrant)
            provider: 提供商 (dalle, midjourney, stable-diffusion, gemini, cogview)

        Returns:
            生成的封面图
        """
        # 首先尝试使用新的图片提供商管理器
        try:
            from ..core.database import async_session_maker
            from pathlib import Path
            async with async_session_maker() as db:
                cover_path = await image_provider_manager.generate_cover(
                    db=db,
                    title=topic,
                    width=900,
                    height=500,
                    style=style
                )
                if cover_path:
                    logger.info(f"使用新图片提供商生成封面图成功: {cover_path}")
                    # 将本地路径转换为可访问的 URL
                    # 统一使用正斜杠，并只保留文件名
                    cover_path = cover_path.replace('\\', '/')
                    filename = cover_path.split('/')[-1]
                    # 返回 uploads 目录下的相对路径
                    url_path = f"uploads/{filename}"
                    return {
                        "url": url_path,
                        "prompt": topic,
                        "provider": "image_provider_manager"
                    }
        except Exception as e:
            logger.warning(f"新图片提供商生成失败，回退到旧方法: {e}")

        # image_provider_manager 失败，使用 mock 图片
        logger.warning("图片提供商生成失败，使用 mock 图片")
        results = await self._get_mock_images(topic, 1)
        return results[0] if results else None

    async def generate_batch_article_covers(
        self,
        topic: str,
        style: str = "professional",
        provider: str = "dalle",
        n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        批量生成文章封面图

        Args:
            topic: 文章主题
            style: 风格 (professional, creative, minimal, vibrant)
            provider: 提供商 (dalle, midjourney, stable-diffusion, gemini, cogview)
            n: 生成数量（1-5）

        Returns:
            生成的封面图列表
        """
        try:
            # 限制生成数量
            n = min(max(n, 1), 5)
            
            # 生成缓存键
            cache_key = f"image:batch:{hashlib.md5(f'{topic}:{style}:{provider}:{n}'.encode()).hexdigest()}"
            
            # 尝试从缓存获取
            cached_images = ai_response_cache.get(cache_key)
            if cached_images and len(cached_images) >= n:
                logger.info(f"使用缓存的批量封面图: {topic} (n={n})")
                return cached_images[:n]
            
            # 构建提示词
            style_prompts = {
                "professional": "professional, clean, modern, minimalist, business",
                "creative": "creative, artistic, colorful, dynamic, expressive",
                "minimal": "minimal, simple, elegant, clean, subtle",
                "vibrant": "vibrant, energetic, bold, colorful, striking"
            }

            prompt = f"Create a professional article cover image about {topic}. Style: {style_prompts.get(style, 'professional')}. High quality, 4K resolution."

            if provider == "dalle":
                images = await self.generate_with_dalle(prompt, size="1024x1024", quality="hd", n=n)
            elif provider == "midjourney":
                images = await self.generate_with_midjourney(prompt, size="1024x1024", n=n)
            elif provider == "stable-diffusion":
                images = await self.generate_with_stable_diffusion(prompt, size="102x1024", n=n)
            elif provider == "gemini":
                images = await self.generate_with_gemini(prompt, size="1024x1024", n=n)
            elif provider == "cogview":
                images = await self.generate_with_cogview(prompt, size="1024x1024", n=n)
            else:
                raise ValueError(f"Unknown provider: {provider}")

            # 保存到缓存（24小时）
            if images:
                ai_response_cache.set(cache_key, images, ttl=86400)
                logger.info(f"批量封面图已缓存: {topic} (n={n})")
            
            return images

        except Exception as e:
            logger.error(f"Error generating batch article covers: {str(e)}")
            raise

    def analyze_topic_complexity(self, topic: str) -> str:
        """
        分析主题复杂度，智能选择最优模型

        Args:
            topic: 文章主题

        Returns:
            推荐的模型 (mock, cogview, dalle)
        """
        # 简单主题关键词（使用模拟模式）
        simple_keywords = ['测试', '示例', 'demo', 'test', '简单', '基础', '入门']
        if any(keyword in topic.lower() for keyword in simple_keywords):
            return 'mock'
        
        # 复杂主题关键词（使用DALL-E 3）
        complex_keywords = ['复杂', '详细', '高级', '专业', '深度', 'comprehensive', 'detailed']
        if any(keyword in topic.lower() for keyword in complex_keywords):
            return 'dalle'
        
        # 默认使用Cogview（性价比高）
        return 'cogview'

    def enhance_prompt(
        self,
        topic: str,
        style: str = "professional"
    ) -> str:
        """
        智能优化提示词，提高图片质量

        Args:
            topic: 原始主题
            style: 图片风格

        Returns:
            优化后的提示词
        """
        # 风格增强词库
        style_enhancements = {
            "professional": {
                "keywords": ["professional", "clean", "modern", "minimalist", "business", "high-quality", "4K resolution", "sharp details", "corporate style"],
                "elements": ["clean layout", "typography", "modern design", "business elements"],
                "atmosphere": "professional, trustworthy, modern, sophisticated"
            },
            "creative": {
                "keywords": ["creative", "artistic", "colorful", "dynamic", "expressive", "bold", "unique", "eye-catching", "vibrant colors"],
                "elements": ["artistic composition", "dynamic shapes", "color gradient", "creative patterns"],
                "atmosphere": "creative, inspiring, energetic, innovative"
            },
            "minimal": {
                "keywords": ["minimal", "simple", "elegant", "clean", "subtle", "refined", "sophisticated", "white space", "clean lines"],
                "elements": ["simple shapes", "clean typography", "minimal graphics", "elegant composition"],
                "atmosphere": "minimal, elegant, refined, sophisticated"
            },
            "vibrant": {
                "keywords": ["vibrant", "energetic", "bold", "colorful", "striking", "dynamic", "intense", "lively", "color palette"],
                "elements": ["vibrant colors", "dynamic composition", "bold shapes", "color contrast"],
                "atmosphere": "vibrant, energetic, bold, lively"
            }
        }
        
        style_info = style_enhancements.get(style, style_enhancements["professional"])
        
        # 构建基础提示词
        base_prompt = f"Create a {style} article cover image about {topic}"
        
        # 添加关键词
        keywords_str = ", ".join(style_info["keywords"][:5])
        enhanced_prompt = f"{base_prompt}. Style: {keywords_str}"
        
        # 添加具体要求
        requirements = [
            "High quality",
            "4K resolution",
            "Sharp details",
            "Professional lighting",
            "Good composition",
            "Suitable for articles"
        ]
        
        enhanced_prompt += f". Requirements: {', '.join(requirements)}"
        
        # 添加氛围描述
        enhanced_prompt += f". Atmosphere: {style_info['atmosphere']}"
        
        logger.info(f"提示词已优化: {topic} -> {len(enhanced_prompt)} 字符")
        
        return enhanced_prompt

    async def generate_article_cover_smart(
        self,
        topic: str,
        style: str = "professional",
        provider: str = "auto"
    ) -> Dict[str, Any]:
        """
        智能生成文章封面图（自动选择最优模型 + 优化提示词）

        Args:
            topic: 文章主题
            style: 风格
            provider: 提供商（auto表示自动选择）

        Returns:
            生成的封面图
        """
        # 如果指定了provider，直接使用
        if provider != "auto":
            # 优化提示词
            enhanced_prompt = self.enhance_prompt(topic, style)
            
            # 替换原始提示词
            style_prompts = {
                "professional": "professional, clean, modern, minimalist, business",
                "creative": "creative, artistic, colorful, dynamic, expressive",
                "minimal": "minimal, simple, elegant, clean, subtle",
                "vibrant": "vibrant, energetic, bold, colorful, striking"
            }
            
            # 生成缓存键
            cache_key = f"image:cover:{hashlib.md5(f'{enhanced_prompt}:{provider}'.encode()).hexdigest()}"
            
            # 尝试从缓存获取
            cached_image = ai_response_cache.get(cache_key)
            if cached_image:
                logger.info(f"使用缓存的优化封面图: {topic}")
                return cached_image
            
            # 调用各提供商
            if provider == "dalle":
                images = await self.generate_with_dalle(enhanced_prompt, size="1024x1024", quality="hd", n=1)
            elif provider == "midjourney":
                images = await self.generate_with_midjourney(enhanced_prompt, size="1024x1024", n=1)
            elif provider == "stable-diffusion":
                images = await self.generate_with_stable_diffusion(enhanced_prompt, size="1024x1024", n=1)
            elif provider == "gemini":
                images = await self.generate_with_gemini(enhanced_prompt, size="1024x1024", n=1)
            elif provider == "cogview":
                images = await self.generate_with_cogview(enhanced_prompt, size="1024x1024", n=1)
            else:
                raise ValueError(f"Unknown provider: {provider}")

            result = images[0] if images else {}
            
            # 保存到缓存
            if result:
                ai_response_cache.set(cache_key, result, ttl=86400)
                logger.info(f"优化封面图已缓存: {topic}")
            
            return result
        
        # 智能选择最优模型
        recommended_provider = self.analyze_topic_complexity(topic)
        logger.info(f"智能选择模型: {recommended_provider} (主题: {topic})")
        
        return await self.generate_article_cover_smart(topic, style, recommended_provider)

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
        """生成精美的封面图"""
        from PIL import Image, ImageDraw, ImageFont
        from pathlib import Path
        import hashlib
        import random
        
        mock_images = []
        
        # 风格配置
        colors = [
            '#2C3E50', '#E74C3C', '#3498DB', '#9B59B6', '#1ABC9C', '#F39C12'
        ]
        
        for i in range(n):
            try:
                # 选择颜色
                bg_color = random.choice(colors)
                text_color = '#FFFFFF' if bg_color != '#ECF0F1' else '#2C3E50'
                accent_color = random.choice(colors)
                
                # 创建图片
                img = Image.new('RGB', (900, 500), color=bg_color)
                draw = ImageDraw.Draw(img)
                
                # 添加装饰图案
                for j in range(5):
                    x = random.randint(0, 100)
                    y = random.randint(0, 100)
                    r = random.randint(5, 20)
                    draw.ellipse([x-r, y-r, x+r, y+r], fill=accent_color)
                
                for j in range(5):
                    x = random.randint(800, 900)
                    y = random.randint(400, 500)
                    r = random.randint(5, 20)
                    draw.ellipse([x-r, y-r, x+r, y+r], fill=accent_color)
                
                # 添加标题 - 尝试使用支持中文的字体
                font = None
                font_paths = [
                    'C:/Windows/Fonts/simhei.ttf',  # 黑体
                    'C:/Windows/Fonts/simsun.ttc',  # 宋体
                    'C:/Windows/Fonts/msyh.ttc',    # 微软雅黑
                    'C:/Windows/Fonts/arial.ttf',   # Arial
                ]
                for font_path in font_paths:
                    try:
                        font = ImageFont.truetype(font_path, 50)
                        break
                    except:
                        continue
                if not font:
                    font = ImageFont.load_default()
                
                # 从提示词中提取文章标题（在单引号之间的中文内容）
                import re
                match = re.search(r"about '([^']+)'", prompt)
                if match:
                    title = match.group(1)
                else:
                    # 降级方案：提取前20个字符
                    title = prompt[:30] if len(prompt) > 30 else prompt
                
                bbox = draw.textbbox((0, 0), title, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (900 - text_width) / 2
                y = (500 - text_height) / 2 - 30
                
                draw.text((x, y), title, fill=text_color, font=font)
                
                # 添加副标题 - 使用相同字体但更小字号
                font_small = None
                for font_path in font_paths:
                    try:
                        font_small = ImageFont.truetype(font_path, 24)
                        break
                    except:
                        continue
                if not font_small:
                    font_small = ImageFont.load_default()
                
                subtitle = 'AI 智能生成'
                bbox_small = draw.textbbox((0, 0), subtitle, font=font_small)
                text_width_small = bbox_small[2] - bbox_small[0]
                
                x_small = (900 - text_width_small) / 2
                draw.text((x_small, 380), subtitle, fill=text_color, font=font_small)
                
                # 保存图片（添加时间戳确保唯一性）
                import time
                upload_dir = Path(settings.UPLOAD_DIR)
                upload_dir.mkdir(exist_ok=True)
                
                # 使用时间戳 + prompt hash 确保文件名唯一
                timestamp = int(time.time())
                filename = f'cover_{timestamp}_{hashlib.md5((prompt + str(i)).encode()).hexdigest()[:8]}.jpg'
                file_path = upload_dir / filename
                img.save(file_path, 'JPEG', quality=95)
                
                mock_images.append({
                    'url': f'uploads/{filename}',
                    'prompt': prompt,
                    'provider': 'local',
                    'size': '900x500'
                })
                
                logger.info(f'封面图生成成功: {file_path}')
                
            except Exception as e:
                logger.error(f'生成封面图失败: {str(e)}')
                # 降级到占位符
                mock_images.append({
                    'url': f'https://via.placeholder.com/900x500?text=Cover+{i+1}',
                    'prompt': prompt,
                    'provider': 'mock',
                    'size': '900x500'
                })
        
        return mock_images

    async def close(self):
        """关闭客户端"""
        await self.http_client.aclose()

    async def download_image(self, url: str) -> Optional[str]:
        """
        下载图片

        Args:
            url: 图片URL

        Returns:
            本地文件路径
        """
        try:
            from pathlib import Path
            import hashlib
            import aiofiles

            response = await self.http_client.get(url)
            response.raise_for_status()

            # 生成文件名
            filename = hashlib.md5(url.encode()).hexdigest() + ".jpg"
            file_path = Path(settings.UPLOAD_DIR) / filename
            file_path.parent.mkdir(exist_ok=True)

            # 保存图片
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(response.content)

            logger.info(f"图片下载成功: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"下载图片失败: {str(e)}")
            return None

    async def crop_image(
        self,
        file_path: str,
        target_width: int = 900,
        target_height: int = 383
    ) -> str:
        """
        裁剪图片到指定尺寸

        Args:
            file_path: 原始图片路径
            target_width: 目标宽度
            target_height: 目标高度

        Returns:
            裁剪后的图片路径
        """
        try:
            from PIL import Image

            # 打开图片
            img = Image.open(file_path)

            # 转换为RGB（处理RGBA图片）
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # 计算裁剪区域（居中裁剪）
            original_width, original_height = img.size
            target_ratio = target_width / target_height
            original_ratio = original_width / original_height

            if original_ratio > target_ratio:
                # 原图更宽，裁剪左右
                new_height = original_height
                new_width = int(new_height * target_ratio)
                x_offset = (original_width - new_width) // 2
                y_offset = 0
            else:
                # 原图更高，裁剪上下
                new_width = original_width
                new_height = int(new_width / target_ratio)
                x_offset = 0
                y_offset = (original_height - new_height) // 2

            # 裁剪
            cropped = img.crop((x_offset, y_offset, x_offset + new_width, y_offset + new_height))

            # 调整大小
            resized = cropped.resize((target_width, target_height), Image.LANCZOS)

            # 保存
            output_path = file_path.replace('.jpg', '_cropped.jpg')
            resized.save(output_path, 'JPEG', quality=85)

            logger.info(f"图片裁剪成功: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"裁剪图片失败: {str(e)}")
            return file_path


# 全局实例
image_generation_service = ImageGenerationService()