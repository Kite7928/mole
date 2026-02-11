"""
模板管理服务
支持10+分类模板管理，包括科技、财经、教育、健康、美食等
支持模板CRUD操作、分类管理、预览、版本控制
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from ..core.logger import logger
from ..models.template import Template


class TemplateService:
    """模板管理服务"""

    # 默认模板分类
    CATEGORIES = {
        "tech": "科技数码",
        "finance": "财经投资",
        "education": "教育学习",
        "health": "健康养生",
        "food": "美食旅行",
        "fashion": "时尚生活",
        "career": "职场发展",
        "emotion": "情感心理",
        "entertainment": "娱乐八卦",
        "news": "新闻时事",
    }

    def __init__(self):
        pass

    async def create_template(
        self,
        db: AsyncSession,
        name: str,
        category: str,
        html_content: str,
        description: Optional[str] = None,
        css_content: Optional[str] = None,
        is_default: bool = False,
        **kwargs
    ) -> Template:
        """
        创建模板

        Args:
            db: 数据库会话
            name: 模板名称
            category: 模板分类
            html_content: HTML内容
            description: 模板描述
            css_content: CSS样式
            is_default: 是否为默认模板
            **kwargs: 其他字段

        Returns:
            创建的模板
        """
        try:
            logger.info(f"创建模板: {name}")

            template = Template(
                name=name,
                category=category,
                description=description,
                html_content=html_content,
                css_content=css_content,
                is_default=is_default,
                **kwargs
            )

            db.add(template)
            await db.commit()
            await db.refresh(template)

            logger.info(f"模板创建成功，ID: {template.id}")
            return template

        except Exception as e:
            logger.error(f"创建模板失败: {str(e)}")
            await db.rollback()
            raise

    async def get_template(
        self,
        db: AsyncSession,
        template_id: int
    ) -> Optional[Template]:
        """
        获取模板详情

        Args:
            db: 数据库会话
            template_id: 模板ID

        Returns:
            模板详情
        """
        try:
            query = select(Template).where(Template.id == template_id)
            result = await db.execute(query)
            template = result.scalar_one_or_none()

            if template:
                # 更新使用次数
                await db.execute(
                    update(Template)
                    .where(Template.id == template_id)
                    .values(usage_count=Template.usage_count + 1)
                )
                await db.commit()

            return template

        except Exception as e:
            logger.error(f"获取模板失败: {str(e)}")
            raise

    async def list_templates(
        self,
        db: AsyncSession,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Template]:
        """
        获取模板列表

        Args:
            db: 数据库会话
            category: 分类筛选
            is_active: 是否启用筛选
            skip: 跳过数量
            limit: 返回数量

        Returns:
            模板列表
        """
        try:
            query = select(Template).order_by(Template.sort_order.asc(), Template.created_at.desc())

            if category:
                query = query.where(Template.category == category)

            if is_active is not None:
                query = query.where(Template.is_active == is_active)

            query = query.offset(skip).limit(limit)

            result = await db.execute(query)
            templates = result.scalars().all()

            return templates

        except Exception as e:
            logger.error(f"获取模板列表失败: {str(e)}")
            raise

    async def update_template(
        self,
        db: AsyncSession,
        template_id: int,
        **kwargs
    ) -> Optional[Template]:
        """
        更新模板

        Args:
            db: 数据库会话
            template_id: 模板ID
            **kwargs: 更新字段

        Returns:
            更新后的模板
        """
        try:
            logger.info(f"更新模板，ID: {template_id}")

            query = update(Template).where(Template.id == template_id).values(**kwargs)
            await db.execute(query)
            await db.commit()

            # 返回更新后的模板
            return await self.get_template(db, template_id)

        except Exception as e:
            logger.error(f"更新模板失败: {str(e)}")
            await db.rollback()
            raise

    async def delete_template(
        self,
        db: AsyncSession,
        template_id: int
    ) -> bool:
        """
        删除模板

        Args:
            db: 数据库会话
            template_id: 模板ID

        Returns:
            是否成功
        """
        try:
            logger.info(f"删除模板，ID: {template_id}")

            query = delete(Template).where(Template.id == template_id)
            await db.execute(query)
            await db.commit()

            logger.info(f"模板删除成功，ID: {template_id}")
            return True

        except Exception as e:
            logger.error(f"删除模板失败: {str(e)}")
            await db.rollback()
            raise

    async def get_template_by_category(
        self,
        db: AsyncSession,
        category: str,
        count: int = 1
    ) -> List[Template]:
        """
        根据分类获取模板

        Args:
            db: 数据库会话
            category: 分类
            count: 获取数量

        Returns:
            模板列表
        """
        try:
            query = (
                select(Template)
                .where(Template.category == category, Template.is_active == True)
                .order_by(Template.is_default.desc(), Template.usage_count.desc())
                .limit(count)
            )

            result = await db.execute(query)
            templates = result.scalars().all()

            return templates

        except Exception as e:
            logger.error(f"根据分类获取模板失败: {str(e)}")
            raise

    async def get_default_template(
        self,
        db: AsyncSession,
        category: Optional[str] = None
    ) -> Optional[Template]:
        """
        获取默认模板

        Args:
            db: 数据库会话
            category: 分类（可选）

        Returns:
            默认模板
        """
        try:
            query = select(Template).where(Template.is_default == True, Template.is_active == True)

            if category:
                query = query.where(Template.category == category)

            query = query.order_by(Template.usage_count.desc()).limit(1)

            result = await db.execute(query)
            template = result.scalar_one_or_none()

            return template

        except Exception as e:
            logger.error(f"获取默认模板失败: {str(e)}")
            raise

    async def like_template(
        self,
        db: AsyncSession,
        template_id: int
    ) -> bool:
        """
        点赞模板

        Args:
            db: 数据库会话
            template_id: 模板ID

        Returns:
            是否成功
        """
        try:
            await db.execute(
                update(Template)
                .where(Template.id == template_id)
                .values(like_count=Template.like_count + 1)
            )
            await db.commit()

            return True

        except Exception as e:
            logger.error(f"点赞模板失败: {str(e)}")
            await db.rollback()
            raise

    async def get_categories(self) -> Dict[str, str]:
        """
        获取所有分类

        Returns:
            分类字典
        """
        return self.CATEGORIES.copy()

    async def preview_template(
        self,
        template: Template,
        content: str
    ) -> str:
        """
        预览模板

        Args:
            template: 模板对象
            content: 文章内容

        Returns:
            预览HTML
        """
        try:
            # 简单的模板替换
            html = template.html_content.replace("{{content}}", content)

            if template.css_content:
                html = f'<style>{template.css_content}</style>\n{html}'

            return html

        except Exception as e:
            logger.error(f"预览模板失败: {str(e)}")
            raise


# 全局实例
template_service = TemplateService()
