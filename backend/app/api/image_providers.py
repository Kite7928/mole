"""
图片生成服务提供商配置API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.logger import logger
from ..services.image_provider_manager import image_provider_manager

router = APIRouter(tags=["图片生成配置"])


class ProviderConfigCreate(BaseModel):
    """创建提供商配置请求"""
    provider_type: str = Field(..., description="提供商类型")
    name: str = Field(..., min_length=1, max_length=100, description="配置名称")
    api_config: dict = Field(default={}, description="API配置")
    default_params: dict = Field(default={}, description="默认生成参数")
    is_default: bool = Field(default=False, description="是否设为默认")
    priority: int = Field(default=0, description="优先级")


class ProviderConfigUpdate(BaseModel):
    """更新提供商配置请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    api_config: Optional[dict] = None
    default_params: Optional[dict] = None
    is_enabled: Optional[bool] = None
    is_default: Optional[bool] = None
    priority: Optional[int] = None


class CoverGenerateRequest(BaseModel):
    """生成封面图请求"""
    title: str = Field(..., min_length=1, description="文章标题")
    provider_id: Optional[int] = Field(None, description="指定提供商配置ID")
    width: int = Field(default=900, ge=100, le=1920, description="图片宽度")
    height: int = Field(default=500, ge=100, le=1080, description="图片高度")
    style: str = Field(default="professional", description="图片风格")


@router.get("/types", response_model=dict)
async def get_provider_types():
    """
    获取所有可用的图片生成提供商类型
    """
    try:
        providers = image_provider_manager.get_available_provider_types()
        return {
            "success": True,
            "providers": providers
        }
    except Exception as e:
        logger.error(f"获取提供商类型失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configs", response_model=dict)
async def get_all_configs(db: AsyncSession = Depends(get_db)):
    """
    获取所有图片生成提供商配置
    """
    try:
        configs = await image_provider_manager.get_all_configs(db)
        return {
            "success": True,
            "configs": configs
        }
    except Exception as e:
        logger.error(f"获取配置列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configs/{config_id}", response_model=dict)
async def get_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """
    获取单个配置详情
    """
    try:
        config = await image_provider_manager.get_config(db, config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        return {
            "success": True,
            "config": config
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/configs", response_model=dict)
async def create_config(
    request: ProviderConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的图片生成提供商配置
    
    示例:
    ```json
    {
        "provider_type": "pollinations",
        "name": "Pollinations免费生成",
        "api_config": {},
        "default_params": {"width": 900, "height": 500},
        "is_default": true,
        "priority": 0
    }
    ```
    """
    try:
        config = await image_provider_manager.create_config(
            db=db,
            provider_type=request.provider_type,
            name=request.name,
            api_config=request.api_config,
            default_params=request.default_params,
            is_default=request.is_default,
            priority=request.priority
        )
        
        return {
            "success": True,
            "message": "配置创建成功",
            "config_id": config.id
        }
        
    except Exception as e:
        logger.error(f"创建配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/configs/{config_id}", response_model=dict)
async def update_config(
    config_id: int,
    request: ProviderConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新图片生成提供商配置
    """
    try:
        config = await image_provider_manager.update_config(
            db=db,
            config_id=config_id,
            **request.dict(exclude_unset=True)
        )
        
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        return {
            "success": True,
            "message": "配置更新成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/configs/{config_id}", response_model=dict)
async def delete_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """
    删除图片生成提供商配置
    """
    try:
        success = await image_provider_manager.delete_config(db, config_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        return {
            "success": True,
            "message": "配置删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/configs/{config_id}/test", response_model=dict)
async def test_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """
    测试配置是否有效
    
    会尝试使用配置生成一张测试图片来验证配置是否正确
    """
    try:
        result = await image_provider_manager.test_config(db, config_id)
        return result
        
    except Exception as e:
        logger.error(f"测试配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-cover", response_model=dict)
async def generate_cover(
    request: CoverGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    生成文章封面图
    
    示例:
    ```json
    {
        "title": "人工智能如何改变世界",
        "provider_id": 1,
        "width": 900,
        "height": 500,
        "style": "tech"
    }
    ```
    """
    try:
        image_path = await image_provider_manager.generate_cover(
            db=db,
            title=request.title,
            provider_id=request.provider_id,
            width=request.width,
            height=request.height,
            style=request.style
        )
        
        if not image_path:
            raise HTTPException(status_code=500, detail="图片生成失败")
        
        # 返回图片URL（相对于uploads目录）
        from pathlib import Path
        from ..core.config import settings
        
        upload_path = Path(image_path)
        relative_path = upload_path.name
        
        return {
            "success": True,
            "message": "封面图生成成功",
            "cover_image_url": f"uploads/{relative_path}",
            "title": request.title
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成封面图失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-setup", response_model=dict)
async def quick_setup(db: AsyncSession = Depends(get_db)):
    """
    快速设置 - 创建推荐的默认配置
    
    会自动创建以下免费提供商的默认配置（按优先级排序）：
    1. Pollinations.ai（无需API Key，完全免费）
    2. Pexels（免费图库，需要API Key但免费注册）
    """
    try:
        created_configs = []
        
        # 1. 创建Pollinations配置（无需API Key）
        try:
            config1 = await image_provider_manager.create_config(
                db=db,
                provider_type="pollinations",
                name="Pollinations.ai（免费）",
                api_config={},
                default_params={"width": 900, "height": 500, "model": "flux"},
                is_default=True,
                priority=0
            )
            created_configs.append({"id": config1.id, "name": config1.name, "type": "pollinations"})
        except Exception as e:
            logger.warning(f"创建Pollinations配置失败: {e}")
        
        # 2. 创建Pexels配置（需要用户后续填写API Key）
        try:
            config2 = await image_provider_manager.create_config(
                db=db,
                provider_type="pexels",
                name="Pexels免费图库（需配置API Key）",
                api_config={"api_key": "请填写你的Pexels API Key"},
                default_params={"width": 900, "height": 500},
                is_default=False,
                priority=1
            )
            created_configs.append({"id": config2.id, "name": config2.name, "type": "pexels"})
        except Exception as e:
            logger.warning(f"创建Pexels配置失败: {e}")
        
        return {
            "success": True,
            "message": f"快速设置完成，创建了 {len(created_configs)} 个配置",
            "configs": created_configs,
            "note": "Pollinations.ai 可以立即使用（无需API Key），Pexels需要配置API Key后使用"
        }
        
    except Exception as e:
        logger.error(f"快速设置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class TongyiConfigRequest(BaseModel):
    """通义万相配置请求"""
    api_key: str = Field(..., min_length=10, description="阿里云API Key")
    name: str = Field(default="通义万相（阿里）", description="配置名称")
    is_default: bool = Field(default=False, description="是否设为默认")


@router.post("/setup-tongyi", response_model=dict)
async def setup_tongyi(
    request: TongyiConfigRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    快速配置通义万相（阿里）
    
    示例:
    ```json
    {
        "api_key": "sk-cc858afbb27242d7afea9969a66ac5f4",
        "name": "通义万相",
        "is_default": true
    }
    ```
    """
    try:
        config = await image_provider_manager.create_config(
            db=db,
            provider_type="tongyi_wanxiang",
            name=request.name,
            api_config={
                "api_key": request.api_key,
                "base_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
                "model": "wanx-v1"
            },
            default_params={
                "width": 900,
                "height": 500,
                "style": "<auto>"
            },
            is_default=request.is_default,
            priority=0 if request.is_default else 1
        )
        
        return {
            "success": True,
            "message": "通义万相配置成功",
            "config_id": config.id,
            "provider_type": "tongyi_wanxiang",
            "note": "配置已保存，可以使用通义万相生成封面图了"
        }
        
    except Exception as e:
        logger.error(f"配置通义万相失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))