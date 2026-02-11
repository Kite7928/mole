"""
测试图片生成功能
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.core.config import settings
from app.services.image_generation_service import image_generation_service

async def test_image_generation():
    """测试图片生成"""
    print("=" * 60)
    print("图片生成测试")
    print("=" * 60)
    
    # 检查配置
    print("\n1. 检查 API Key 配置:")
    print(f"   COGVIEW_API_KEY: {'已配置' if settings.COGVIEW_API_KEY else '未配置'}")
    print(f"   ZHIPU_API_KEY: {'已配置' if settings.ZHIPU_API_KEY else '未配置'}")
    print(f"   COGVIEW_MODEL: {settings.COGVIEW_MODEL}")
    
    # 测试生成封面图
    print("\n2. 测试生成封面图:")
    topic = "人工智能与未来科技"
    print(f"   主题: {topic}")
    print(f"   提供商: cogview")
    print(f"   风格: professional")
    
    try:
        result = await image_generation_service.generate_article_cover(
            topic=topic,
            style="professional",
            provider="cogview"
        )
        
        if result and result.get("url"):
            print(f"\n   ✅ 生成成功!")
            print(f"   图片路径: {result['url']}")
            print(f"   提供商: {result.get('provider', 'unknown')}")
        else:
            print(f"\n   ❌ 生成失败，返回结果: {result}")
            
    except Exception as e:
        print(f"\n   ❌ 生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    
    # 关闭客户端
    await image_generation_service.close()

if __name__ == "__main__":
    asyncio.run(test_image_generation())
