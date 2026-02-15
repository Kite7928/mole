"""
热门话题数据模型 - 增强版
支持热度历史追踪、趋势分析、多维度筛选
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean, Index
from datetime import datetime
from ..core.database import Base
import json


class Hotspot(Base):
    """热门话题模型 - 增强版"""

    __tablename__ = "hotspots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rank = Column(Integer, nullable=False, index=True, comment="排名")
    title = Column(String(500), nullable=False, index=True, comment="话题标题")
    url = Column(String(1000), nullable=True, comment="话题链接")
    source = Column(String(50), nullable=False, index=True, comment="来源（weibo/zhihu/bilibili等）")
    category = Column(String(100), nullable=True, index=True, comment="分类")
    tags = Column(Text, nullable=True, comment="标签（逗号分隔）")
    heat = Column(Integer, default=0, index=True, comment="热度值")
    heat_trend = Column(Float, default=0.0, comment="热度趋势（百分比变化）")
    
    # 内容摘要和关键词
    summary = Column(Text, nullable=True, comment="内容摘要")
    keywords = Column(Text, nullable=True, comment="关键词（逗号分隔）")
    
    # 统计信息
    view_count = Column(Integer, default=0, comment="浏览量")
    discuss_count = Column(Integer, default=0, comment="讨论量")
    
    # 状态标记
    is_active = Column(Boolean, default=True, comment="是否有效")
    is_processed = Column(Boolean, default=False, comment="是否已处理（生成文章）")
    
    # 热度历史（JSON格式存储最近24小时的数据点）
    heat_history = Column(Text, nullable=True, comment="热度历史数据（JSON数组）")
    
    # 原始数据（JSON格式，存储API返回的完整数据）
    raw_data = Column(Text, nullable=True, comment="原始数据（JSON）")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 复合索引
    __table_args__ = (
        Index('ix_hotspots_source_created', 'source', 'created_at'),
        Index('ix_hotspots_category_heat', 'category', 'heat'),
    )

    def to_dict(self, include_history: bool = False):
        """转换为字典"""
        data = {
            "id": self.id,
            "rank": self.rank,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "category": self.category,
            "tags": self.get_tags_list(),
            "heat": self.heat,
            "heat_trend": self.heat_trend,
            "summary": self.summary,
            "keywords": self.get_keywords_list(),
            "view_count": self.view_count,
            "discuss_count": self.discuss_count,
            "is_active": self.is_active,
            "is_processed": self.is_processed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_history and self.heat_history:
            try:
                data["heat_history"] = json.loads(self.heat_history)
            except:
                data["heat_history"] = []
                
        return data
    
    def get_tags_list(self) -> list:
        """获取标签列表"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def set_tags_list(self, tags: list):
        """设置标签列表"""
        self.tags = ','.join(tags) if tags else None
    
    def get_keywords_list(self) -> list:
        """获取关键词列表"""
        if not self.keywords:
            return []
        return [kw.strip() for kw in self.keywords.split(',') if kw.strip()]
    
    def set_keywords_list(self, keywords: list):
        """设置关键词列表"""
        self.keywords = ','.join(keywords) if keywords else None
    
    def add_heat_point(self, heat_value: int):
        """添加热度数据点"""
        try:
            history = json.loads(self.heat_history) if self.heat_history else []
        except:
            history = []
        
        # 添加新数据点
        history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "heat": heat_value
        })
        
        # 只保留最近24小时的数据（每15分钟一个点，最多96个点）
        max_points = 96
        if len(history) > max_points:
            history = history[-max_points:]
        
        self.heat_history = json.dumps(history)
        
        # 计算趋势（最近1小时 vs 1小时前）
        if len(history) >= 8:  # 至少有8个点（2小时数据）
            recent = sum(h["heat"] for h in history[-4:]) / 4  # 最近1小时
            previous = sum(h["heat"] for h in history[-8:-4]) / 4  # 1小时前
            if previous > 0:
                self.heat_trend = ((recent - previous) / previous) * 100


class HotspotTrend(Base):
    """热点趋势统计 - 按小时聚合"""
    
    __tablename__ = "hotspot_trends"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False, index=True, comment="来源")
    hour = Column(DateTime, nullable=False, index=True, comment="统计小时")
    
    # 统计数据
    total_hotspots = Column(Integer, default=0, comment="热点总数")
    avg_heat = Column(Float, default=0.0, comment="平均热度")
    max_heat = Column(Integer, default=0, comment="最高热度")
    min_heat = Column(Integer, default=0, comment="最低热度")
    
    # 分类分布（JSON格式）
    category_distribution = Column(Text, nullable=True, comment="分类分布（JSON）")
    
    # 热门话题ID列表
    top_hotspot_ids = Column(Text, nullable=True, comment="TOP10话题ID列表（JSON）")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    __table_args__ = (
        Index('ix_trends_source_hour', 'source', 'hour', unique=True),
    )