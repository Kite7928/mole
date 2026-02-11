"""
检查配置是否正确加载
"""
import sys
sys.path.insert(0, '.')

from app.core.config import settings

print("=" * 60)
print("配置检查")
print("=" * 60)

print("\n1. 智谱 AI 配置:")
print(f"   ZHIPU_API_KEY: {'已配置' if settings.ZHIPU_API_KEY else '未配置'}")
if settings.ZHIPU_API_KEY:
    print(f"   Key 前10位: {settings.ZHIPU_API_KEY[:10]}...")
print(f"   ZHIPU_MODEL: {settings.ZHIPU_MODEL}")

print("\n2. 图片生成配置:")
print(f"   COGVIEW_API_KEY: {'已配置' if settings.COGVIEW_API_KEY else '未配置'}")
if settings.COGVIEW_API_KEY:
    print(f"   Key 前10位: {settings.COGVIEW_API_KEY[:10]}...")
print(f"   COGVIEW_MODEL: {settings.COGVIEW_MODEL}")
print(f"   COGVIEW_BASE_URL: {settings.COGVIEW_BASE_URL}")

print("\n3. 其他图片提供商:")
print(f"   DALL_E_API_KEY: {'已配置' if settings.DALL_E_API_KEY else '未配置'}")
print(f"   GEMINI_API_KEY: {'已配置' if settings.GEMINI_API_KEY else '未配置'}")

print("\n" + "=" * 60)

# 测试 API 连接
if settings.COGVIEW_API_KEY:
    print("\n4. 测试智谱 API 连接...")
    import httpx
    import asyncio
    
    async def test_api():
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    settings.COGVIEW_BASE_URL,
                    headers={"Authorization": f"Bearer {settings.COGVIEW_API_KEY}"},
                    json={
                        "model": settings.COGVIEW_MODEL,
                        "prompt": "test",
                        "size": "1024x1024"
                    }
                )
                print(f"   状态码: {response.status_code}")
                if response.status_code == 401:
                    print("   ❌ 401 Unauthorized - API Key 无效或已过期")
                elif response.status_code == 200:
                    print("   ✅ 连接成功")
                else:
                    print(f"   响应: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ 连接失败: {e}")
    
    asyncio.run(test_api())

print("\n" + "=" * 60)
