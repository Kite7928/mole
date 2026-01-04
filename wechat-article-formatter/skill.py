#!/usr/bin/env python3
"""
wechat-article-formatter - HTML格式化美化工具
支持CSS内联化、三套主题、微信代码块兼容转换
"""

import os
import re
import json
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
import markdown
from bs4 import BeautifulSoup
import cssutils


class WeChatHTMLConverter:
    """微信公众号HTML转换器"""
    
    # CSS主题定义
    THEMES = {
        "tech": """
/* Tech主题 - 科技风 */
:root {
    --primary-color: #007aff;
    --secondary-color: #5856d6;
    --accent-color: #ff9500;
    --bg-color: #ffffff;
    --text-color: #333333;
    --heading-color: #1a1a1a;
    --code-bg: #f5f5f7;
    --border-color: #e5e5e5;
}

h1, h2, h3 {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: bold;
}

h1 { font-size: 24px; margin: 30px 0 20px; }
h2 { font-size: 20px; margin: 25px 0 15px; }
h3 { font-size: 18px; margin: 20px 0 10px; }

p { line-height: 1.8; margin: 15px 0; color: var(--text-color); }

code {
    background-color: var(--code-bg);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    color: var(--primary-color);
}

pre {
    background-color: var(--code-bg);
    padding: 15px;
    border-radius: 8px;
    overflow-x: auto;
    border-left: 4px solid var(--primary-color);
}

blockquote {
    border-left: 4px solid var(--accent-color);
    padding-left: 15px;
    margin: 20px 0;
    color: #666;
    background-color: #fff9f0;
    padding: 15px;
    border-radius: 0 8px 8px 0;
}
""",
        "minimal": """
/* Minimal主题 - 简约风 */
:root {
    --primary-color: #000000;
    --secondary-color: #333333;
    --accent-color: #666666;
    --bg-color: #ffffff;
    --text-color: #1a1a1a;
    --heading-color: #000000;
    --code-bg: #f8f8f8;
    --border-color: #e0e0e0;
}

h1, h2, h3 {
    color: var(--heading-color);
    font-weight: 600;
    letter-spacing: -0.5px;
}

h1 { font-size: 26px; margin: 40px 0 25px; border-bottom: 2px solid #000; padding-bottom: 10px; }
h2 { font-size: 22px; margin: 30px 0 20px; }
h3 { font-size: 18px; margin: 25px 0 15px; }

p { line-height: 2; margin: 20px 0; color: var(--text-color); }

code {
    background-color: var(--code-bg);
    padding: 3px 8px;
    border-radius: 3px;
    font-family: 'SF Mono', 'Monaco', monospace;
    color: var(--primary-color);
}

pre {
    background-color: var(--code-bg);
    padding: 20px;
    border-radius: 6px;
    overflow-x: auto;
    border: 1px solid var(--border-color);
}

blockquote {
    border-left: 3px solid var(--primary-color);
    padding-left: 20px;
    margin: 25px 0;
    color: var(--accent-color);
    font-style: italic;
}
""",
        "business": """
/* Business主题 - 商务风 */
:root {
    --primary-color: #1e40af;
    --secondary-color: #1e3a8a;
    --accent-color: #dc2626;
    --bg-color: #ffffff;
    --text-color: #374151;
    --heading-color: #111827;
    --code-bg: #f3f4f6;
    --border-color: #d1d5db;
}

h1, h2, h3 {
    color: var(--heading-color);
    font-weight: 700;
}

h1 { 
    font-size: 24px; 
    margin: 30px 0 20px; 
    background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
h2 { font-size: 20px; margin: 25px 0 15px; color: var(--primary-color); }
h3 { font-size: 18px; margin: 20px 0 10px; }

p { line-height: 1.75; margin: 15px 0; color: var(--text-color); }

code {
    background-color: var(--code-bg);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Consolas', monospace;
    color: var(--accent-color);
}

pre {
    background-color: var(--code-bg);
    padding: 15px;
    border-radius: 6px;
    overflow-x: auto;
    border: 1px solid var(--border-color);
    border-left: 4px solid var(--primary-color);
}

blockquote {
    border-left: 4px solid var(--primary-color);
    padding-left: 15px;
    margin: 20px 0;
    color: #4b5563;
    background-color: #eff6ff;
    padding: 15px;
    border-radius: 0 6px 6px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}

th, td {
    border: 1px solid var(--border-color);
    padding: 12px;
    text-align: left;
}

th {
    background-color: var(--primary-color);
    color: white;
    font-weight: 600;
}
"""
    }
    
    def __init__(self, theme: str = "tech"):
        """
        初始化转换器
        
        Args:
            theme: 主题名称 (tech/minimal/business)
        """
        if theme not in self.THEMES:
            raise ValueError(f"不支持的主题: {theme}，可选: {list(self.THEMES.keys())}")
        
        self.theme = theme
        self.theme_css = self.THEMES[theme]
        self.css_vars = self._parse_css_vars()
        self.css_rules = self._parse_css_to_dict()
    
    def _parse_css_vars(self) -> Dict[str, str]:
        """解析CSS变量"""
        css_vars = {}
        var_pattern = r'--([a-zA-Z0-9-]+):\s*([^;]+);'
        
        for match in re.finditer(var_pattern, self.theme_css):
            var_name = f'--{match.group(1)}'
            var_value = match.group(2).strip()
            css_vars[var_name] = var_value
        
        return css_vars
    
    def _parse_css_to_dict(self) -> Dict[str, Dict[str, str]]:
        """解析CSS为字典格式，用于内联样式"""
        css_rules = {}
        
        try:
            sheet = cssutils.parseString(self.theme_css)
            
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    selectors = rule.selectorText
                    style_dict = {}
                    
                    for prop in rule.style:
                        prop_value = prop.value
                        # 替换CSS变量为实际值
                        if 'var(' in prop_value:
                            prop_value = self._replace_css_vars(prop_value)
                        
                        style_dict[prop.name] = prop_value
                    
                    css_rules[selectors] = style_dict
        except Exception as e:
            print(f"解析CSS时出错: {e}")
        
        return css_rules
    
    def _replace_css_vars(self, value: str) -> str:
        """替换CSS变量为实际值"""
        var_pattern = r'var\(--([a-zA-Z0-9-]+)\)'
        
        def replace_var(match):
            var_name = f'--{match.group(1)}'
            if var_name in self.css_vars:
                return self.css_vars[var_name]
            return match.group(0)
        
        return re.sub(var_pattern, replace_var, value)
    
    def _apply_inline_styles(self, soup: BeautifulSoup) -> BeautifulSoup:
        """应用内联样式到HTML元素"""
        for selectors, styles in self.css_rules.items():
            # 简化选择器匹配（实际应该使用更完整的CSS选择器解析）
            elements = soup.select(selectors)
            
            for element in elements:
                existing_style = element.get('style', '')
                new_styles = []
                
                for prop, value in styles.items():
                    new_styles.append(f"{prop}: {value}")
                
                if existing_style:
                    element['style'] = f"{existing_style}; {'; '.join(new_styles)}"
                else:
                    element['style'] = '; '.join(new_styles)
        
        return soup
    
    def _convert_code_blocks(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        转换代码块为微信兼容格式
        微信不支持<pre><code>标签，必须转换为<div> + <br> + &nbsp;
        """
        # 查找所有<pre>标签
        for pre in soup.find_all('pre'):
            # 获取代码内容
            code_content = pre.get_text()
            
            # 创建新的div容器
            new_div = soup.new_tag('div')
            
            # 获取原有样式
            pre_style = pre.get('style', '')
            if pre_style:
                new_div['style'] = pre_style
            
            # 分割代码行
            lines = code_content.split('\n')
            
            # 转换每一行
            for line in lines:
                # 替换空格为&nbsp;
                line_html = line.replace(' ', '&nbsp;')
                
                # 创建行div
                line_div = soup.new_tag('div')
                line_div.string = line_html
                
                new_div.append(line_div)
            
            # 替换原来的<pre>标签
            pre.replace_with(new_div)
        
        # 处理行内代码<code>
        for code in soup.find_all('code'):
            # 获取代码内容
            code_content = code.get_text()
            
            # 替换空格为&nbsp;
            code_content = code_content.replace(' ', '&nbsp;')
            
            # 创建新的span标签
            new_span = soup.new_tag('span')
            new_span.string = code_content
            
            # 复制样式
            code_style = code.get('style', '')
            if code_style:
                new_span['style'] = code_style
            
            code.replace_with(new_span)
        
        return soup
    
    def markdown_to_html(self, markdown_text: str) -> str:
        """
        将Markdown转换为HTML（带内联样式）
        
        Args:
            markdown_text: Markdown文本
            
        Returns:
            HTML字符串
        """
        # 1. Markdown转HTML
        html = markdown.markdown(
            markdown_text,
            extensions=['extra', 'codehilite', 'tables', 'fenced_code']
        )
        
        # 2. 解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # 3. 应用内联样式
        soup = self._apply_inline_styles(soup)
        
        # 4. 转换代码块为微信兼容格式
        soup = self._convert_code_blocks(soup)
        
        # 5. 返回HTML字符串
        return str(soup)
    
    def format_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        格式化Markdown文件
        
        Args:
            input_path: 输入Markdown文件路径
            output_path: 输出HTML文件路径（可选）
            
        Returns:
            HTML字符串
        """
        # 读取Markdown文件
        with open(input_path, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
        
        # 转换为HTML
        html = self.markdown_to_html(markdown_text)
        
        # 保存HTML文件
        if output_path is None:
            output_path = os.path.splitext(input_path)[0] + '.html'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return html


class WeChatArticleFormatter:
    """微信公众号文章格式化器"""
    
    def __init__(self, default_theme: str = "tech"):
        """
        初始化格式化器
        
        Args:
            default_theme: 默认主题
        """
        self.default_theme = default_theme
    
    def detect_theme(self, content: str) -> str:
        """
        自动检测适合的主题
        
        Args:
            content: 文章内容
            
        Returns:
            主题名称
        """
        # 检测技术关键词
        tech_keywords = ["代码", "编程", "算法", "API", "框架", "库", "技术", "开发"]
        # 检测商务关键词
        business_keywords = ["报告", "分析", "数据", "市场", "商业", "业务", "策略"]
        
        tech_count = sum(1 for keyword in tech_keywords if keyword in content)
        business_count = sum(1 for keyword in business_keywords if keyword in content)
        
        if tech_count > business_count:
            return "tech"
        elif business_count > tech_count:
            return "business"
        else:
            return "minimal"
    
    def format_article(self, input_path: str, 
                      theme: Optional[str] = None,
                      output_path: Optional[str] = None) -> str:
        """
        格式化文章
        
        Args:
            input_path: 输入文件路径
            theme: 主题（可选，不指定则自动检测）
            output_path: 输出文件路径（可选）
            
        Returns:
            HTML字符串
        """
        # 读取文件内容
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检测主题
        if theme is None:
            theme = self.detect_theme(content)
        
        # 创建转换器
        converter = WeChatHTMLConverter(theme=theme)
        
        # 格式化文件
        html = converter.format_file(input_path, output_path)
        
        print(f"文章已格式化，使用主题: {theme}")
        print(f"输出文件: {output_path or os.path.splitext(input_path)[0] + '.html'}")
        
        return html


def main():
    """主函数 - 演示用法"""
    # 初始化格式化器
    formatter = WeChatArticleFormatter(default_theme="tech")
    
    # 格式化文章
    input_file = "./articles/Claude_Sonnet_4.md"
    if os.path.exists(input_file):
        formatter.format_article(input_file)
    else:
        print(f"文件不存在: {input_file}")
        print("请先生成文章")


if __name__ == "__main__":
    main()