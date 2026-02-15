"""
图片处理服务
支持图片压缩、格式转换、尺寸调整，适配多平台要求
"""
import os
import io
import hashlib
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..core.logger import logger
from ..core.config import settings
from ..core.platform_image_specs import (
    get_platform_spec, 
    validate_image_for_platform,
    ImageSpec,
    ImageType
)


class ImageProcessor:
    """图片处理器"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.quality_settings = {
            "high": 95,
            "medium": 85,
            "low": 75,
            "thumbnail": 70
        }
    
    async def process_image(
        self,
        image_path: str,
        output_path: Optional[str] = None,
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
        quality: str = "medium",
        format: Optional[str] = None,
        keep_aspect_ratio: bool = True,
        platform: Optional[str] = None,
        image_type: str = "inline"
    ) -> Dict[str, Any]:
        """
        处理图片，适配目标规格
        
        Args:
            image_path: 源图片路径
            output_path: 输出路径（可选）
            target_width: 目标宽度
            target_height: 目标高度
            quality: 图片质量 (high/medium/low/thumbnail)
            format: 输出格式（可选）
            keep_aspect_ratio: 是否保持宽高比
            platform: 目标平台（可选，自动获取规格）
            image_type: 图片类型 (cover/inline/thumbnail)
        
        Returns:
            处理结果字典
        """
        try:
            # 如果指定了平台，获取平台规格
            if platform and not (target_width and target_height):
                spec = get_platform_spec(platform, image_type)
                if spec:
                    target_width = target_width or spec.width
                    target_height = target_height or spec.height
                    format = format or (spec.formats[0] if spec.formats else None)
            
            # 设置默认输出路径
            if not output_path:
                file_name = Path(image_path).stem
                output_dir = Path(settings.UPLOAD_DIR)
                output_dir.mkdir(parents=True, exist_ok=True)
                ext = format.lower() if format else Path(image_path).suffix.lstrip('.').lower()
                output_path = str(output_dir / f"{file_name}_processed.{ext}")
            
            # 使用线程池执行图片处理
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._process_image_sync,
                image_path,
                output_path,
                target_width,
                target_height,
                quality,
                format,
                keep_aspect_ratio
            )
            
            return result
            
        except Exception as e:
            logger.error(f"处理图片失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "original_path": image_path
            }
    
    def _process_image_sync(
        self,
        image_path: str,
        output_path: str,
        target_width: Optional[int],
        target_height: Optional[int],
        quality: str,
        format: Optional[str],
        keep_aspect_ratio: bool
    ) -> Dict[str, Any]:
        """同步处理图片（在线程池中执行）"""
        
        # 打开图片
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            original_format = img.format
            original_mode = img.mode
            
            # 转换为RGB模式（处理RGBA或其他模式）
            if original_mode in ('RGBA', 'LA', 'P'):
                # 透明背景转换为白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if original_mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                else:
                    img = img.convert('RGB')
            
            # 调整尺寸
            if target_width or target_height:
                new_width, new_height = self._calculate_new_size(
                    original_width, original_height,
                    target_width, target_height,
                    keep_aspect_ratio
                )
                
                if new_width != original_width or new_height != original_height:
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                new_width, new_height = original_width, original_height
            
            # 确定输出格式
            output_format = format.upper() if format else (original_format or 'JPEG')
            if output_format not in ['JPEG', 'JPG', 'PNG', 'GIF', 'WEBP']:
                output_format = 'JPEG'
            
            # 设置保存参数
            save_kwargs = {}
            if output_format in ['JPEG', 'JPG']:
                save_kwargs['quality'] = self.quality_settings.get(quality, 85)
                save_kwargs['optimize'] = True
                save_kwargs['progressive'] = True
            elif output_format == 'PNG':
                save_kwargs['optimize'] = True
            elif output_format == 'WEBP':
                save_kwargs['quality'] = self.quality_settings.get(quality, 85)
                save_kwargs['method'] = 6  # 最佳压缩
            
            # 保存图片
            img.save(output_path, format=output_format, **save_kwargs)
            
            # 获取输出文件信息
            output_size = os.path.getsize(output_path)
            
            return {
                "success": True,
                "original_path": image_path,
                "output_path": output_path,
                "original_size": (original_width, original_height),
                "output_size": (new_width, new_height),
                "original_format": original_format,
                "output_format": output_format,
                "original_file_size": os.path.getsize(image_path),
                "output_file_size": output_size,
                "compression_ratio": f"{(1 - output_size / os.path.getsize(image_path)) * 100:.1f}%"
            }
    
    def _calculate_new_size(
        self,
        original_width: int,
        original_height: int,
        target_width: Optional[int],
        target_height: Optional[int],
        keep_aspect_ratio: bool
    ) -> Tuple[int, int]:
        """计算新的图片尺寸"""
        
        if not keep_aspect_ratio:
            return target_width or original_width, target_height or original_height
        
        # 保持宽高比
        aspect_ratio = original_width / original_height
        
        if target_width and target_height:
            # 同时指定了宽高，计算适应方式
            target_ratio = target_width / target_height
            
            if aspect_ratio > target_ratio:
                # 原图更宽，以宽度为基准
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            else:
                # 原图更高，以高度为基准
                new_height = target_height
                new_width = int(target_height * aspect_ratio)
        
        elif target_width:
            # 只指定宽度
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
        
        elif target_height:
            # 只指定高度
            new_height = target_height
            new_width = int(target_height * aspect_ratio)
        
        else:
            # 都没有指定，保持原尺寸
            new_width, new_height = original_width, original_height
        
        return new_width, new_height
    
    async def compress_image(
        self,
        image_path: str,
        max_size_mb: float = 5.0,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        压缩图片到指定大小以下
        
        Args:
            image_path: 源图片路径
            max_size_mb: 最大文件大小（MB）
            output_path: 输出路径（可选）
        
        Returns:
            处理结果
        """
        file_size = os.path.getsize(image_path) / (1024 * 1024)
        
        # 如果已经小于限制，直接返回
        if file_size <= max_size_mb:
            return {
                "success": True,
                "output_path": image_path,
                "message": "图片已符合大小要求，无需压缩",
                "original_size_mb": file_size,
                "output_size_mb": file_size
            }
        
        # 需要压缩，逐步降低质量
        qualities = ["high", "medium", "low", "thumbnail"]
        
        for quality in qualities:
            result = await self.process_image(
                image_path=image_path,
                output_path=output_path,
                quality=quality
            )
            
            if result.get("success"):
                output_size_mb = result["output_file_size"] / (1024 * 1024)
                if output_size_mb <= max_size_mb:
                    result["message"] = f"使用 {quality} 质量压缩成功"
                    return result
        
        # 如果质量降低还不够，尝试缩小尺寸
        with Image.open(image_path) as img:
            width, height = img.size
            scale = 0.8
            
            while scale > 0.3:  # 最小缩放到30%
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                result = await self.process_image(
                    image_path=image_path,
                    output_path=output_path,
                    target_width=new_width,
                    target_height=new_height,
                    quality="low"
                )
                
                if result.get("success"):
                    output_size_mb = result["output_file_size"] / (1024 * 1024)
                    if output_size_mb <= max_size_mb:
                        result["message"] = f"通过缩小尺寸到 {int(scale * 100)}% 压缩成功"
                        return result
                
                scale -= 0.1
        
        return {
            "success": False,
            "error": "无法将图片压缩到指定大小以下",
            "original_path": image_path
        }
    
    async def adapt_for_platform(
        self,
        image_path: str,
        platform: str,
        image_type: str = "cover",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        将图片适配到指定平台的要求
        
        Args:
            image_path: 源图片路径
            platform: 目标平台
            image_type: 图片类型
            output_path: 输出路径（可选）
        
        Returns:
            处理结果
        """
        # 先验证图片
        is_valid, message = validate_image_for_platform(platform, image_path, image_type)
        
        if is_valid:
            # 图片已经符合要求，可能只需要轻微调整
            spec = get_platform_spec(platform, image_type)
            if spec:
                return await self.process_image(
                    image_path=image_path,
                    output_path=output_path,
                    target_width=spec.width,
                    target_height=spec.height,
                    quality="high",
                    platform=platform,
                    image_type=image_type
                )
        
        # 图片不符合要求，需要处理
        spec = get_platform_spec(platform, image_type)
        if not spec:
            return {
                "success": False,
                "error": f"不支持的平台: {platform}"
            }
        
        # 先压缩到大小限制内
        compress_result = await self.compress_image(
            image_path=image_path,
            max_size_mb=spec.max_size_mb,
            output_path=output_path
        )
        
        if not compress_result.get("success"):
            return compress_result
        
        # 再调整尺寸
        processed_path = compress_result.get("output_path", image_path)
        
        final_result = await self.process_image(
            image_path=processed_path,
            output_path=output_path,
            target_width=spec.width,
            target_height=spec.height,
            quality="medium",
            format=spec.formats[0] if spec.formats else None,
            platform=platform,
            image_type=image_type
        )
        
        final_result["compression_info"] = compress_result
        return final_result
    
    async def generate_inline_images(
        self,
        content: str,
        article_title: str,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        为文章内容生成行内配图
        
        Args:
            content: 文章内容
            article_title: 文章标题
            count: 生成图片数量
        
        Returns:
            生成的图片信息列表
        """
        # 这里可以集成AI图片生成服务
        # 暂时返回空列表，需要与 image_provider_manager 集成
        logger.info(f"为文章 '{article_title}' 生成 {count} 张行内配图")
        return []
    
    async def create_thumbnail(
        self,
        image_path: str,
        output_path: Optional[str] = None,
        size: Tuple[int, int] = (300, 200)
    ) -> Dict[str, Any]:
        """
        创建缩略图
        
        Args:
            image_path: 源图片路径
            output_path: 输出路径（可选）
            size: 缩略图尺寸
        
        Returns:
            处理结果
        """
        return await self.process_image(
            image_path=image_path,
            output_path=output_path,
            target_width=size[0],
            target_height=size[1],
            quality="thumbnail",
            keep_aspect_ratio=True
        )
    
    async def batch_process(
        self,
        image_paths: List[str],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        批量处理图片
        
        Args:
            image_paths: 图片路径列表
            **kwargs: 处理参数
        
        Returns:
            处理结果列表
        """
        tasks = [self.process_image(path, **kwargs) for path in image_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "original_path": image_paths[i]
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """
        清理临时处理文件
        
        Args:
            max_age_hours: 文件最大保留时间（小时）
        """
        import time
        
        upload_dir = Path(settings.UPLOAD_DIR)
        if not upload_dir.exists():
            return
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        cleaned_count = 0
        for file_path in upload_dir.glob("*_processed.*"):
            try:
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"清理临时文件失败 {file_path}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"清理了 {cleaned_count} 个临时处理文件")


# 全局实例
image_processor = ImageProcessor()
