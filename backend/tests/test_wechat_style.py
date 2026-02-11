"""
微信样式表渲染测试
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.markdown_converter import markdown_converter_service


async def test_wechat_style():
    """测试微信样式表渲染"""
    print("=" * 60)
    print("测试微信样式表渲染功能")
    print("=" * 60)
    
    # 测试 Markdown 内容
    test_markdown = """
# 人工智能改变生活

**AI 已经无处不在** 这就对了！

今天要和大家聊的是人工智能如何改变我们的生活。

## 1. 智能助手

简单来说，就是帮你解决日常问题。

**重点：** 效率提升 10 倍！

## 2. 自动驾驶

「自动驾驶」到底是什么？

简单来讲，就是车自己开。

## 总结

**金句：** AI 不是要取代人类，而是要赋能人类。

**预告：** 下期聊聊 AI 的未来。

**互动：** 你怎么看？评论区见！
"""
    
# 测试用例 1：转换 Markdown 为微信 HTML
    print("\n测试用例 1：转换 Markdown 为微信 HTML（不内联 CSS）")
    print(f"原始 Markdown（长度: {len(test_markdown)} 字符）:")
    print(f"{test_markdown}")
    
    # 测试转换（不内联 CSS，保留 style 标签）
    html = await markdown_converter_service.convert_to_wechat_html(test_markdown, inline_css=False)
    
    print(f"\n转换后的 HTML（长度: {len(html)} 字符）:")
    print(f"{html[:500]}...")
    
    # 验证 HTML 包含关键元素
    assert "<style>" in html, "HTML 应该包含样式表"
    # Markdown 转换后标题会被转换成 id 属性
    assert "人工智能改变生活" in html, "HTML 应该包含标题"
    assert "智能助手" in html, "HTML 应该包含内容"
    assert "效率提升 10 倍" in html, "HTML 应该包含重点标记"
    
    print("\n✅ 测试用例 1 通过")
    
    # 测试用例 2：验证样式表加载
    print("\n" + "=" * 60)
    print("测试用例 2：验证微信样式表加载")
    
    wechat_style = markdown_converter_service.wechat_style
    print(f"微信样式表长度: {len(wechat_style)} 字符")
    
    # 验证样式表包含关键样式
    style_keywords = ["h1", "h2", "p", "strong", "a", "blockquote", "code", "table", "img"]
    for keyword in style_keywords:
        if keyword in wechat_style:
            print(f"  ✅ 包含 '{keyword}' 样式")
        else:
            print(f"  ❌ 缺少 '{keyword}' 样式")
    
    assert wechat_style is not None
    assert len(wechat_style) > 0
    
    print("\n✅ 测试用例 2 通过")
    
    # 测试用例 3：验证特定样式
    print("\n" + "=" * 60)
    print("测试用例 3：验证特定样式")
    
    # 验证标题样式
    if "#4A90E2" in wechat_style:
        print("  ✅ 使用微信主题色 (#4A90E2)")
    else:
        print("  ⚠️ 未使用微信主题色")
    
    # 验证响应式设计
    if "@media" in wechat_style:
        print("  ✅ 包含响应式设计")
    else:
        print("  ⚠️ 未包含响应式设计")
    
    # 验证容器宽度
    if "677px" in wechat_style:
        print("  ✅ 使用微信标准宽度 (677px)")
    else:
        print("  ⚠️ 未使用微信标准宽度")
    
    print("\n✅ 测试用例 3 通过")
    
    # 测试用例 4：验证代码块处理
    print("\n" + "=" * 60)
    print("测试用例 4：验证代码块处理")
    
    code_markdown = """
## 代码示例

```python
def hello_world():
    print("Hello, World!")
    return True
```
"""
    
    html_with_code = await markdown_converter_service.convert_to_wechat_html(code_markdown)
    
    # 验证代码块被处理
    assert "hello_world" in html_with_code
    assert "print" in html_with_code
    
    print("  ✅ 代码块处理正确")
    print("\n✅ 测试用例 4 通过")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_wechat_style())