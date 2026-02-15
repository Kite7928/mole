"""
文章配图服务
支持批量生成封面图和段落配图
"""
import asyncio
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime

from ..models.article import Article
from ..core.logger import logger
from .image_provider_manager import image_provider_manager
from .prompt_templates import (
    PromptTemplate,
    ImageStyle,
    analyze_and_build_prompts,
    get_cover_prompt
)


class ArticleImageService:
    """文章配图服务"""
    
    def __init__(self):
        self.max_concurrent = 3  # 最大并发数
    
    async def generate_article_images(
        self,
        db: AsyncSession,
        article_id: int,
        style: str = "professional",
        max_images: int = 5,
        language: str = "zh",
        auto_insert: bool = True
    ) -> Dict[str, Any]:
        """
        为文章批量生成配图
        
        Args:
            db: 数据库会话
            article_id: 文章ID
            style: 图片风格
            max_images: 最多生成图片数
            language: 语言
            auto_insert: 是否自动插入到文章内容中
            
        Returns:
            生成结果
        """
        # 获取文章
        result = await db.execute(
            select(Article).where(Article.id == article_id)
        )
        article = result.scalar_one_or_none()
        
        if not article:
            return {"success": False, "error": "文章不存在"}
        
        try:
            # 1. 分析文章并构建所有 prompts
            prompts = analyze_and_build_prompts(
                title=article.title,
                content=article.content or "",
                summary=article.summary,
                style=style,
                max_images=max_images,
                language=language
            )
            
            logger.info(f"文章《{article.title}》计划生成 {len(prompts)} 张配图")
            
            # 2. 批量生成图片（控制并发）
            generated_images = []
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def generate_with_limit(prompt_data: Dict) -> Dict:
                async with semaphore:
                    return await self._generate_single_image(
                        db, article_id, prompt_data, language
                    )
            
            # 并发生成所有图片
            tasks = [generate_with_limit(p) for p in prompts]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 3. 处理结果
            success_count = 0
            failed_count = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"图片生成失败: {result}")
                    failed_count += 1
                    generated_images.append({
                        "position": prompts[i].get("suggested_position"),
                        "success": False,
                        "error": str(result)
                    })
                elif result.get("success"):
                    success_count += 1
                    generated_images.append(result)
                else:
                    failed_count += 1
                    generated_images.append(result)
            
            # 4. 如果需要，自动插入到文章内容
            if auto_insert and success_count > 0:
                await self._insert_images_into_content(db, article, generated_images)
            
            return {
                "success": True,
                "article_id": article_id,
                "total": len(prompts),
                "success_count": success_count,
                "failed_count": failed_count,
                "images": generated_images
            }
            
        except Exception as e:
            logger.error(f"批量生成配图失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_single_image(
        self,
        db: AsyncSession,
        article_id: int,
        prompt_data: Dict[str, Any],
        language: str = "zh"
    ) -> Dict[str, Any]:
        """
        生成单张图片
        
        Args:
            db: 数据库会话
            article_id: 文章ID
            prompt_data: Prompt 数据
            language: 语言
            
        Returns:
            生成结果
        """
        try:
            position = prompt_data.get("suggested_position", "unknown")
            prompt = prompt_data.get("prompt", "")
            style = prompt_data.get("style", "professional")
            tongyi_style = prompt_data.get("tongyi_style", "<auto>")
            
            logger.info(f"生成 {position} 图片: {prompt[:50]}...")
            
            # 使用 image_provider_manager 生成图片
            image_path = await image_provider_manager.generate_cover(
                db=db,
                title=prompt,  # 使用完整 prompt 作为标题
                style=style,
                width=900,
                height=500
            )
            
            if not image_path:
                return {
                    "position": position,
                    "success": False,
                    "error": "图片生成失败"
                }
            
            # 转换为 URL 路径
            image_url = image_path.replace("\\", "/").split("/")[-1]
            image_url = f"uploads/{image_url}"
            
            return {
                "position": position,
                "success": True,
                "url": image_url,
                "prompt": prompt,
                "style": style,
                "type": "cover" if position == "cover" else "paragraph"
            }
            
        except Exception as e:
            logger.error(f"生成图片失败: {e}")
            return {
                "position": prompt_data.get("suggested_position", "unknown"),
                "success": False,
                "error": str(e)
            }
    
    async def _insert_images_into_content(
        self,
        db: AsyncSession,
        article: Article,
        images: List[Dict[str, Any]]
    ):
        """
        将生成的图片插入到文章内容中
        
        Args:
            db: 数据库会话
            article: 文章对象
            images: 生成的图片列表
        """
        content = article.content or ""
        
        # 按位置排序图片
        cover_image = None
        paragraph_images = []
        
        for img in images:
            if not img.get("success"):
                continue
            if img["position"] == "cover":
                cover_image = img
            else:
                paragraph_images.append(img)
        
        # 更新封面图
        if cover_image:
            article.cover_image_url = cover_image["url"]
        
        # 插入段落配图
        if paragraph_images and content:
            new_content = self._insert_paragraph_images(content, paragraph_images)
            article.content = new_content
        
        await db.commit()
        logger.info(f"已自动插入 {len(images)} 张图片到文章")
    
    def _insert_paragraph_images(
        self,
        content: str,
        images: List[Dict[str, Any]]
    ) -> str:
        """
        在文章内容中插入段落配图
        
        策略：
        1. 在每个 H2 标题后插入一张图片
        2. 如果段落内容较长（>300字），在段落中间也插入图片
        
        Args:
            content: 原始内容（Markdown）
            images: 段落图片列表
            
        Returns:
            插入图片后的内容
        """
        import re
        
        lines = content.split("\n")
        new_lines = []
        image_index = 0
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # 检测 H2 标题（## 开头）
            if line.startswith("## ") and image_index < len(images):
                # 在标题后插入图片
                img = images[image_index]
                img_markdown = f"\n![段落配图]({img['url']})\n"
                new_lines.append(img_markdown)
                image_index += 1
        
        return "\n".join(new_lines)
    
    async def regenerate_single_image(
        self,
        db: AsyncSession,
        article_id: int,
        position: str,
        style: str = "professional",
        language: str = "zh"
    ) -> Dict[str, Any]:
        """
        重新生成单张图片
        
        Args:
            db: 数据库会话
            article_id: 文章ID
            position: 图片位置（cover/paragraph_N）
            style: 风格
            language: 语言
            
        Returns:
            生成结果
        """
        # 获取文章
        result = await db.execute(
            select(Article).where(Article.id == article_id)
        )
        article = result.scalar_one_or_none()
        
        if not article:
            return {"success": False, "error": "文章不存在"}
        
        try:
            # 分析文章结构
            prompts = analyze_and_build_prompts(
                title=article.title,
                content=article.content or "",
                summary=article.summary,
                style=style,
                language=language
            )
            
            # 找到对应位置的 prompt
            target_prompt = None
            for p in prompts:
                if p.get("suggested_position") == position:
                    target_prompt = p
                    break
            
            if not target_prompt:
                return {"success": False, "error": f"未找到位置 {position} 的配图配置"}
            
            # 重新生成
            result = await self._generate_single_image(
                db, article_id, target_prompt, language
            )
            
            # 更新文章内容
            if result.get("success") and position != "cover":
                # 替换原有图片
                old_url_pattern = f'!\[.*?\]\(.*?{position}.*?\)'
                new_markdown = f'![段落配图]({result["url"]})'
                article.content = re.sub(old_url_pattern, new_markdown, article.content or "")
                await db.commit()
            elif result.get("success") and position == "cover":
                article.cover_image_url = result["url"]
                await db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"重新生成图片失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_article_structure(
        self,
        article_id: int,
        content: str,
        title: str
    ) -> Dict[str, Any]:
        """
        分析文章结构，建议配图位置
        
        Args:
            article_id: 文章ID
            content: 文章内容
            title: 文章标题
            
        Returns:
            分析结果
        """
        try:
            # 使用 PromptTemplate 分析
            suggestions = PromptTemplate.analyze_article_for_images(content)
            
            # 构建 prompts 预览
            prompts_preview = analyze_and_build_prompts(
                title=title,
                content=content,
                style="professional"
            )
            
            return {
                "success": True,
                "article_id": article_id,
                "total_suggestions": len(suggestions),
                "suggestions": suggestions,
                "prompts_preview": [
                    {
                        "position": p.get("suggested_position"),
                        "prompt": p.get("prompt", "")[:100] + "...",
                        "style": p.get("style")
                    }
                    for p in prompts_preview
                ]
            }
            
        except Exception as e:
            logger.error(f"分析文章结构失败: {e}")
            return {"success": False, "error": str(e)}


# 全局实例
article_image_service = ArticleImageService()
