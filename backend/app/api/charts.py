"""
图表API路由
提供图表生成和数据服务
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from ..services.chart_service import chart_service, ChartData

router = APIRouter()


class GenerateChartRequest(BaseModel):
    """生成图表请求"""
    chart_type: str = Field(default="bar", description="图表类型: bar, line, pie, area")
    title: str = Field(..., description="图表标题")
    data: Dict[str, Any] = Field(..., description="图表数据")
    options: Optional[Dict[str, Any]] = Field(default=None, description="图表配置选项")


class ParseChartRequest(BaseModel):
    """解析文本生成图表请求"""
    text: str = Field(..., description="包含数据的文本")
    chart_type: str = Field(default="bar", description="图表类型")


class SampleChartRequest(BaseModel):
    """生成示例图表请求"""
    topic: str = Field(..., description="主题/话题")


class ChartResponse(BaseModel):
    """图表响应"""
    success: bool
    data: Optional[ChartData] = None
    message: str = ""


@router.post("/generate", response_model=ChartResponse)
async def generate_chart(request: GenerateChartRequest):
    """
    生成图表数据
    
    根据提供的数据生成图表配置
    """
    try:
        chart_data = chart_service.generate_chart_data(
            chart_type=request.chart_type,
            title=request.title,
            data=request.data,
            options=request.options
        )
        return ChartResponse(
            success=True,
            data=chart_data,
            message="图表生成成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图表生成失败: {str(e)}")


@router.post("/parse", response_model=ChartResponse)
async def parse_chart(request: ParseChartRequest):
    """
    从文本解析生成图表
    
    支持格式:
    - CSV格式: 标题\n标签1,值1\n标签2,值2
    - JSON格式: {"labels": [...], "values": [...]}
    """
    try:
        chart_data = chart_service.parse_text_to_chart(
            text=request.text,
            chart_type=request.chart_type
        )
        
        if chart_data is None:
            return ChartResponse(
                success=False,
                message="无法从文本中解析出有效数据"
            )
        
        return ChartResponse(
            success=True,
            data=chart_data,
            message="图表解析成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图表解析失败: {str(e)}")


@router.post("/sample", response_model=ChartResponse)
async def sample_chart(request: SampleChartRequest):
    """
    生成示例图表
    
    根据主题生成示例图表数据
    """
    try:
        chart_data = chart_service.generate_sample_chart(topic=request.topic)
        return ChartResponse(
            success=True,
            data=chart_data,
            message="示例图表生成成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"示例图表生成失败: {str(e)}")


@router.get("/types")
async def get_chart_types():
    """
    获取支持的图表类型列表
    """
    return {
        "success": True,
        "types": [
            {"value": "bar", "label": "柱状图", "icon": "BarChart"},
            {"value": "line", "label": "折线图", "icon": "LineChart"},
            {"value": "pie", "label": "饼图", "icon": "PieChart"},
            {"value": "area", "label": "面积图", "icon": "AreaChart"}
        ]
    }
