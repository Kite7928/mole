"""
测试智谱 Cogview API 连接
"""
import asyncio
import httpx
import os

# 从 .env 文件加载配置
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env()

API_KEY = os.getenv('COGVIEW_API_KEY')
BASE_URL = os.getenv('COGVIEW_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4/images/generations')
MODEL = os.getenv('COGVIEW_MODEL', 'cogview-3-flash')

async def test_cogview():
    print("=" * 60)
    print("智谱 Cogview API 测试")
    print("=" * 60)
    
    print(f"\nAPI Key: {API_KEY[:20]}..." if API_KEY else "API Key: 未配置")
    print(f"模型: {MODEL}")
    print(f"URL: {BASE_URL}")
    
    if not API_KEY:
        print("\n❌ API Key 未配置")
        return
    
    # 测试请求
    url = BASE_URL
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "prompt": "A beautiful sunset over mountains",
        "size": "1024x1024",
        "n": 1
    }
    
    print("\n发送测试请求...")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")
    
    try:
        # 禁用SSL验证（仅用于测试）
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            print(f"\n状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ 请求成功!")
                print(f"响应: {data}")
            else:
                print(f"\n❌ 请求失败")
                print(f"响应内容: {response.text}")
                
    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP 错误: {e}")
        print(f"响应: {e.response.text}")
    except httpx.RequestError as e:
        print(f"\n❌ 请求错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cogview())
