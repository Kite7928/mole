"""
图片生成服务提供商配置管理
"""
import json
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ..models.image_provider_config import ImageProviderConfig
from .image_providers import (
    create_provider,
    get_available_providers,
    BaseImageProvider
)
from ..core.logger import logger


class ImageProviderManager:
    """图片生成提供商管理器"""
    
    def __init__(self):
        self._provider_cache: Dict[str, BaseImageProvider] = {}
        # 项目优先级：通义默认，P（Pollinations）次级，其他继续兜底
        self._provider_priority_order = {
            "tongyi_wanxiang": 0,
            "pollinations": 1,
            "pexels": 2,
            "leonardo": 3,
            "stable_diffusion": 4,
        }
    
    async def _update_tongyi_api_key_if_needed(self, db: AsyncSession, configs: List[Dict[str, Any]]):
        """如果通义万相的 API Key 为空，尝试从环境变量更新"""
        try:
            from ..core.config import settings
            
            # 查找通义万相配置
            tongyi_config = None
            for config in configs:
                if config.get("provider_type") == "tongyi_wanxiang":
                    tongyi_config = config
                    break
            
            if not tongyi_config:
                return
            
            # 检查当前 API Key 是否为空
            api_config = tongyi_config.get("api_config", {})
            current_key = api_config.get("api_key", "")
            
            if current_key:
                logger.info("通义万相已配置 API Key，无需更新")
                return
            
            # 从环境变量获取 API Key
            env_key = getattr(settings, 'TONGYI_WANXIANG_API_KEY', None) or getattr(settings, 'COGVIEW_API_KEY', None)
            
            if not env_key:
                logger.warning("环境变量中没有找到通义万相的 API Key")
                return
            
            # 更新数据库中的配置
            api_config["api_key"] = env_key
            
            result = await db.execute(
                update(ImageProviderConfig)
                .where(ImageProviderConfig.id == tongyi_config["id"])
                .values(api_config=json.dumps(api_config), is_enabled=True)
            )
            await db.commit()
            
            logger.info(f"已从环境变量更新通义万相的 API Key")
            
            # 清除缓存
            cache_key = f"tongyi_wanxiang_{tongyi_config['id']}"
            if cache_key in self._provider_cache:
                del self._provider_cache[cache_key]
                
        except Exception as e:
            logger.warning(f"更新通义万相 API Key 失败: {e}")
    
    async def initialize_default_configs(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        初始化默认图片提供商配置
        如果没有配置，自动创建推荐的默认配置
        """
        # 检查是否已有配置
        existing_configs = await self.get_all_configs(db)
        if existing_configs:
            logger.info(f"已有 {len(existing_configs)} 个图片提供商配置")
            # 检查通义万相是否需要更新 API Key
            await self._update_tongyi_api_key_if_needed(db, existing_configs)
            return []
        
        created_configs = []
        from ..core.config import settings
        tongyi_api_key = settings.COGVIEW_API_KEY or settings.TONGYI_WANXIANG_API_KEY or ""
        has_tongyi_key = bool(tongyi_api_key)

        # 1. 通义万相（主图源）
        try:
            config1 = await self.create_config(
                db=db,
                provider_type="tongyi_wanxiang",
                name="通义万相（阿里）",
                api_config={
                    "api_key": tongyi_api_key,
                    "base_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
                    "model": "wanx-v1"
                },
                default_params={"width": 900, "height": 500, "style": "<auto>"},
                is_default=has_tongyi_key,
                is_enabled=has_tongyi_key,
                priority=0
            )
            created_configs.append({
                "id": config1.id,
                "name": config1.name,
                "type": "tongyi_wanxiang",
                "note": "已设为主图源" if has_tongyi_key else "已创建，待配置 API Key 后启用"
            })
            logger.info(f"创建默认配置: {config1.name}")
        except Exception as e:
            logger.warning(f"创建通义万相配置失败: {e}")

        # 2. Pollinations（P 次级回退）
        try:
            config2 = await self.create_config(
                db=db,
                provider_type="pollinations",
                name="Pollinations.ai（免费回退）",
                api_config={},
                default_params={"width": 900, "height": 500, "model": "flux"},
                is_default=not has_tongyi_key,
                is_enabled=True,
                priority=1
            )
            created_configs.append({
                "id": config2.id,
                "name": config2.name,
                "type": "pollinations",
                "note": "作为通义失败时的自动回退"
            })
            logger.info(f"创建默认配置: {config2.name}")
        except Exception as e:
            logger.warning(f"创建Pollinations配置失败: {e}")

        # 3. Pexels（补充图库）
        try:
            config3 = await self.create_config(
                db=db,
                provider_type="pexels",
                name="Pexels免费图库",
                api_config={"api_key": ""},
                default_params={"width": 900, "height": 500},
                is_default=False,
                is_enabled=True,
                priority=2
            )
            created_configs.append({
                "id": config3.id,
                "name": config3.name,
                "type": "pexels",
                "note": "需要配置 API Key 后可用"
            })
            logger.info(f"创建默认配置: {config3.name}")
        except Exception as e:
            logger.warning(f"创建Pexels配置失败: {e}")
        
        if created_configs:
            logger.info(f"成功初始化 {len(created_configs)} 个默认图片提供商配置")
        
        return created_configs
    
    async def get_all_configs(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """获取所有配置"""
        result = await db.execute(
            select(ImageProviderConfig).order_by(ImageProviderConfig.priority)
        )
        configs = result.scalars().all()
        
        return [
            {
                "id": c.id,
                "provider_type": c.provider_type,
                "name": c.name,
                "is_enabled": c.is_enabled,
                "is_default": c.is_default,
                "api_config": json.loads(c.api_config) if c.api_config else {},
                "default_params": json.loads(c.default_params) if c.default_params else {},
                "priority": c.priority,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None
            }
            for c in configs
        ]
    
    async def get_config(self, db: AsyncSession, config_id: int) -> Optional[Dict[str, Any]]:
        """获取单个配置"""
        result = await db.execute(
            select(ImageProviderConfig).where(ImageProviderConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            return None
        
        return {
            "id": config.id,
            "provider_type": config.provider_type,
            "name": config.name,
            "is_enabled": config.is_enabled,
            "is_default": config.is_default,
            "api_config": json.loads(config.api_config) if config.api_config else {},
            "default_params": json.loads(config.default_params) if config.default_params else {},
            "priority": config.priority,
            "created_at": config.created_at.isoformat() if config.created_at else None,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None
        }
    
    async def create_config(
        self,
        db: AsyncSession,
        provider_type: str,
        name: str,
        api_config: Dict[str, Any],
        default_params: Optional[Dict[str, Any]] = None,
        is_default: bool = False,
        is_enabled: bool = True,
        priority: int = 0
    ) -> ImageProviderConfig:
        """创建配置"""
        # 如果设为默认，取消其他默认配置
        if is_default:
            await db.execute(
                update(ImageProviderConfig)
                .values(is_default=False)
            )
        
        config = ImageProviderConfig(
            provider_type=provider_type,
            name=name,
            api_config=json.dumps(api_config) if api_config else None,
            default_params=json.dumps(default_params) if default_params else None,
            is_enabled=is_enabled,
            is_default=is_default,
            priority=priority
        )
        
        db.add(config)
        await db.commit()
        await db.refresh(config)
        
        logger.info(f"创建图片生成配置: {name} ({provider_type})")
        return config
    
    async def update_config(
        self,
        db: AsyncSession,
        config_id: int,
        **kwargs
    ) -> Optional[ImageProviderConfig]:
        """更新配置"""
        result = await db.execute(
            select(ImageProviderConfig).where(ImageProviderConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            return None
        
        # 如果设为默认，取消其他默认配置
        if kwargs.get("is_default") and not config.is_default:
            await db.execute(
                update(ImageProviderConfig)
                .values(is_default=False)
            )
        
        # 更新字段
        if "name" in kwargs:
            config.name = kwargs["name"]
        if "api_config" in kwargs:
            config.api_config = json.dumps(kwargs["api_config"])
        if "default_params" in kwargs:
            config.default_params = json.dumps(kwargs["default_params"])
        if "is_enabled" in kwargs:
            config.is_enabled = kwargs["is_enabled"]
        if "is_default" in kwargs:
            config.is_default = kwargs["is_default"]
        if "priority" in kwargs:
            config.priority = kwargs["priority"]
        
        await db.commit()
        await db.refresh(config)
        
        # 清除缓存
        cache_key = f"{config.provider_type}_{config_id}"
        if cache_key in self._provider_cache:
            del self._provider_cache[cache_key]
        
        logger.info(f"更新图片生成配置: {config.name}")
        return config
    
    async def delete_config(self, db: AsyncSession, config_id: int) -> bool:
        """删除配置"""
        result = await db.execute(
            select(ImageProviderConfig).where(ImageProviderConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            return False
        
        # 清除缓存
        cache_key = f"{config.provider_type}_{config_id}"
        if cache_key in self._provider_cache:
            del self._provider_cache[cache_key]
        
        await db.delete(config)
        await db.commit()
        
        logger.info(f"删除图片生成配置: {config.name}")
        return True
    
    async def get_default_provider(self, db: AsyncSession) -> Optional[BaseImageProvider]:
        """获取默认的提供商实例"""
        # 优先获取标记为默认的启用配置
        result = await db.execute(
            select(ImageProviderConfig)
            .where(ImageProviderConfig.is_enabled == True)
            .where(ImageProviderConfig.is_default == True)
            .order_by(ImageProviderConfig.priority)
        )
        config = result.scalar_one_or_none()
        
        # 如果没有默认配置，获取优先级最高的启用配置
        if not config:
            result = await db.execute(
                select(ImageProviderConfig)
                .where(ImageProviderConfig.is_enabled == True)
                .order_by(ImageProviderConfig.priority)
            )
            config = result.scalar_one_or_none()
        
        if not config:
            return None
        
        return self._get_or_create_provider(config)
    
    async def get_provider_by_id(
        self,
        db: AsyncSession,
        config_id: int
    ) -> Optional[BaseImageProvider]:
        """根据ID获取提供商实例"""
        result = await db.execute(
            select(ImageProviderConfig).where(ImageProviderConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        
        if not config or not config.is_enabled:
            return None
        
        return self._get_or_create_provider(config)
    
    def _get_or_create_provider(self, config: ImageProviderConfig) -> Optional[BaseImageProvider]:
        """获取或创建提供商实例"""
        cache_key = f"{config.provider_type}_{config.id}"
        
        if cache_key in self._provider_cache:
            return self._provider_cache[cache_key]
        
        api_config = json.loads(config.api_config) if config.api_config else {}
        provider = create_provider(config.provider_type, api_config)
        
        if provider:
            self._provider_cache[cache_key] = provider
        
        return provider
    
    async def test_config(self, db: AsyncSession, config_id: int) -> Dict[str, Any]:
        """测试配置是否有效"""
        result = await db.execute(
            select(ImageProviderConfig).where(ImageProviderConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            return {"success": False, "message": "配置不存在"}
        
        api_config = json.loads(config.api_config) if config.api_config else {}
        provider = create_provider(config.provider_type, api_config)
        
        if not provider:
            return {"success": False, "message": "无法创建提供商实例"}
        
        if not provider.validate_config():
            return {"success": False, "message": "配置验证失败，请检查API Key等配置"}
        
        # 获取配置的默认尺寸参数
        default_params = json.loads(config.default_params) if config.default_params else {}
        # 使用配置中的尺寸，如果没有则使用 512x512（测试用小尺寸）
        test_width = default_params.get('width', 512)
        test_height = default_params.get('height', 512)
        # 测试时使用较小的尺寸以节省资源，但保持相同的宽高比
        if test_width > 512 or test_height > 512:
            ratio = test_width / test_height
            if ratio >= 1:
                test_width = 512
                test_height = int(512 / ratio)
            else:
                test_height = 512
                test_width = int(512 * ratio)
        
        # 尝试生成一张测试图片
        try:
            test_prompt = "A simple test image, blue sky with white clouds"
            image_path = await provider.generate(test_prompt, width=test_width, height=test_height)
            
            if image_path:
                # 清理测试图片
                import os
                if os.path.exists(image_path):
                    os.remove(image_path)
                return {"success": True, "message": f"配置测试成功（测试尺寸: {test_width}x{test_height}）"}
            else:
                return {"success": False, "message": "图片生成失败，请检查配置"}
                
        except Exception as e:
            return {"success": False, "message": f"测试失败: {str(e)}"}
    
    async def generate_cover(
        self,
        db: AsyncSession,
        title: str,
        provider_id: Optional[int] = None,
        width: int = 900,
        height: int = 500,
        **kwargs
    ) -> Optional[str]:
        """
        生成文章封面图
        
        Args:
            title: 文章标题
            provider_id: 指定提供商配置ID，None则使用默认
            width: 图片宽度
            height: 图片高度
            
        Returns:
            生成的图片本地路径
        """
        # 获取要尝试的提供商列表
        providers_to_try = []
        
        if provider_id:
            # 指定了特定提供商
            result = await db.execute(
                select(ImageProviderConfig).where(ImageProviderConfig.id == provider_id)
            )
            config = result.scalar_one_or_none()
            if config and config.is_enabled:
                provider = self._get_or_create_provider(config)
                if provider and provider.validate_config():
                    providers_to_try.append((config.provider_type, provider))
        else:
            # 获取所有启用的提供商，并按项目策略排序
            configs = await self.get_all_configs(db)
            sorted_configs = self._sort_configs_for_generation(configs)

            for config in sorted_configs:
                provider = self._get_or_create_provider_by_config(config)
                if not provider:
                    continue
                if not provider.validate_config():
                    logger.warning(f"跳过未通过配置校验的图源: {config.get('provider_type')}")
                    continue
                providers_to_try.append((config.get("provider_type", "unknown"), provider))
        
        if not providers_to_try:
            logger.error("没有可用的图片生成提供商")
            return None

        provider_chain = " -> ".join([item[0] for item in providers_to_try])
        logger.info(f"封面图生成候选链路: {provider_chain}")
        
        # 构建提示词
        prompt = self._build_cover_prompt(title, kwargs.get("style", "professional"))
        
        # 依次尝试每个提供商
        for i, (provider_name, provider) in enumerate(providers_to_try):
            try:
                logger.info(f"尝试使用第 {i+1} 个提供商生成封面图: {provider_name}")
                image_path = await provider.generate(prompt, width=width, height=height, **kwargs)
                if image_path:
                    logger.info(f"第 {i+1} 个提供商生成成功: {provider_name}")
                    return image_path
            except Exception as e:
                logger.warning(f"第 {i+1} 个提供商生成失败 ({provider_name}): {e}")
                continue
        
        logger.error("所有图片提供商都失败")
        return None

    def _sort_configs_for_generation(self, configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按项目策略排序可用于生成的配置"""
        enabled_configs = [cfg for cfg in configs if cfg.get("is_enabled")]
        if not enabled_configs:
            return []

        # 每个 provider_type 只保留一个最优配置，避免重复尝试同类图源
        best_by_type: Dict[str, Dict[str, Any]] = {}
        for cfg in enabled_configs:
            provider_type = cfg.get("provider_type", "")
            current_best = best_by_type.get(provider_type)
            if not current_best:
                best_by_type[provider_type] = cfg
                continue

            current_key = (
                0 if current_best.get("is_default") else 1,
                current_best.get("priority", 999),
                current_best.get("id", 0),
            )
            new_key = (
                0 if cfg.get("is_default") else 1,
                cfg.get("priority", 999),
                cfg.get("id", 0),
            )
            if new_key < current_key:
                best_by_type[provider_type] = cfg

        ordered = list(best_by_type.values())
        ordered.sort(
            key=lambda cfg: (
                self._provider_priority_order.get(cfg.get("provider_type", ""), 99),
                0 if cfg.get("is_default") else 1,
                cfg.get("priority", 999),
                cfg.get("id", 0),
            )
        )
        return ordered
    
    def _get_or_create_provider_by_config(self, config: Dict[str, Any]) -> Optional[BaseImageProvider]:
        """根据配置字典获取或创建提供商实例"""
        from .image_providers import create_provider
        
        cache_key = f"{config.get('provider_type')}_{config.get('id')}"
        
        if cache_key in self._provider_cache:
            return self._provider_cache[cache_key]
        
        api_config = config.get("api_config", {})
        provider = create_provider(config.get("provider_type"), api_config)
        
        if provider:
            self._provider_cache[cache_key] = provider
        
        return provider
    
    def _build_cover_prompt(self, title: str, style: str = "professional", article_type: str = "general") -> str:
        """构建封面图提示词 - 专业自媒体创作者角度
        
        优化要点：
        1. 中文场景化描述，更符合通义万相的理解
        2. 情感化关键词，增强视觉冲击力
        3. 根据文章类型自动匹配视觉风格
        4. 包含色彩、构图、氛围的具体描述
        """
        
        # 根据文章类型匹配视觉风格描述
        type_visual_styles = {
            "social": {
                "mood": "温暖、亲切、有共鸣感",
                "colors": "暖色调，橙黄、米白、柔和蓝",
                "elements": "人物剪影、生活场景、情感符号",
                "composition": "中心构图，突出人情味"
            },
            "business": {
                "mood": "专业、高端、可信赖",
                "colors": "深蓝、金色、黑白灰",
                "elements": "数据可视化、商务场景、城市建筑",
                "composition": "对称构图，突出稳重感"
            },
            "tech": {
                "mood": "未来感、科技感、创新精神",
                "colors": "科技蓝、电光紫、银白",
                "elements": "电路纹理、光效、抽象科技元素",
                "composition": "动感构图，斜线或放射状"
            },
            "lifestyle": {
                "mood": "舒适、品质生活、小确幸",
                "colors": "莫兰迪色系、暖灰、薄荷绿",
                "elements": "生活好物、咖啡、书籍、植物",
                "composition": "平铺或45度角，ins风"
            },
            "entertainment": {
                "mood": "活泼、有趣、轻松",
                "colors": "明亮鲜艳、撞色、彩虹色",
                "elements": "表情符号、流行元素、娱乐图标",
                "composition": "活泼构图，打破常规"
            },
            "general": {
                "mood": "专业且有温度",
                "colors": "蓝白配色、渐变",
                "elements": "抽象图形、文字排版",
                "composition": "简洁大气"
            }
        }
        
        visual = type_visual_styles.get(article_type, type_visual_styles["general"])
        
        # 提取标题关键词用于视觉化
        keywords = self._extract_visual_keywords(title)
        
        # 构建中文场景化提示词
        prompts = [
            f"为微信公众号文章创作封面图",
            f"文章主题：{title}",
            f"",
            f"【画面氛围】{visual['mood']}",
            f"【色彩方案】{visual['colors']}",
            f"【视觉元素】{visual['elements']}",
            f"【构图方式】{visual['composition']}",
            f"",
            f"【核心关键词】{keywords}",
            f"",
            f"要求：",
            f"- 画面要有视觉冲击力，第一眼就能吸引读者",
            f"- 避免文字，用视觉符号表达主题",
            f"- 适合手机屏幕观看，主体突出",
            f"- 高质量，细节丰富，专业摄影/插画水准",
            f"- 比例 16:9 或 2.35:1 电影感画幅"
        ]
        
        return "\n".join(prompts)
    
    def _extract_visual_keywords(self, title: str) -> str:
        """从标题提取可视化关键词"""
        import re
        
        # 提取核心名词和动词
        # 移除常见虚词
        stop_words = ['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这']
        
        # 简单提取2-6字的关键词
        words = []
        for i in range(len(title)):
            for j in range(i+2, min(i+7, len(title)+1)):
                word = title[i:j]
                if word not in stop_words:
                    words.append(word)
        
        # 去重并取前3个
        unique_words = list(dict.fromkeys(words))[:3]
        return "、".join(unique_words) if unique_words else title[:10]
    
    def get_available_provider_types(self) -> List[Dict[str, Any]]:
        """获取所有可用的提供商类型"""
        return get_available_providers()


# 全局实例
image_provider_manager = ImageProviderManager()
