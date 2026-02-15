"""
图片生成服务提供商实现
支持多种AI图片生成平台
"""
from typing import Dict, List, Optional, Any
import httpx
import json
import urllib.parse
from abc import ABC, abstractmethod
from pathlib import Path
import uuid

from ..core.logger import logger
from ..core.config import settings


class BaseImageProvider(ABC):
    """图片生成提供商基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.http_client = httpx.AsyncClient(
            timeout=120.0,
            follow_redirects=True,
            trust_env=False,
        )
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        width: int = 900,
        height: int = 500,
        **kwargs
    ) -> Optional[str]:
        """生成图片，返回本地文件路径"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        pass
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.http_client.aclose()
    
    def _generate_temp_path(self, suffix: str = ".jpg") -> str:
        """生成临时文件路径"""
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        return str(upload_dir / f"cover_{uuid.uuid4().hex[:16]}{suffix}")


class TongyiWanxiangProvider(BaseImageProvider):
    """通义万相（阿里）图片生成"""
    
    def validate_config(self) -> bool:
        """验证配置"""
        return bool(
            self.config.get("api_key") and
            self.config.get("base_url", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis")
        )
    
    async def generate(
        self,
        prompt: str,
        width: int = 900,
        height: int = 500,
        **kwargs
    ) -> Optional[str]:
        """使用通义万相生成图片"""
        try:
            api_key = self.config.get("api_key")
            base_url = self.config.get("base_url", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable"
            }
            
            # 计算合适的尺寸（通义万相支持的尺寸）
            size = self._get_best_size(width, height)
            
            # 将通用 style 映射到通义万相支持的值
            style_map = {
                "professional": "<photography>",
                "creative": "<anime>",
                "minimal": "<flat illustration>",
                "vibrant": "<3d cartoon>",
                "tech": "<3d cartoon>",
                "business": "<photography>",
                "nature": "<watercolor>",
                "abstract": "<sketch>"
            }
            raw_style = kwargs.get("style", "<auto>")
            mapped_style = style_map.get(raw_style, raw_style if raw_style.startswith("<") else "<auto>")
            
            # 将英文提示词转换为中文提示词（提取文章标题）
            cn_prompt = self._convert_to_chinese_prompt(prompt)
            logger.info(f"通义万相使用中文提示词: {cn_prompt[:80]}...")
            
            payload = {
                "model": self.config.get("model", "wanx-v1"),
                "input": {
                    "prompt": cn_prompt
                },
                "parameters": {
                    "size": size,
                    "n": 1,
                    "style": mapped_style,
                    "prompt_extend": kwargs.get("prompt_extend", True)
                }
            }
            
            # 提交任务
            response = await self.http_client.post(base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            task_id = data.get("output", {}).get("task_id")
            if not task_id:
                logger.error("通义万相未返回task_id")
                return None
            
            # 轮询获取结果
            image_url = await self._poll_result(task_id, api_key)
            if not image_url:
                return None
            
            # 下载图片
            return await self._download_image(image_url)
            
        except Exception as e:
            logger.error(f"通义万相生成失败: {e!r}")
            return None
    
    def _convert_to_chinese_prompt(self, prompt: str) -> str:
        """将英文提示词转换为中文提示词，提取文章标题"""
        import re
        
        # 尝试提取单引号中的文章标题
        match = re.search(r"about ['\"]([^'\"]+)['\"]", prompt)
        if match:
            title = match.group(1)
            # 构建中文提示词
            return f"为文章《{title}》创作一张精美的封面插图，高质量，适合微信公众号"
        
        # 如果无法提取，尝试移除常见的英文修饰词
        stop_words = [
            "create a", "professional", "wechat article", "cover image",
            "about", "style", "high quality", "suitable for",
            "blog or news", "clear composition", "the image should be"
        ]
        cn_prompt = prompt
        for word in stop_words:
            cn_prompt = re.sub(re.escape(word), "", cn_prompt, flags=re.IGNORECASE)
        
        # 清理多余的空格和标点
        cn_prompt = re.sub(r'\s+', ' ', cn_prompt).strip(".,'")
        
        if cn_prompt:
            return f"为文章《{cn_prompt}》创作一张精美的封面插图"
        
        # 最后的降级方案
        return "创作一张精美的微信公众号封面图，高质量，专业"
    
    def _get_best_size(self, width: int, height: int) -> str:
        """获取最接近的支持尺寸"""
        # 通义万相支持的尺寸
        supported_sizes = ["1024*1024", "1280*720", "720*1280", "1280*768", "768*1280"]
        
        # 计算宽高比
        ratio = width / height
        
        # 根据比例选择最合适的尺寸
        if 0.9 <= ratio <= 1.1:
            return "1024*1024"
        elif ratio > 1:
            return "1280*720" if ratio > 1.5 else "1280*768"
        else:
            return "720*1280" if ratio < 0.67 else "768*1280"
    
    async def _poll_result(self, task_id: str, api_key: str, max_attempts: int = 30) -> Optional[str]:
        """轮询获取任务结果"""
        import asyncio
        
        url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        for _ in range(max_attempts):
            try:
                response = await self.http_client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                status = data.get("output", {}).get("task_status")
                
                if status == "SUCCEEDED":
                    results = data.get("output", {}).get("results", [])
                    if results:
                        return results[0].get("url")
                    return None
                elif status in ["FAILED", "ERROR"]:
                    logger.error(f"通义万相任务失败: {data}")
                    return None
                
                # 等待2秒再查询
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"查询任务状态失败: {e!r}")
                await asyncio.sleep(2)
        
        logger.error("通义万相任务超时")
        return None
    
    async def _download_image(self, url: str) -> Optional[str]:
        """下载图片到本地"""
        try:
            response = await self.http_client.get(url)
            response.raise_for_status()
            
            temp_path = self._generate_temp_path()
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            return temp_path
            
        except Exception as e:
            logger.error(f"下载图片失败: {e!r}")
            return None


class PexelsProvider(BaseImageProvider):
    """Pexels免费图库"""
    
    def validate_config(self) -> bool:
        """验证配置"""
        return bool(self.config.get("api_key"))
    
    async def generate(
        self,
        prompt: str,
        width: int = 900,
        height: int = 500,
        **kwargs
    ) -> Optional[str]:
        """搜索Pexels图片"""
        try:
            api_key = self.config.get("api_key")
            base_url = "https://api.pexels.com/v1/search"
            
            headers = {
                "Authorization": api_key
            }
            
            # 提取关键词（简化提示词）
            keywords = self._extract_keywords(prompt)
            
            params = {
                "query": keywords,
                "per_page": 5,
                "orientation": self._get_orientation(width, height)
            }
            
            response = await self.http_client.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            photos = data.get("photos", [])
            if not photos:
                logger.warning(f"Pexels未找到相关图片: {keywords}")
                return None
            
            # 选择最合适的尺寸
            photo = photos[0]
            image_url = self._select_best_size(photo["src"], width, height)
            
            # 下载图片
            return await self._download_image(image_url)
            
        except Exception as e:
            logger.error(f"Pexels搜索失败: {e}")
            return None
    
    def _extract_keywords(self, prompt: str) -> str:
        """从提示词中提取关键词"""
        # 移除常见修饰词，保留核心名词
        stop_words = ["美丽的", "精美的", "高质量的", "专业的", "创建", "生成", "一张", "图片", "封面"]
        keywords = prompt
        for word in stop_words:
            keywords = keywords.replace(word, "")
        return keywords.strip()[:50] or "technology"
    
    def _get_orientation(self, width: int, height: int) -> str:
        """获取方向参数"""
        ratio = width / height
        if ratio > 1.2:
            return "landscape"
        elif ratio < 0.8:
            return "portrait"
        return "square"
    
    def _select_best_size(self, src: Dict, target_width: int, target_height: int) -> str:
        """选择最接近目标尺寸的图片"""
        # Pexels提供的尺寸
        sizes = ["original", "large2x", "large", "medium", "small", "portrait", "landscape", "tiny"]
        
        # 根据目标尺寸选择
        if target_width >= 1920:
            return src.get("large2x") or src.get("large") or src.get("original")
        elif target_width >= 1280:
            return src.get("large") or src.get("medium") or src.get("original")
        else:
            return src.get("medium") or src.get("small") or src.get("large")
    
    async def _download_image(self, url: str) -> Optional[str]:
        """下载图片"""
        try:
            response = await self.http_client.get(url)
            response.raise_for_status()
            
            temp_path = self._generate_temp_path()
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            return temp_path
            
        except Exception as e:
            logger.error(f"下载图片失败: {e}")
            return None


class LeonardoProvider(BaseImageProvider):
    """Leonardo.ai图片生成"""
    
    def validate_config(self) -> bool:
        """验证配置"""
        return bool(
            self.config.get("api_key") and
            self.config.get("base_url", "https://cloud.leonardo.ai/api/rest/v1")
        )
    
    async def generate(
        self,
        prompt: str,
        width: int = 900,
        height: int = 500,
        **kwargs
    ) -> Optional[str]:
        """使用Leonardo生成图片"""
        try:
            api_key = self.config.get("api_key")
            base_url = self.config.get("base_url", "https://cloud.leonardo.ai/api/rest/v1")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # 生成图片
            payload = {
                "prompt": prompt,
                "width": width,
                "height": height,
                "modelId": self.config.get("model_id", "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3"),  # Leonardo Diffusion XL
                "num_images": 1,
                "guidance_scale": kwargs.get("guidance_scale", 7),
                "alchemy": kwargs.get("alchemy", True),
                "photoReal": kwargs.get("photoReal", False)
            }
            
            url = f"{base_url}/generations"
            response = await self.http_client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            generation_id = data.get("sdGenerationJob", {}).get("generationId")
            if not generation_id:
                logger.error("Leonardo未返回generationId")
                return None
            
            # 等待生成完成
            return await self._wait_for_generation(generation_id, api_key, base_url)
            
        except Exception as e:
            logger.error(f"Leonardo生成失败: {e}")
            return None
    
    async def _wait_for_generation(self, generation_id: str, api_key: str, base_url: str, max_attempts: int = 30) -> Optional[str]:
        """等待生成完成"""
        import asyncio
        
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"{base_url}/generations/{generation_id}"
        
        for _ in range(max_attempts):
            try:
                response = await self.http_client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                generations = data.get("generations_by_pk", {})
                status = generations.get("status")
                
                if status == "COMPLETE":
                    images = generations.get("generated_images", [])
                    if images:
                        return await self._download_image(images[0]["url"])
                    return None
                elif status == "FAILED":
                    logger.error(f"Leonardo生成失败: {generations}")
                    return None
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"查询生成状态失败: {e}")
                await asyncio.sleep(2)
        
        logger.error("Leonardo生成超时")
        return None
    
    async def _download_image(self, url: str) -> Optional[str]:
        """下载图片"""
        try:
            response = await self.http_client.get(url)
            response.raise_for_status()
            
            temp_path = self._generate_temp_path()
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            return temp_path
            
        except Exception as e:
            logger.error(f"下载图片失败: {e}")
            return None


class PollinationsProvider(BaseImageProvider):
    """Pollinations.ai免费图片生成（无需API Key）"""
    
    def validate_config(self) -> bool:
        """Pollinations不需要配置"""
        return True
    
    async def generate(
        self,
        prompt: str,
        width: int = 900,
        height: int = 500,
        **kwargs
    ) -> Optional[str]:
        """使用Pollinations生成图片"""
        try:
            # URL编码提示词
            encoded_prompt = urllib.parse.quote(prompt)
            
            # 构建URL
            seed = kwargs.get("seed", uuid.uuid4().int % 10000)
            model = kwargs.get("model", "flux")  # flux, turbo, sdxl
            
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true&model={model}"
            
            logger.info(f"Pollinations生成URL: {url[:100]}...")
            
            # 下载图片
            response = await self.http_client.get(url, timeout=60.0)
            response.raise_for_status()
            
            temp_path = self._generate_temp_path()
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"Pollinations图片已保存: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Pollinations生成失败: {e!r}")
            logger.error(f"Pollinations请求URL: {url[:150]}...")
            return None


class StableDiffusionProvider(BaseImageProvider):
    """Stable Diffusion本地或远程部署"""
    
    def validate_config(self) -> bool:
        """验证配置"""
        return bool(self.config.get("base_url"))
    
    async def generate(
        self,
        prompt: str,
        width: int = 900,
        height: int = 500,
        **kwargs
    ) -> Optional[str]:
        """使用Stable Diffusion生成图片"""
        try:
            base_url = self.config.get("base_url")  # 例如: http://localhost:7860
            
            payload = {
                "prompt": prompt,
                "negative_prompt": kwargs.get("negative_prompt", "blur, low quality, distorted"),
                "width": width,
                "height": height,
                "steps": kwargs.get("steps", 30),
                "cfg_scale": kwargs.get("cfg_scale", 7.0),
                "sampler_index": kwargs.get("sampler", "DPM++ 2M Karras"),
                "batch_size": 1,
                "n_iter": 1
            }
            
            url = f"{base_url}/sdapi/v1/txt2img"
            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            images = data.get("images", [])
            if not images:
                logger.error("Stable Diffusion未返回图片")
                return None
            
            # 保存base64图片
            import base64
            temp_path = self._generate_temp_path()
            with open(temp_path, "wb") as f:
                f.write(base64.b64decode(images[0]))
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Stable Diffusion生成失败: {e}")
            return None


# 提供商工厂
PROVIDER_MAP = {
    "tongyi_wanxiang": TongyiWanxiangProvider,
    "pexels": PexelsProvider,
    "leonardo": LeonardoProvider,
    "pollinations": PollinationsProvider,
    "stable_diffusion": StableDiffusionProvider,
}


def create_provider(provider_type: str, config: Dict[str, Any]) -> Optional[BaseImageProvider]:
    """创建提供商实例"""
    provider_class = PROVIDER_MAP.get(provider_type)
    if not provider_class:
        logger.error(f"未知的图片提供商类型: {provider_type}")
        return None
    
    return provider_class(config)


def get_available_providers() -> List[Dict[str, Any]]:
    """获取所有可用的提供商列表"""
    return [
        {
            "type": "pollinations",
            "name": "Pollinations.ai",
            "description": "完全免费的AI图片生成，无需API Key",
            "requires_config": False,
            "recommended": True
        },
        {
            "type": "pexels",
            "name": "Pexels",
            "description": "免费高质量图库，每小时200次请求",
            "requires_config": True,
            "config_fields": ["api_key"],
            "recommended": True
        },
        {
            "type": "tongyi_wanxiang",
            "name": "通义万相（阿里）",
            "description": "阿里云AI绘画，支持中文，有免费额度",
            "requires_config": True,
            "config_fields": ["api_key"],
            "recommended": True
        },
        {
            "type": "leonardo",
            "name": "Leonardo.ai",
            "description": "每日150 tokens免费额度",
            "requires_config": True,
            "config_fields": ["api_key"],
            "recommended": False
        },
        {
            "type": "stable_diffusion",
            "name": "Stable Diffusion",
            "description": "本地或远程部署的开源模型",
            "requires_config": True,
            "config_fields": ["base_url"],
            "recommended": False
        }
    ]
