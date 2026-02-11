from typing import Optional, Dict, Any
import markdown
from bs4 import BeautifulSoup
import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from ..core.logger import logger
import os


class MarkdownConverterService:
    """
    Markdown to HTML converter for WeChat official account.
    """

    def __init__(self):
        # Custom CSS styles for WeChat
        self.default_style = """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                font-size: 16px;
                line-height: 1.8;
                color: #333;
                max-width: 677px;
                margin: 0 auto;
                padding: 20px;
            }
            
            h1, h2, h3, h4, h5, h6 {
                margin-top: 1.5em;
                margin-bottom: 0.5em;
                font-weight: 600;
                line-height: 1.4;
            }
            
            h1 { font-size: 2em; border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
            h2 { font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
            h3 { font-size: 1.25em; }
            h4 { font-size: 1.1em; }
            
            p { margin-bottom: 1em; }
            
            a { color: #576b95; text-decoration: none; }
            a:hover { text-decoration: underline; }
            
            blockquote {
                margin: 1em 0;
                padding: 0.5em 1em;
                border-left: 4px solid #576b95;
                background-color: #f7f7f7;
                color: #666;
            }
            
            code {
                font-family: "Consolas", "Monaco", "Courier New", monospace;
                background-color: #f5f5f5;
                padding: 2px 4px;
                border-radius: 3px;
                font-size: 0.9em;
            }
            
            pre {
                background-color: #f5f5f5;
                padding: 1em;
                border-radius: 5px;
                overflow-x: auto;
                margin: 1em 0;
            }
            
            pre code {
                background-color: transparent;
                padding: 0;
                border-radius: 0;
            }
            
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }
            
            table th, table td {
                border: 1px solid #ddd;
                padding: 8px 12px;
                text-align: left;
            }
            
            table th {
                background-color: #f5f5f5;
                font-weight: 600;
            }
            
            img {
                max-width: 100%;
                height: auto;
                display: block;
                margin: 1em auto;
            }
            
            ul, ol {
                padding-left: 2em;
                margin-bottom: 1em;
            }
            
            li { margin-bottom: 0.5em; }
            
            hr {
                border: none;
                border-top: 1px solid #eee;
                margin: 2em 0;
            }
            
            strong { font-weight: 600; }
            em { font-style: italic; }
        </style>
        """
        
        # 微信样式表路径
        self.wechat_style_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'templates',
            'wechat_style.css'
        )
        
        # 加载微信样式表
        self.wechat_style = self._load_wechat_style()
        logger.info(f"微信样式表加载完成，路径: {self.wechat_style_path}")

    def _load_wechat_style(self) -> str:
        """加载微信样式表"""
        try:
            if os.path.exists(self.wechat_style_path):
                with open(self.wechat_style_path, 'r', encoding='utf-8') as f:
                    style_content = f.read()
                # 包装在 style 标签中
                return f'<style>\n{style_content}\n</style>'
            else:
                logger.warning(f"微信样式表文件不存在: {self.wechat_style_path}，使用默认样式")
                return self.default_style
        except Exception as e:
            logger.error(f"加载微信样式表失败: {str(e)}，使用默认样式")
            return self.default_style

    async def convert_to_html(
        self,
        markdown_text: str,
        style: Optional[str] = None,
        inline_css: bool = True,
        use_wechat_style: bool = False
    ) -> str:
        """
        Convert Markdown to HTML for WeChat.

        Args:
            markdown_text: Markdown text to convert
            style: Custom CSS style (optional)
            inline_css: Whether to inline CSS styles
            use_wechat_style: Whether to use WeChat official style

        Returns:
            HTML string
        """
        try:
            # 如果使用微信样式，替换默认样式
            if use_wechat_style:
                style = self.wechat_style
            
            # Convert Markdown to HTML
            html = markdown.markdown(
                markdown_text,
                extensions=[
                    'tables',
                    'fenced_code',
                    'codehilite',
                    'nl2br',
                    'sane_lists',
                    'toc',
                    'attr_list'
                ]
            )

            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')

            # Process code blocks
            soup = self._process_code_blocks(soup)

            # Process images
            soup = self._process_images(soup)

            # Process links
            soup = self._process_links(soup)

            # Inline CSS if requested
            if inline_css:
                soup = self._inline_css(soup, style or self.default_style)

            # Add style tag
            if style and not inline_css:
                style_tag = soup.new_tag('style')
                style_tag.string = style
                soup.insert(0, style_tag)

            result = str(soup)
            
            if use_wechat_style:
                logger.info("Markdown converted to HTML with WeChat style successfully")
            else:
                logger.info("Markdown converted to HTML successfully")
                
            return result

        except Exception as e:
            logger.error(f"Error converting Markdown to HTML: {str(e)}")
            raise

    def _process_code_blocks(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Process code blocks for WeChat compatibility."""
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if code:
                # Get code language
                language = None
                if code.get('class'):
                    classes = code.get('class', [])
                    for cls in classes:
                        if cls.startswith('language-'):
                            language = cls.replace('language-', '')
                            break

                # Get code text
                code_text = code.get_text()

                # Remove existing code tag
                code.decompose()

                # Add line numbers
                lines = code_text.split('\n')
                numbered_lines = []
                for i, line in enumerate(lines, 1):
                    numbered_lines.append(f'<div style="display:flex;"><span style="color:#999;min-width:2em;margin-right:1em;">{i}.</span><span>{line}</span></div>')

                # Create new code block
                new_code = soup.new_tag('div')
                new_code['style'] = 'background-color:#f5f5f5;padding:1em;border-radius:5px;font-family:Consolas,Monaco,Courier New,monospace;font-size:14px;overflow-x:auto;'
                new_code.append(''.join(numbered_lines))

                pre.replace_with(new_code)

        return soup

    def _process_images(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Process images for WeChat compatibility."""
        for img in soup.find_all('img'):
            # Add alt text if missing
            if not img.get('alt'):
                img['alt'] = '图片'

            # Ensure src is present
            if not img.get('src'):
                img.decompose()

            # Add style for responsive images
            img['style'] = 'max-width:100%;height:auto;display:block;margin:1em auto;'

        return soup

    def _process_links(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Process links for WeChat compatibility."""
        for a in soup.find_all('a'):
            # Add target="_blank" for external links
            href = a.get('href', '')
            if href.startswith('http'):
                a['target'] = '_blank'
                a['rel'] = 'noopener noreferrer'

            # Add style
            a['style'] = 'color:#576b95;text-decoration:none;'

        return soup

    def _inline_css(self, soup: BeautifulSoup, css: str) -> BeautifulSoup:
        """Inline CSS styles into HTML elements."""
        try:
            from lxml import etree
            from premailer import Premailer

            # Convert to string
            html_str = str(soup)

            # Inline CSS
            premailer = Premailer(
                html_str,
                base_url='',
                remove_classes=False,
                keep_style_tags=False
            )

            inlined_html = premailer.transform()

            # Parse back to BeautifulSoup
            return BeautifulSoup(inlined_html, 'html.parser')

        except Exception as e:
            logger.warning(f"Failed to inline CSS: {str(e)}, returning original HTML")
            return soup

    async def generate_custom_style(
        self,
        theme: str = "default"
    ) -> str:
        """
        Generate custom CSS style based on theme.

        Args:
            theme: Theme name (default, blue, green, purple, dark)

        Returns:
            CSS string
        """
        themes = {
            "default": {
                "primary": "#576b95",
                "background": "#ffffff",
                "text": "#333333",
                "border": "#eeeeee"
            },
            "blue": {
                "primary": "#1890ff",
                "background": "#f0f9ff",
                "text": "#1a1a2e",
                "border": "#bae7ff"
            },
            "green": {
                "primary": "#52c41a",
                "background": "#f6ffed",
                "text": "#1a1a2e",
                "border": "#b7eb8f"
            },
            "purple": {
                "primary": "#722ed1",
                "background": "#f9f0ff",
                "text": "#1a1a2e",
                "border": "#d3adf7"
            },
            "dark": {
                "primary": "#177ddc",
                "background": "#1a1a2e",
                "text": "#ffffff",
                "border": "#303030"
            }
        }

        colors = themes.get(theme, themes["default"])

        custom_style = f"""
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                font-size: 16px;
                line-height: 1.8;
                color: {colors['text']};
                max-width: 677px;
                margin: 0 auto;
                padding: 20px;
                background-color: {colors['background']};
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                margin-top: 1.5em;
                margin-bottom: 0.5em;
                font-weight: 600;
                line-height: 1.4;
                color: {colors['text']};
            }}
            
            h1 {{ font-size: 2em; border-bottom: 2px solid {colors['border']}; padding-bottom: 0.3em; }}
            h2 {{ font-size: 1.5em; border-bottom: 1px solid {colors['border']}; padding-bottom: 0.3em; }}
            h3 {{ font-size: 1.25em; }}
            h4 {{ font-size: 1.1em; }}
            
            p {{ margin-bottom: 1em; }}
            
            a {{ color: {colors['primary']}; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            
            blockquote {{
                margin: 1em 0;
                padding: 0.5em 1em;
                border-left: 4px solid {colors['primary']};
                background-color: {colors['border']}33;
                color: {colors['text']};
            }}
            
            code {{
                font-family: "Consolas", "Monaco", "Courier New", monospace;
                background-color: {colors['border']};
                padding: 2px 4px;
                border-radius: 3px;
                font-size: 0.9em;
            }}
            
            pre {{
                background-color: {colors['border']};
                padding: 1em;
                border-radius: 5px;
                overflow-x: auto;
                margin: 1em 0;
            }}
            
            img {{
                max-width: 100%;
                height: auto;
                display: block;
                margin: 1em auto;
            }}
            
            strong {{ font-weight: 600; }}
            em {{ font-style: italic; }}
        </style>
        """

        return custom_style

    async def convert_with_custom_theme(
        self,
        markdown_text: str,
        theme: str = "default"
    ) -> str:
        """
        Convert Markdown to HTML with custom theme.

        Args:
            markdown_text: Markdown text to convert
            theme: Theme name

        Returns:
            HTML string with custom theme
        """
        # Generate custom style
        style = await self.generate_custom_style(theme)

        # Convert Markdown
        html = await self.convert_to_html(markdown_text, style=style, inline_css=False)

        return html

    async def convert_to_wechat_html(
        self,
        markdown_text: str,
        inline_css: bool = True
    ) -> str:
        """
        Convert Markdown to WeChat-compatible HTML with official style.

        Args:
            markdown_text: Markdown text to convert
            inline_css: Whether to inline CSS styles

        Returns:
            HTML string with WeChat style
        """
        try:
            # Convert with WeChat style
            html = await self.convert_to_html(
                markdown_text,
                inline_css=inline_css,
                use_wechat_style=True
            )
            
            logger.info("Markdown converted to WeChat HTML successfully")
            return html
            
        except Exception as e:
            logger.error(f"Error converting to WeChat HTML: {str(e)}")
            raise


# Global instance
markdown_converter_service = MarkdownConverterService()

# 别名，用于向后兼容
markdown_converter = markdown_converter_service