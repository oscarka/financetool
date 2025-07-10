#!/usr/bin/env python3
"""
API配置测试脚本
测试天天基金网和雪球API的连接和配置
"""

import asyncio
import httpx
import json
from datetime import date
from decimal import Decimal
from loguru import logger
from app.settings import settings


class APIConfigTester:
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=settings.fund_api_timeout)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()
    
    async def test_tiantian_fund_nav_api(self, fund_code: str = "000001"):
        """测试天天基金网净值API"""
        print(f"🔍 测试天天基金网净值API (基金代码: {fund_code})...")
        
        try:
            url = f"{settings.tiantian_fund_api_base_url}/js/{fund_code}.js"
            print(f"API地址: {url}")
            
            response = await self.session.get(url, headers=self.headers)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                print(f"响应长度: {len(content)} 字符")
                
                if content.startswith("jsonpgz(") and content.endswith(")"):
                    json_str = content[8:-1]
                    data = json.loads(json_str)
                    print(f"解析成功: {data}")
                    return True
                else:
                    print(f"响应格式异常: {content[:100]}...")
                    return False
            else:
                print(f"请求失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"测试失败: {e}")
            return False
    
    async def test_tiantian_fund_info_api(self, fund_code: str = "000001"):
        """测试天天基金网基金信息API"""
        print(f"🔍 测试天天基金网基金信息API (基金代码: {fund_code})...")
        
        try:
            url = f"{settings.tiantian_fund_info_base_url}/{fund_code}.js"
            print(f"API地址: {url}")
            
            response = await self.session.get(url, headers=self.headers)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                print(f"响应长度: {len(content)} 字符")
                
                # 检查是否包含基金信息
                if "fS_name" in content:
                    print("✅ 基金信息API响应正常")
                    return True
                else:
                    print(f"响应内容异常: {content[:100]}...")
                    return False
            else:
                print(f"请求失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"测试失败: {e}")
            return False
    
    async def test_xueqiu_api(self, fund_code: str = "000001"):
        """测试雪球API"""
        print(f"🔍 测试雪球API (基金代码: {fund_code})...")
        
        try:
            url = settings.xueqiu_api_base_url
            params = {
                "symbol": f"SH{fund_code}" if fund_code.startswith("5") else f"SZ{fund_code}",
                "period": "1d",
                "type": "before",
                "count": 1
            }
            print(f"API地址: {url}")
            print(f"参数: {params}")
            
            response = await self.session.get(url, params=params, headers=self.headers)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"响应数据: {data}")
                return True
            else:
                print(f"请求失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"测试失败: {e}")
            return False
    
    async def test_config_loading(self):
        """测试配置加载"""
        print("🔍 测试配置加载...")
        
        print(f"应用环境: {settings.app_env}")
        print(f"调试模式: {settings.debug}")
        print(f"数据库URL: {settings.database_url}")
        print(f"基金API超时: {settings.fund_api_timeout}秒")
        print(f"基金API重试次数: {settings.fund_api_retry_times}")
        print(f"天天基金网API地址: {settings.tiantian_fund_api_base_url}")
        print(f"天天基金网信息API地址: {settings.tiantian_fund_info_base_url}")
        print(f"雪球API地址: {settings.xueqiu_api_base_url}")
        print(f"时区: {settings.scheduler_timezone}")
        print(f"日志级别: {settings.log_level}")
        print(f"日志文件: {settings.log_file}")
        
        return True


async def main():
    """主测试函数"""
    print("🚀 开始API配置测试")
    print("=" * 50)
    
    async with APIConfigTester() as tester:
        # 测试配置加载
        print("\n1. 配置加载测试")
        await tester.test_config_loading()
        
        # 测试天天基金网净值API
        print("\n2. 天天基金网净值API测试")
        await tester.test_tiantian_fund_nav_api()
        
        # 测试天天基金网基金信息API
        print("\n3. 天天基金网基金信息API测试")
        await tester.test_tiantian_fund_info_api()
        
        # 测试雪球API
        print("\n4. 雪球API测试")
        await tester.test_xueqiu_api()
    
    print("\n" + "=" * 50)
    print("✅ API配置测试完成")


if __name__ == "__main__":
    asyncio.run(main()) 