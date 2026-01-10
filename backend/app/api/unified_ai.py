"""
统一AI模型API路由
提供统一的AI调用接口，支持多个提供商和轮询机制
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from ..services.unified_ai_service import (
    unified_ai_service,
    AIProvider,
    RotationStrategy,
    AIResponse
)
from ..core.logger import logger

router = APIRouter()


# Pydantic模型
class Message(BaseModel):
    role: str = Field(..., description="消息角色：system, user, assistant")
    content: str = Field(..., description="消息内容")


class AIRequest(BaseModel):
    messages: List[Message] = Field(..., description="消息列表")
    provider: Optional[str] = Field(None, description="指定提供商（可选）")
    model: Optional[str] = Field(None, description="指定模型（可选）")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(4000, ge=1, le=32000, description="最大token数")
    max_retries: int = Field(3, ge=1, le=10, description="最大重试次数")


class AIResponseModel(BaseModel):
    content: str
    provider: str
    model: str
    token_usage: dict
    finish_reason: str
    metadata: dict
    created_at: str


class ProvidersResponse(BaseModel):
    providers: List[dict]
    current_strategy: str
    enabled_providers: List[str]


class RotationStrategyRequest(BaseModel):
    strategy: str = Field(..., description="轮询策略：sequential 或 random")


# API端点
@router.post("/generate", response_model=AIResponseModel)
async def generate(request: AIRequest):
    """
    生成AI响应（支持轮询和重试）
    
    - **provider**: 可选，指定提供商。不指定则使用轮询策略
    - **model**: 可选，指定模型
    - **temperature**: 0.0-2.0，控制创造性
    - **max_tokens**: 最大生成token数
    - **max_retries**: 失败重试次数
    """
    try:
        # 转换消息格式
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # 解析提供商
        provider = None
        if request.provider:
            try:
                provider = AIProvider(request.provider)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid provider: {request.provider}")
        
        # 生成响应
        response = await unified_ai_service.generate(
            messages=messages,
            provider=provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            max_retries=request.max_retries
        )
        
        return response.to_dict()
        
    except Exception as e:
        logger.error(f"Error in generate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers", response_model=ProvidersResponse)
async def get_providers():
    """
    获取所有可用的AI提供商
    
    返回所有提供商的列表，包括：
    - 提供商名称
    - 是否可用
    - 默认模型
    - 当前轮询策略
    - 已启用的提供商列表
    """
    try:
        providers = unified_ai_service.get_available_providers()
        
        return {
            "providers": providers,
            "current_strategy": unified_ai_service.rotation_strategy.value,
            "enabled_providers": [p.value for p in unified_ai_service.enabled_providers]
        }
        
    except Exception as e:
        logger.error(f"Error in get_providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rotation-strategy")
async def set_rotation_strategy(request: RotationStrategyRequest):
    """
    设置轮询策略
    
    - **strategy**: 轮询策略
      - sequential: 顺序轮询（按顺序使用提供商）
      - random: 随机轮询（随机选择提供商）
    """
    try:
        strategy = RotationStrategy(request.strategy)
        unified_ai_service.set_rotation_strategy(strategy)
        
        return {
            "message": f"Rotation strategy set to {strategy.value}",
            "strategy": strategy.value
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid strategy: {request.strategy}. Must be 'sequential' or 'random'")
    except Exception as e:
        logger.error(f"Error in set_rotation_strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{provider}")
async def get_provider_models(provider: str):
    """
    获取指定提供商的可用模型列表
    
    - **provider**: 提供商名称
    """
    try:
        # 验证提供商
        try:
            provider_enum = AIProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
        
        # 获取默认模型
        default_model = unified_ai_service._get_default_model(provider_enum)
        
        # 返回模型列表（这里只返回默认模型，可以根据需要扩展）
        models = {
            "provider": provider,
            "default_model": default_model,
            "available_models": [default_model]  # 可以扩展为从配置或API获取
        }
        
        return models
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_provider_models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-provider")
async def test_provider(
    provider: str = Query(..., description="提供商名称"),
    message: str = Query("Hello, how are you?", description="测试消息")
):
    """
    测试指定的AI提供商是否可用
    
    - **provider**: 提供商名称
    - **message**: 测试消息
    """
    try:
        # 验证提供商
        try:
            provider_enum = AIProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
        
        # 检查提供商是否可用
        if provider_enum not in unified_ai_service.providers:
            return {
                "provider": provider,
                "available": False,
                "error": "Provider not configured or API key missing"
            }
        
        # 发送测试请求
        messages = [{"role": "user", "content": message}]
        response = await unified_ai_service.generate(
            messages=messages,
            provider=provider_enum,
            max_tokens=100
        )
        
        return {
            "provider": provider,
            "available": True,
            "model": response.model,
            "response": response.content[:200] + "..." if len(response.content) > 200 else response.content,
            "token_usage": response.token_usage.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in test_provider: {str(e)}")
        return {
            "provider": provider,
            "available": False,
            "error": str(e)
        }


@router.get("/stats")
async def get_stats():
    """
    获取AI服务统计信息
    
    返回：
    - 可用提供商数量
    - 已启用提供商列表
    - 当前轮询策略
    - 服务状态
    """
    try:
        available_providers = len(unified_ai_service.providers)
        enabled_providers = [p.value for p in unified_ai_service.enabled_providers]
        
        return {
            "available_providers": available_providers,
            "enabled_providers": enabled_providers,
            "current_strategy": unified_ai_service.rotation_strategy.value,
            "status": "running",
            "service_version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Error in get_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))