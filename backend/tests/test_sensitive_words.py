"""
敏感词审查功能测试
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.sensitive_words import (
    filter_sensitive_words,
    check_sensitive_words,
    get_replacement,
    get_all_sensitive_words
)


async def test_sensitive_words():
    """测试敏感词过滤功能"""
    print("=" * 60)
    print("测试敏感词审查功能")
    print("=" * 60)
    
    # 测试用例 1：包含多个敏感词的文章
    test_content_1 = """
    这篇文章讲述如何通过自动化股票赚钱的方式，使用ChatGPT和DeepSeek等AI工具，
    在微信和抖音上推广，最终实现暴富的目标。你需要翻墙访问一些资源，
    但要注意不要使用盗版软件。
    """
    
    print("\n测试用例 1：包含多个敏感词的文章")
    print(f"原始内容:\n{test_content_1}")
    
    filtered_1 = filter_sensitive_words(test_content_1)
    print(f"\n过滤后内容:\n{filtered_1}")
    
    found_1 = check_sensitive_words(test_content_1)
    print(f"\n检测到的敏感词: {found_1}")
    
    # 验证替换是否正确
    assert "自动化" not in filtered_1
    assert "智能联动" in filtered_1
    assert "股票" not in filtered_1
    assert "权益资产" in filtered_1
    assert "赚钱" not in filtered_1
    assert "获取收益" in filtered_1
    
    print("✅ 测试用例 1 通过")
    
    # 测试用例 2：不包含敏感词的文章
    test_content_2 = """
    这是一个关于科技发展的科普文章，介绍了新技术在医疗、教育、
    交通等领域的应用，以及未来的发展趋势。
    """
    
    print("\n" + "=" * 60)
    print("测试用例 2：不包含敏感词的文章")
    print(f"原始内容:\n{test_content_2}")
    
    filtered_2 = filter_sensitive_words(test_content_2)
    print(f"\n过滤后内容:\n{filtered_2}")
    
    found_2 = check_sensitive_words(test_content_2)
    print(f"\n检测到的敏感词: {found_2 if found_2 else '无'}")
    
    # 验证内容未被修改
    assert filtered_2 == test_content_2
    assert len(found_2) == 0
    
    print("✅ 测试用例 2 通过")
    
    # 测试用例 3：获取所有敏感词映射
    print("\n" + "=" * 60)
    print("测试用例 3：获取所有敏感词映射")
    
    all_words = get_all_sensitive_words()
    print(f"敏感词总数: {len(all_words)}")
    print("\n敏感词映射表（前10个）:")
    for i, (word, replacement) in enumerate(list(all_words.items())[:10]):
        print(f"  {i+1}. {word} -> {replacement}")
    
    print("✅ 测试用例 3 通过")
    
    # 测试用例 4：测试单个敏感词替换
    print("\n" + "=" * 60)
    print("测试用例 4：测试单个敏感词替换")
    
    test_word = "股票"
    replacement = get_replacement(test_word)
    print(f"敏感词: {test_word}")
    print(f"替换词: {replacement}")
    
    assert replacement == "权益资产"
    
    print("✅ 测试用例 4 通过")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_sensitive_words())
