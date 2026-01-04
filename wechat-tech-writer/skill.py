#!/usr/bin/env python3
"""
wechat-tech-writer - AI技术文章写作引擎
支持多轮智能搜索、内容改写、AI配图生成
"""

import os
import json
import re
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import requests
from google import genai


class ImageGenerator(ABC):
    """图片生成器抽象基类"""
    
    @abstractmethod
    def generate(self, prompt: str, output_path: str, **kwargs) -> str:
        """生成图片"""
        pass


class GeminiImageGenerator(ImageGenerator):
    """Gemini Imagen API图片生成器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def generate(self, prompt: str, output_path: str, **kwargs) -> str:
        """
        使用Gemini生成图片
        
        Args:
            prompt: 图片生成提示词
            output_path: 输出图片路径
            **kwargs: 其他参数
            
        Returns:
            生成的图片路径
        """
        # 创建客户端
        client = genai.Client(api_key=self.api_key)
        
        # 生成图片
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt],
        )
        
        # 保存图片
        # 注意：实际实现需要根据API返回的图片数据进行保存
        # 这里是简化版本
        return output_path


class OpenAIImageGenerator(ImageGenerator):
    """OpenAI DALL-E图片生成器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def generate(self, prompt: str, output_path: str, **kwargs) -> str:
        """
        使用DALL-E生成图片
        
        Args:
            prompt: 图片生成提示词
            output_path: 输出图片路径
            **kwargs: 其他参数
            
        Returns:
            生成的图片路径
        """
        import openai
        
        client = openai.OpenAI(api_key=self.api_key)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",  # 16:9 比例
            quality="standard",
            n=1,
        )
        
        # 保存图片
        image_url = response.data[0].url
        img_response = requests.get(image_url)
        with open(output_path, 'wb') as f:
            f.write(img_response.content)
        
        return output_path


class WeChatTechWriter:
    """微信公众号技术文章写作引擎"""
    
    def __init__(self, 
                 image_generator: Optional[ImageGenerator] = None,
                 output_dir: str = "./articles"):
        """
        初始化写作引擎
        
        Args:
            image_generator: 图片生成器实例
            output_dir: 文章输出目录
        """
        self.image_generator = image_generator
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def research_topic(self, topic: str) -> List[Dict]:
        """
        多轮智能搜索策略
        
        Args:
            topic: 研究主题
            
        Returns:
            搜索结果列表
        """
        # 第1轮：官方信息
        search_queries = [
            f"{topic} 官方文档",
            f"{topic} GitHub",
        ]
        
        # 第2轮：技术解析
        search_queries.extend([
            f"{topic} 详细介绍",
            f"{topic} 教程",
        ])
        
        # 第3轮：对比评测
        search_queries.extend([
            f"{topic} vs {topic} 竞品",
            f"{topic} 评测",
        ])
        
        # 第4轮：补充验证（根据前3轮结果动态调整）
        # 这里简化处理，实际应该根据前3轮结果分析缺失信息
        
        results = []
        for query in search_queries:
            # 这里应该调用搜索API
            # 简化版本，返回模拟数据
            results.append({
                "query": query,
                "title": f"{query} - 搜索结果",
                "url": f"https://example.com/{query}",
                "snippet": f"关于{query}的详细内容..."
            })
        
        return results
    
    def analyze_gaps(self, search_results: List[Dict]) -> str:
        """
        分析搜索结果中的信息缺口
        
        Args:
            search_results: 搜索结果列表
            
        Returns:
            缺失信息描述
        """
        # 简化版本，实际应该分析搜索结果
        return "需要补充的信息"
    
    def rewrite_content(self, topic: str, research_results: List[Dict]) -> str:
        """
        结构化改写内容
        
        Args:
            topic: 主题
            research_results: 研究结果
            
        Returns:
            改写后的文章内容
        """
        # 文章结构模板（2000-3000字）
        article_template = f"""
# {topic}

## 1. 引言
（这里应该由AI根据研究结果生成100-200字的引子）

## 2. 是什么
（这里应该由AI根据研究结果生成300-500字的基本介绍）

## 3. 能做什么
（这里应该由AI根据研究结果生成500-800字的核心功能特性和应用场景）

## 4. 如何使用
（这里应该由AI根据研究结果生成具体使用案例和代码示例）

## 5. 总结
（这里应该由AI根据研究结果生成总结）
"""
        
        # 注意：实际实现应该调用AI API进行内容生成
        # 这里返回模板，实际使用时需要替换为AI生成的内容
        return article_template
    
    def generate_article(self, topic: str, template: str = "default") -> Dict:
        """
        生成完整文章
        
        Args:
            topic: 文章主题
            template: 文章模板类型
            
        Returns:
            包含文章内容、图片路径等信息的字典
        """
        # 1. 多轮智能搜索
        research_results = self.research_topic(topic)
        
        # 2. 内容改写
        article_content = self.rewrite_content(topic, research_results)
        
        # 3. 生成配图
        images = []
        if self.image_generator:
            # 根据文章类型选择配色和图片策略
            article_type = self._detect_article_type(topic)
            
            if article_type == "tech":
                # AI/科技类：蓝紫渐变，1封面 + 1性能对比图
                cover_prompt = self._create_cover_prompt(topic, article_type)
                cover_path = os.path.join(self.output_dir, f"{topic}_cover.png")
                self.image_generator.generate(cover_prompt, cover_path)
                images.append({"type": "cover", "path": cover_path})
            elif article_type == "tool":
                # 工具类：绿橙渐变，1封面 + 1架构图
                cover_prompt = self._create_cover_prompt(topic, article_type)
                cover_path = os.path.join(self.output_dir, f"{topic}_cover.png")
                self.image_generator.generate(cover_prompt, cover_path)
                images.append({"type": "cover", "path": cover_path})
            else:
                # 新闻类：粉紫渐变，仅1封面
                cover_prompt = self._create_cover_prompt(topic, article_type)
                cover_path = os.path.join(self.output_dir, f"{topic}_cover.png")
                self.image_generator.generate(cover_prompt, cover_path)
                images.append({"type": "cover", "path": cover_path})
        
        # 4. 保存文章
        article_path = os.path.join(self.output_dir, f"{topic}.md")
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(article_content)
        
        return {
            "topic": topic,
            "content": article_content,
            "article_path": article_path,
            "images": images,
            "research_results": research_results
        }
    
    def _detect_article_type(self, topic: str) -> str:
        """
        检测文章类型
        
        Args:
            topic: 文章主题
            
        Returns:
            文章类型：tech/tool/news
        """
        # 简化版本，实际应该使用更智能的检测逻辑
        tech_keywords = ["AI", "人工智能", "机器学习", "深度学习", "模型", "算法"]
        tool_keywords = ["工具", "软件", "平台", "框架", "库"]
        
        for keyword in tech_keywords:
            if keyword in topic:
                return "tech"
        
        for keyword in tool_keywords:
            if keyword in topic:
                return "tool"
        
        return "news"
    
    def _create_cover_prompt(self, topic: str, article_type: str) -> str:
        """
        创建封面图生成提示词
        
        Args:
            topic: 文章主题
            article_type: 文章类型
            
        Returns:
            图片生成提示词
        """
        color_schemes = {
            "tech": "蓝紫渐变 (#1a1f5c → #7c3aed)",
            "tool": "绿橙渐变 (#10b981 → #f97316)",
            "news": "粉紫渐变 (#ec4899 → #a855f7)"
        }
        
        prompt = f"""
Generate a professional magazine-style cover image for an article about "{topic}".
Style: Modern, clean, professional technology magazine cover
Color scheme: {color_schemes.get(article_type, "blue gradient")}
Aspect ratio: 16:9 (landscape)
Text: Use simplified Chinese for any text elements
Note: Keep text minimal (≤15 characters) and use English title with Chinese subtitle if needed
"""
        
        return prompt


def main():
    """主函数 - 演示用法"""
    # 初始化图片生成器（需要API密钥）
    # image_generator = GeminiImageGenerator(api_key="your-gemini-api-key")
    # 或
    # image_generator = OpenAIImageGenerator(api_key="your-openai-api-key")
    
    # 初始化写作引擎
    writer = WeChatTechWriter(
        image_generator=None,  # 暂时不使用图片生成
        output_dir="./articles"
    )
    
    # 生成文章
    result = writer.generate_article("Claude Sonnet 4")
    
    print(f"文章已生成：{result['article_path']}")
    print(f"文章字数：{len(result['content'])} 字")
    print(f"配图数量：{len(result['images'])}")


if __name__ == "__main__":
    main()