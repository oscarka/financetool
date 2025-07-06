#!/usr/bin/env python3
import asyncio
import httpx
import json

async def test_okx_instruments():
    """测试OKX 公共接口 /api/v5/public/instruments"""
    print("测试OKX 公共接口 /api/v5/public/instruments ...")
    url = "https://www.okx.com/api/v5/public/instruments?instType=SPOT"
    print(f"请求URL: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {response.headers}")
            print(f"响应内容: {response.text[:500]}...")
            if response.status_code == 200:
                data = response.json()
                print(f"解析后的数据: {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}...")
            else:
                print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    asyncio.run(test_okx_instruments()) 