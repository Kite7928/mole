"""
写作风格功能测试
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.tech_fast_food import (
    get_writing_style_prompt,
    get_writing_template,
    apply_writing_style,
    get_writing_example
)


async def test_writing_style():
    """测试写作风格功能"""
    print("=" * 60)
    print("测试写作风格功能")
    print("=" * 60)
    
    # 测试用例 1：获取写作风格 Prompt
    print("\n测试用例 1：获取写作风格 Prompt")
    
    prompt = get_writing_style_prompt()
    print(f"写作风格 Prompt 长度: {len(prompt)} 字符")
    print(f"包含关键词检查:")
    
    keywords = ["科技速食", "开篇风格", "段落节奏", "重点突出", "结尾三件套"]
    for keyword in keywords:
        if keyword in prompt:
            print(f"  ✅ 包含 '{keyword}'")
        else:
            print(f"  ❌ 缺少 '{keyword}'")
    
    assert "科技速食" in prompt
    assert "开篇风格" in prompt
    assert "段落节奏" in prompt
    assert "重点突出" in prompt
    assert "结尾三件套" in prompt
    
    print("✅ 测试用例 1 通过")
    
    # 测试用例 2：获取写作模板
    print("\n" + "=" * 60)
    print("测试用例 2：获取写作模板")
    
    templates = ["opening", "transition", "emphasis", "summary", "interaction"]
    for template_type in templates:
        template = get_writing_template(template_type)
        print(f"\n{template_type} 模板:")
        print(f"  {template}")
    
    print("\n✅ 测试用例 2 通过")
    
    # 测试用例 3：应用写作风格（段落分割）
    print("\n" + "=" * 60)
    print("测试用例 3：应用写作风格（段落分割）")
    
    long_paragraph = """这是一个很长的段落，包含了太多的内容，应该被分割成更短的段落以提高可读性。这个段落有多个句子，每个句子都应该独立成段，这样读者阅读起来会更加轻松。同时，我们也需要确保每个段落的长度控制在合理范围内，不要超过100个字。"""
    
    print(f"原始段落（长度: {len(long_paragraph)} 字）:")
    print(f"  {long_paragraph}")
    
    styled_content = apply_writing_style(long_paragraph)
    print(f"\n应用写作风格后:")
    print(f"  {styled_content}")
    
    # 验证段落被分割
    styled_paragraphs = styled_content.split('\n\n')
    assert len(styled_paragraphs) > 1
    
    # 验证每个段落长度
    for para in styled_paragraphs:
        assert len(para) <= 100, f"段落过长: {len(para)} 字"
    
    print(f"\n段落数量: {len(styled_paragraphs)}")
    print("✅ 测试用例 3 通过")
    
    # 测试用例 4：获取写作示例
    print("\n" + "=" * 60)
    print("测试用例 4：获取写作示例")
    
    ai_example = get_writing_example("ai")
    blockchain_example = get_writing_example("blockchain")
    
    if ai_example:
        print("\nAI 写作示例（前 200 字）:")
        print(f"  {ai_example[:200]}...")
        assert "金句" in ai_example or "**" in ai_example
    
    if blockchain_example:
        print("\n区块链写作示例（前 200 字）:")
        print(f"  {blockchain_example[:200]}...")
        assert "金句" in blockchain_example or "**" in blockchain_example
    
    print("✅ 测试用例 4 通过")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_writing_style())