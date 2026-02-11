"""
配置管理API路由
支持获取、保存、测试配置
支持多AI提供商配置管理
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from ..core.database import get_db
from ..core.logger import logger
from ..services.config_service import config_service


router = APIRouter()


class ConfigRequest(BaseModel):
    """配置请求模型"""
    ai_provider: str = Field(default="deepseek", description="AI提供商")
    api_key: str = Field(..., description="API密钥")
    base_url: str = Field(default="https://api.deepseek.com/v1", description="API基础URL")
    model: str = Field(default="deepseek-chat", description="模型名称")
    wechat_app_id: Optional[str] = Field(None, description="微信AppID")
    wechat_app_secret: Optional[str] = Field(None, description="微信AppSecret")
    enable_auto_publish: bool = Field(default=False, description="是否自动发布")
    max_news_count: int = Field(default=20, ge=1, le=100, description="最大新闻数量")


class TestAPIRequest(BaseModel):
    """测试API请求"""
    api_key: str = Field(..., min_length=1, description="API密钥")
    base_url: str = Field(default="https://api.deepseek.com/v1", description="API基础URL")
    model: str = Field(default="deepseek-chat", description="模型名称")


class TestWeChatRequest(BaseModel):
    """测试微信请求"""
    app_id: str = Field(..., min_length=1, description="微信AppID")
    app_secret: str = Field(..., min_length=1, description="微信AppSecret")


class ProviderConfigRequest(BaseModel):
    """AI提供商配置请求"""
    provider: str = Field(..., description="提供商标识")
    api_key: str = Field(..., description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")
    model: Optional[str] = Field(None, description="模型名称")
    is_enabled: bool = Field(default=True, description="是否启用")
    is_default: bool = Field(default=False, description="是否为默认提供商")


# ==================== 多AI提供商配置管理 ====================

@router.get("/providers", response_model=dict)
async def get_all_providers(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有AI提供商配置（包括默认配置和数据库中的配置）

    Returns:
        所有提供商配置列表，已配置的会标记 has_api_key=true
    """
    try:
        configs = await config_service.get_all_provider_configs(db)
        return {
            "success": True,
            "providers": configs,
            "total": len(configs)
        }
    except Exception as e:
        logger.error(f"获取所有提供商配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取提供商配置失败: {str(e)}")


@router.get("/providers/status/overview", response_model=dict)
async def get_providers_status(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有提供商的状态概览

    Returns:
        提供商状态概览，包括已配置数量、推荐提供商等
    """
    try:
        all_providers = await config_service.get_all_provider_configs(db)
        configured = await config_service.get_configured_providers(db)
        recommended = await config_service.get_recommended_provider(db)

        configured_count = len([p for p in all_providers if p.get("has_api_key")])
        enabled_count = len([p for p in all_providers if p.get("is_enabled") and p.get("has_api_key")])

        return {
            "success": True,
            "overview": {
                "total_providers": len(all_providers),
                "configured_count": configured_count,
                "enabled_count": enabled_count,
                "has_recommended": recommended is not None,
                "recommended_provider": recommended.get("provider") if recommended else None,
                "recommended_name": recommended.get("name") if recommended else None
            },
            "providers": all_providers
        }
    except Exception as e:
        logger.error(f"获取提供商状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取提供商状态失败: {str(e)}")


@router.get("/providers/configured", response_model=dict)
async def get_configured_providers(
    db: AsyncSession = Depends(get_db)
):
    """
    获取已配置的AI提供商列表（按推荐优先级排序）

    返回的列表中，已配置且有API Key的提供商会排在前面，
    默认提供商会排在最前面。

    Returns:
        已配置的提供商列表
    """
    try:
        providers = await config_service.get_configured_providers(db)

        # 分离已配置和未配置的
        configured = [p for p in providers if p.get("has_api_key")]
        unconfigured = [p for p in providers if not p.get("has_api_key")]

        return {
            "success": True,
            "providers": providers,
            "configured_count": len(configured),
            "unconfigured_count": len(unconfigured),
            "configured": configured,
            "unconfigured": unconfigured
        }
    except Exception as e:
        logger.error(f"获取已配置提供商失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取已配置提供商失败: {str(e)}")


@router.get("/providers/recommended", response_model=dict)
async def get_recommended_provider(
    db: AsyncSession = Depends(get_db)
):
    """
    获取推荐的AI提供商

    优先返回已配置且设置为默认的提供商，
    如果没有默认的，返回第一个已配置的，
    如果没有配置的，返回 null。

    Returns:
        推荐的提供商配置
    """
    try:
        provider = await config_service.get_recommended_provider(db)

        if provider:
            return {
                "success": True,
                "provider": provider,
                "message": f"推荐使用 {provider.get('name', provider.get('provider'))}"
            }
        else:
            return {
                "success": True,
                "provider": None,
                "message": "暂无已配置的AI提供商，请先配置至少一个提供商"
            }
    except Exception as e:
        logger.error(f"获取推荐提供商失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取推荐提供商失败: {str(e)}")


# 注意：具体路径的路由必须放在带参数的路由之前！
# 如 /providers/status/overview 必须在 /providers/{provider} 之前

@router.get("/providers/{provider}", response_model=dict)
async def get_provider_config(
    provider: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定提供商配置

    Args:
        provider: 提供商标识（如 openai, deepseek, claude 等）

    Returns:
        提供商配置
    """
    try:
        config = await config_service.get_provider_config(db, provider)

        if config:
            return {
                "success": True,
                "config": config
            }
        else:
            raise HTTPException(status_code=404, detail=f"提供商 {provider} 不存在")
    except Exception as e:
        logger.error(f"获取提供商配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取提供商配置失败: {str(e)}")


@router.post("/providers", response_model=dict)
async def save_provider_config(
    request: ProviderConfigRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    保存AI提供商配置
    
    Args:
        request: 提供商配置请求
    
    Returns:
        保存结果
    """
    try:
        config = await config_service.save_provider_config(
            db=db,
            provider=request.provider,
            api_key=request.api_key,
            base_url=request.base_url,
            model=request.model,
            is_enabled=request.is_enabled,
            is_default=request.is_default
        )
        
        return {
            "success": True,
            "message": f"提供商 {request.provider} 配置保存成功",
            "config": config.to_dict(hide_api_key=True)
        }
    except Exception as e:
        logger.error(f"保存提供商配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存提供商配置失败: {str(e)}")


@router.delete("/providers/{provider}", response_model=dict)
async def delete_provider_config(
    provider: str,
    db: AsyncSession = Depends(get_db)
):
    """
    删除AI提供商配置
    
    Args:
        provider: 提供商标识
    
    Returns:
        删除结果
    """
    try:
        success = await config_service.delete_provider_config(db, provider)
        
        if success:
            return {
                "success": True,
                "message": f"提供商 {provider} 配置已删除"
            }
        else:
            raise HTTPException(status_code=404, detail=f"提供商 {provider} 配置不存在")
    except Exception as e:
        logger.error(f"删除提供商配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除提供商配置失败: {str(e)}")


@router.post("/providers/{provider}/test", response_model=dict)
async def test_provider_connection(
    provider: str,
    db: AsyncSession = Depends(get_db)
):
    """
    测试指定提供商的API连接

    Args:
        provider: 提供商标识

    Returns:
        测试结果
    """
    try:
        # 获取提供商配置
        config = await config_service.get_provider_config(db, provider)

        if not config or not config.get("has_api_key"):
            return {
                "success": False,
                "message": f"提供商 {provider} 未配置或缺少API Key"
            }

        # 测试连接
        result = await config_service.test_api_connection(
            api_key=config.get("api_key", ""),
            base_url=config.get("base_url", ""),
            model=config.get("model", "")
        )

        return result

    except Exception as e:
        logger.error(f"测试提供商连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试提供商连接失败: {str(e)}")


# ==================== 原有单配置管理（保持兼容） ====================

@router.get("/", response_model=dict)
async def get_config(db: AsyncSession = Depends(get_db)):
    """
    获取当前配置
    
    Returns:
        配置信息（密钥已隐藏）
    """
    try:
        config = await config_service.get_config(db)
        return {
            "success": True,
            "config": config
        }
    except Exception as e:
        logger.error(f"获取配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.post("/", response_model=dict)
async def save_config(
    request: ConfigRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    保存配置
    
    Args:
        request: 配置请求
        db: 数据库会话
    
    Returns:
        保存结果
    """
    try:
        logger.info("保存配置")
        
        # 保存配置
        config = await config_service.save_config(
            db=db,
            ai_provider=request.ai_provider,
            api_key=request.api_key,
            base_url=request.base_url,
            model=request.model,
            wechat_app_id=request.wechat_app_id,
            wechat_app_secret=request.wechat_app_secret,
            enable_auto_publish=request.enable_auto_publish,
            max_news_count=request.max_news_count
        )
        
        return {
            "success": True,
            "message": "配置保存成功",
            "config_id": config.id
        }
        
    except Exception as e:
        logger.error(f"保存配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")


@router.post("/test-api", response_model=dict)
async def test_api_connection(request: TestAPIRequest):
    """
    测试API连接
    
    Args:
        request: 测试API请求
    
    Returns:
        测试结果
    """
    try:
        result = await config_service.test_api_connection(
            api_key=request.api_key,
            base_url=request.base_url,
            model=request.model
        )
        
        return result
        
    except Exception as e:
        logger.error(f"测试API连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试API连接失败: {str(e)}")


@router.post("/test-wechat", response_model=dict)
async def test_wechat_connection(request: TestWeChatRequest):
    """
    测试微信连接
    
    Args:
        request: 测试微信请求
    
    Returns:
        测试结果
    """
    try:
        result = await config_service.test_wechat_connection(
            app_id=request.app_id,
            app_secret=request.app_secret
        )
        
        return result
        
    except Exception as e:
        logger.error(f"测试微信连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试微信连接失败: {str(e)}")