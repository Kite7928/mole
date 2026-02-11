"""
配置管理服务
用于读取、保存和更新应用配置
支持多 AI 提供商配置管理
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models.config import AppConfig
from ..models.ai_provider_config import AIProviderConfig, DEFAULT_AI_PROVIDERS
from ..core.logger import logger
from ..core.config import settings


class ConfigService:
    """配置管理服务"""

    # ==================== 多 AI 提供商配置管理 ====================

    async def get_all_provider_configs(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        获取所有 AI 提供商配置

        Args:
            db: 数据库会话

        Returns:
            提供商配置列表
        """
        try:
            query = select(AIProviderConfig).order_by(AIProviderConfig.provider)
            result = await db.execute(query)
            configs = result.scalars().all()

            # 转换为字典列表
            config_list = [config.to_dict(hide_api_key=True) for config in configs]

            # 合并默认配置信息
            merged_configs = []
            for provider_id, default_info in DEFAULT_AI_PROVIDERS.items():
                # 查找数据库中是否已有配置
                db_config = next((c for c in config_list if c["provider"] == provider_id), None)

                merged_config = {
                    **default_info,
                    "id": db_config["id"] if db_config else None,
                    "provider": provider_id,
                    "is_enabled": db_config["is_enabled"] if db_config else False,
                    "api_key": db_config["api_key"] if db_config else None,
                    "has_api_key": db_config["has_api_key"] if db_config else False,
                    "base_url": db_config["base_url"] if db_config else default_info["base_url"],
                    "model": db_config["model"] if db_config else default_info["model"],
                    "is_default": db_config["is_default"] if db_config else False,
                    "is_configured": db_config["has_api_key"] if db_config else False,
                }
                merged_configs.append(merged_config)

            return merged_configs

        except Exception as e:
            logger.error(f"获取所有提供商配置失败: {str(e)}")
            raise

    async def get_provider_config(self, db: AsyncSession, provider: str) -> Optional[Dict[str, Any]]:
        """
        获取指定提供商配置

        Args:
            db: 数据库会话
            provider: 提供商标识

        Returns:
            提供商配置字典，如果不存在返回 None
        """
        try:
            query = select(AIProviderConfig).where(AIProviderConfig.provider == provider)
            result = await db.execute(query)
            config = result.scalar_one_or_none()

            if config:
                return config.to_dict(hide_api_key=True)

            # 返回默认配置
            if provider in DEFAULT_AI_PROVIDERS:
                default_info = DEFAULT_AI_PROVIDERS[provider]
                return {
                    **default_info,
                    "provider": provider,
                    "is_enabled": False,
                    "api_key": None,
                    "has_api_key": False,
                    "base_url": default_info["base_url"],
                    "model": default_info["model"],
                    "is_default": False,
                    "is_configured": False,
                }

            return None

        except Exception as e:
            logger.error(f"获取提供商配置失败: {str(e)}")
            raise

    async def save_provider_config(
        self,
        db: AsyncSession,
        provider: str,
        api_key: str,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        is_enabled: bool = True,
        is_default: bool = False,
        extra_config: Optional[str] = None
    ) -> AIProviderConfig:
        """
        保存 AI 提供商配置

        Args:
            db: 数据库会话
            provider: 提供商标识
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            is_enabled: 是否启用
            is_default: 是否为默认提供商
            extra_config: 额外配置（JSON字符串）

        Returns:
            保存的配置对象
        """
        try:
            # 获取默认配置
            default_info = DEFAULT_AI_PROVIDERS.get(provider, {})
            base_url = base_url or default_info.get("base_url", "")
            model = model or default_info.get("model", "")

            # 如果设置为默认，先取消其他默认设置
            if is_default:
                await db.execute(
                    select(AIProviderConfig).where(AIProviderConfig.is_default == True)
                )
                default_configs = await db.execute(
                    select(AIProviderConfig).where(AIProviderConfig.is_default == True)
                )
                for dc in default_configs.scalars().all():
                    dc.is_default = False

            # 查询是否已有配置
            query = select(AIProviderConfig).where(AIProviderConfig.provider == provider)
            result = await db.execute(query)
            existing_config = result.scalar_one_or_none()

            if existing_config:
                # 更新现有配置
                existing_config.api_key = api_key
                existing_config.base_url = base_url
                existing_config.model = model
                existing_config.is_enabled = is_enabled and bool(api_key)
                existing_config.is_default = is_default
                if extra_config:
                    existing_config.extra_config = extra_config

                await db.commit()
                await db.refresh(existing_config)
                logger.info(f"更新提供商配置成功: {provider}")
                return existing_config
            else:
                # 创建新配置
                config = AIProviderConfig(
                    provider=provider,
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                    is_enabled=is_enabled and bool(api_key),
                    is_default=is_default,
                    extra_config=extra_config
                )

                db.add(config)
                await db.commit()
                await db.refresh(config)
                logger.info(f"创建提供商配置成功: {provider}")
                return config

        except Exception as e:
            logger.error(f"保存提供商配置失败: {str(e)}")
            await db.rollback()
            raise

    async def delete_provider_config(self, db: AsyncSession, provider: str) -> bool:
        """
        删除 AI 提供商配置

        Args:
            db: 数据库会话
            provider: 提供商标识

        Returns:
            是否删除成功
        """
        try:
            query = delete(AIProviderConfig).where(AIProviderConfig.provider == provider)
            result = await db.execute(query)
            await db.commit()

            if result.rowcount > 0:
                logger.info(f"删除提供商配置成功: {provider}")
                return True
            return False

        except Exception as e:
            logger.error(f"删除提供商配置失败: {str(e)}")
            await db.rollback()
            raise

    async def get_configured_providers(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        获取已配置的 AI 提供商列表（按推荐优先级排序）

        Args:
            db: 数据库会话

        Returns:
            已配置的提供商列表（已配置且有 API Key 的排在前面）
        """
        try:
            all_configs = await self.get_all_provider_configs(db)

            # 分离已配置和未配置的
            configured = [c for c in all_configs if c.get("has_api_key")]
            unconfigured = [c for c in all_configs if not c.get("has_api_key")]

            # 已配置的按 is_default 排序
            configured.sort(key=lambda x: (not x.get("is_default", False), x.get("provider")))

            # 未配置的保持默认顺序
            return configured + unconfigured

        except Exception as e:
            logger.error(f"获取已配置提供商失败: {str(e)}")
            raise

    async def get_recommended_provider(self, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """
        获取推荐的 AI 提供商（优先返回已配置且启用的提供商）

        Args:
            db: 数据库会话

        Returns:
            推荐的提供商配置
        """
        try:
            configured = await self.get_configured_providers(db)

            # 优先返回默认的已配置提供商
            for provider in configured:
                if provider.get("has_api_key") and provider.get("is_default"):
                    return provider

            # 否则返回第一个已配置的
            for provider in configured:
                if provider.get("has_api_key"):
                    return provider

            # 如果没有配置的，返回 None
            return None

        except Exception as e:
            logger.error(f"获取推荐提供商失败: {str(e)}")
            raise

    async def get_enabled_providers(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        获取所有启用的 AI 提供商

        Args:
            db: 数据库会话

        Returns:
            启用的提供商列表
        """
        try:
            query = select(AIProviderConfig).where(
                AIProviderConfig.is_enabled == True,
                AIProviderConfig.api_key.isnot(None)
            )
            result = await db.execute(query)
            configs = result.scalars().all()

            return [config.to_dict(hide_api_key=True) for config in configs]

        except Exception as e:
            logger.error(f"获取启用提供商失败: {str(e)}")
            raise

    # ==================== 原有单配置管理（保持兼容） ====================

    async def get_config(self, db: AsyncSession) -> Dict[str, Any]:
        """
        获取配置
        
        Args:
            db: 数据库会话
        
        Returns:
            配置字典
        """
        try:
            # 从数据库查询配置
            query = select(AppConfig).order_by(AppConfig.id.desc())
            result = await db.execute(query)
            config = result.scalar_one_or_none()
            
            if config:
                # 返回数据库中的配置（返回真实密钥，前端用密码框隐藏）
                return {
                    "id": config.id,
                    "ai_provider": config.ai_provider,
                    "api_key": config.api_key,  # 返回真实密钥
                    "base_url": config.base_url,
                    "model": config.model,
                    "wechat_app_id": config.wechat_app_id,
                    "wechat_app_secret": config.wechat_app_secret,  # 返回真实密钥
                    "enable_auto_publish": config.enable_auto_publish,
                    "max_news_count": config.max_news_count,
                    "has_api_key": bool(config.api_key),
                    "has_wechat_config": bool(config.wechat_app_id and config.wechat_app_secret)
                }
            else:
                # 返回默认配置
                return {
                    "ai_provider": "deepseek",
                    "api_key": None,
                    "base_url": "https://api.deepseek.com/v1",
                    "model": "deepseek-chat",
                    "wechat_app_id": None,
                    "wechat_app_secret": None,
                    "enable_auto_publish": False,
                    "max_news_count": 20,
                    "has_api_key": False,
                    "has_wechat_config": False
                }
                
        except Exception as e:
            logger.error(f"获取配置失败: {str(e)}")
            raise
    
    async def save_config(
        self,
        db: AsyncSession,
        ai_provider: str,
        api_key: str,
        base_url: str,
        model: str,
        wechat_app_id: str,
        wechat_app_secret: str,
        enable_auto_publish: bool,
        max_news_count: int
    ) -> AppConfig:
        """
        保存配置
        
        Args:
            db: 数据库会话
            ai_provider: AI提供商
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            wechat_app_id: 微信AppID
            wechat_app_secret: 微信AppSecret
            enable_auto_publish: 是否自动发布
            max_news_count: 最大新闻数量
        
        Returns:
            保存的配置对象
        """
        try:
            # 查询是否已有配置
            query = select(AppConfig).order_by(AppConfig.id.desc())
            result = await db.execute(query)
            existing_config = result.scalar_one_or_none()
            
            if existing_config:
                # 更新现有配置
                existing_config.ai_provider = ai_provider
                existing_config.api_key = api_key
                existing_config.base_url = base_url
                existing_config.model = model
                existing_config.wechat_app_id = wechat_app_id
                existing_config.wechat_app_secret = wechat_app_secret
                existing_config.enable_auto_publish = enable_auto_publish
                existing_config.max_news_count = max_news_count
                
                await db.commit()
                await db.refresh(existing_config)
                
                logger.info(f"更新配置成功，ID: {existing_config.id}")
                return existing_config
            else:
                # 创建新配置
                config = AppConfig(
                    ai_provider=ai_provider,
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                    wechat_app_id=wechat_app_id,
                    wechat_app_secret=wechat_app_secret,
                    enable_auto_publish=enable_auto_publish,
                    max_news_count=max_news_count
                )
                
                db.add(config)
                await db.commit()
                await db.refresh(config)
                
                logger.info(f"创建配置成功，ID: {config.id}")
                return config
                
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
            await db.rollback()
            raise
    
    async def test_api_connection(
        self,
        api_key: str,
        base_url: str,
        model: str
    ) -> Dict[str, Any]:
        """
        测试API连接

        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称

        Returns:
            测试结果
        """
        try:
            from openai import AsyncOpenAI

            # 创建客户端
            client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )

            # 测试调用（使用英文避免编码问题）
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=10
            )

            # 关闭客户端
            await client.close()

            return {
                "success": True,
                "message": "API连接测试成功",
                "model": model
            }

        except Exception as e:
            logger.error(f"API连接测试失败: {str(e)}")
            return {
                "success": False,
                "message": f"API连接测试失败: {str(e)}"
            }
    
    async def test_wechat_connection(
        self,
        app_id: str,
        app_secret: str
    ) -> Dict[str, Any]:
        """
        测试微信连接
        
        Args:
            app_id: 微信AppID
            app_secret: 微信AppSecret
        
        Returns:
            测试结果
        """
        try:
            from ..services.wechat_service import wechat_service
            
            # 获取access_token
            access_token = await wechat_service.get_access_token(app_id, app_secret)
            
            return {
                "success": True,
                "message": "微信连接测试成功",
                "access_token": access_token[:20] + "..."  # 只显示部分
            }
            
        except Exception as e:
            logger.error(f"微信连接测试失败: {str(e)}")
            return {
                "success": False,
                "message": f"微信连接测试失败: {str(e)}"
            }


# 全局实例
config_service = ConfigService()