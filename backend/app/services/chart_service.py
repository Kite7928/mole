"""
图表生成服务
支持生成各种类型的数据图表
"""

import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class ChartData(BaseModel):
    """图表数据模型"""
    type: str  # bar, line, pie, area
    title: str
    labels: List[str]
    datasets: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None


class ChartService:
    """图表生成服务"""
    
    @staticmethod
    def generate_chart_data(
        chart_type: str,
        title: str,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> ChartData:
        """
        生成图表数据
        
        Args:
            chart_type: 图表类型 (bar, line, pie, area)
            title: 图表标题
            data: 原始数据
            options: 可选配置
        
        Returns:
            ChartData: 图表数据对象
        """
        # 提取标签和数据集
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        # 如果没有数据集，创建一个默认的
        if not datasets and 'values' in data:
            datasets = [{
                'label': data.get('series_name', '数据'),
                'data': data['values'],
                'backgroundColor': ChartService._get_colors(chart_type, len(data['values'])),
                'borderColor': ChartService._get_border_colors(chart_type, len(data['values'])),
                'borderWidth': 2
            }]
        
        # 设置默认选项
        default_options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'display': chart_type == 'pie',
                    'position': 'bottom'
                },
                'title': {
                    'display': True,
                    'text': title,
                    'font': {'size': 16}
                }
            },
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'grid': {'color': 'rgba(0,0,0,0.1)'}
                },
                'x': {
                    'grid': {'display': False}
                }
            } if chart_type in ['bar', 'line', 'area'] else {}
        }
        
        # 合并选项
        final_options = {**default_options, **(options or {})}
        
        return ChartData(
            type=chart_type,
            title=title,
            labels=labels,
            datasets=datasets,
            options=final_options
        )
    
    @staticmethod
    def _get_colors(chart_type: str, count: int) -> Any:
        """获取颜色配置"""
        colors = [
            'rgba(99, 102, 241, 0.8)',   # indigo
            'rgba(139, 92, 246, 0.8)',   # purple
            'rgba(236, 72, 153, 0.8)',   # pink
            'rgba(34, 197, 94, 0.8)',    # green
            'rgba(59, 130, 246, 0.8)',   # blue
            'rgba(245, 158, 11, 0.8)',   # amber
            'rgba(239, 68, 68, 0.8)',    # red
            'rgba(20, 184, 166, 0.8)',   # teal
        ]
        
        if chart_type == 'pie':
            return colors[:count] if count <= len(colors) else colors * (count // len(colors) + 1)
        else:
            return colors[0]
    
    @staticmethod
    def _get_border_colors(chart_type: str, count: int) -> Any:
        """获取边框颜色配置"""
        colors = [
            'rgb(99, 102, 241)',
            'rgb(139, 92, 246)',
            'rgb(236, 72, 153)',
            'rgb(34, 197, 94)',
            'rgb(59, 130, 246)',
            'rgb(245, 158, 11)',
            'rgb(239, 68, 68)',
            'rgb(20, 184, 166)',
        ]
        
        if chart_type == 'pie':
            return colors[:count] if count <= len(colors) else colors * (count // len(colors) + 1)
        else:
            return colors[0]
    
    @staticmethod
    def parse_text_to_chart(text: str, chart_type: str = "bar") -> Optional[ChartData]:
        """
        从文本中提取数据并生成图表
        
        支持格式：
        - 表格格式：标题\n标签1,值1\n标签2,值2
        - JSON格式：{"labels": [...], "values": [...]}
        
        Args:
            text: 包含数据的文本
            chart_type: 图表类型
        
        Returns:
            ChartData 或 None
        """
        try:
            # 尝试解析JSON
            if text.strip().startswith('{'):
                data = json.loads(text)
                return ChartService.generate_chart_data(
                    chart_type=chart_type,
                    title=data.get('title', '数据图表'),
                    data=data
                )
            
            # 解析CSV/表格格式
            lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
            if len(lines) < 2:
                return None
            
            title = lines[0]
            labels = []
            values = []
            
            for line in lines[1:]:
                parts = line.split(',')
                if len(parts) >= 2:
                    labels.append(parts[0].strip())
                    try:
                        values.append(float(parts[1].strip()))
                    except ValueError:
                        continue
            
            if not labels or not values:
                return None
            
            return ChartService.generate_chart_data(
                chart_type=chart_type,
                title=title,
                data={
                    'labels': labels,
                    'values': values,
                    'series_name': '数值'
                }
            )
        
        except Exception as e:
            print(f"解析图表数据失败: {e}")
            return None
    
    @staticmethod
    def generate_sample_chart(topic: str) -> ChartData:
        """
        根据主题生成示例图表数据
        
        Args:
            topic: 主题/话题
        
        Returns:
            ChartData: 示例图表数据
        """
        sample_data = {
            '增长趋势': {
                'type': 'line',
                'labels': ['1月', '2月', '3月', '4月', '5月', '6月'],
                'datasets': [{
                    'label': '增长率 (%)',
                    'data': [12, 19, 25, 32, 45, 58],
                    'borderColor': 'rgb(99, 102, 241)',
                    'backgroundColor': 'rgba(99, 102, 241, 0.1)',
                    'tension': 0.4,
                    'fill': True
                }]
            },
            '市场份额': {
                'type': 'pie',
                'labels': ['产品A', '产品B', '产品C', '产品D', '其他'],
                'datasets': [{
                    'label': '市场份额 (%)',
                    'data': [35, 25, 20, 15, 5],
                    'backgroundColor': [
                        'rgba(99, 102, 241, 0.8)',
                        'rgba(139, 92, 246, 0.8)',
                        'rgba(236, 72, 153, 0.8)',
                        'rgba(34, 197, 94, 0.8)',
                        'rgba(156, 163, 175, 0.8)'
                    ]
                }]
            },
            '对比分析': {
                'type': 'bar',
                'labels': ['指标1', '指标2', '指标3', '指标4', '指标5'],
                'datasets': [
                    {
                        'label': '今年',
                        'data': [85, 92, 78, 95, 88],
                        'backgroundColor': 'rgba(99, 102, 241, 0.8)'
                    },
                    {
                        'label': '去年',
                        'data': [72, 85, 65, 88, 75],
                        'backgroundColor': 'rgba(156, 163, 175, 0.8)'
                    }
                ]
            }
        }
        
        # 根据主题关键词选择合适的数据
        data_key = '增长趋势'
        if '份额' in topic or '占比' in topic or '分布' in topic:
            data_key = '市场份额'
        elif '对比' in topic or '比较' in topic or 'vs' in topic.lower():
            data_key = '对比分析'
        
        data = sample_data[data_key]
        return ChartData(
            type=data['type'],
            title=f'{topic} - {data_key}',
            labels=data['labels'],
            datasets=data['datasets']
        )


chart_service = ChartService()
