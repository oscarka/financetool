#!/usr/bin/env python3
"""
基金API测试脚本
用于验证天天基金网API是否正常工作
"""

import asyncio
import json
import httpx
from datetime import date


async def test_tiantian_fund_nav_api():
    """测试天天基金网净值API"""
    print("🔍 测试天天基金网净值API...")
    
    fund_code = "000001"
    url = f"https://fundgz.1234567.com.cn/js/{fund_code}.js"
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.text
            
            print(f"✅ API响应状态: {response.status_code}")
            print(f"📄 响应内容预览: {content[:100]}...")
            
            # 解析JSONP格式
            if content.startswith("jsonpgz(") and content.endswith(";"):
                json_str = content[8:-2]  # 去掉 jsonpgz( 和 );
                data = json.loads(json_str)
                
                print(f"✅ 解析成功!")
                print(f"📊 基金代码: {data.get('fundcode')}")
                print(f"📊 基金名称: {data.get('name')}")
                print(f"📊 净值: {data.get('dwjz')}")
                print(f"📊 估算净值: {data.get('gsz')}")
                print(f"📊 净值日期: {data.get('jzrq')}")
                print(f"📊 增长率: {data.get('gszzl')}%")
                print(f"📊 更新时间: {data.get('gztime')}")
                
                return True
            else:
                print("❌ 响应格式不符合预期")
                return False
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def test_tiantian_fund_info_api():
    """测试天天基金网基金信息API"""
    print("\n🔍 测试天天基金网基金信息API...")
    
    fund_code = "000001"
    url = f"https://fund.eastmoney.com/pingzhongdata/{fund_code}.js"
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.text
            
            print(f"✅ API响应状态: {response.status_code}")
            print(f"📄 响应内容长度: {len(content)} 字符")
            
            # 解析关键信息
            import re
            
            fund_name_match = re.search(r'fS_name\s*=\s*"([^"]+)"', content)
            fund_code_match = re.search(r'fS_code\s*=\s*"([^"]+)"', content)
            min_purchase_match = re.search(r'fund_minsg\s*=\s*"([^"]+)"', content)
            purchase_fee_match = re.search(r'fund_sourceRate\s*=\s*"([^"]+)"', content)
            management_fee_match = re.search(r'fund_Rate\s*=\s*"([^"]+)"', content)
            
            if fund_name_match and fund_code_match:
                print(f"✅ 解析成功!")
                print(f"📊 基金代码: {fund_code_match.group(1)}")
                print(f"📊 基金名称: {fund_name_match.group(1)}")
                print(f"📊 最小申购额: {min_purchase_match.group(1) if min_purchase_match else 'N/A'}")
                print(f"📊 申购费率: {purchase_fee_match.group(1) if purchase_fee_match else 'N/A'}%")
                print(f"📊 管理费率: {management_fee_match.group(1) if management_fee_match else 'N/A'}%")
                
                return True
            else:
                print("❌ 无法解析基金信息")
                return False
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def test_multiple_funds():
    """测试多个基金代码"""
    print("\n🔍 测试多个基金代码...")
    
    fund_codes = ["000001", "110022", "161725", "005827", "001938"]
    success_count = 0
    
    for fund_code in fund_codes:
        try:
            url = f"https://fundgz.1234567.com.cn/js/{fund_code}.js"
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    content = response.text
                    if content.startswith("jsonpgz("):
                        data = json.loads(content[8:-2])
                        print(f"✅ {fund_code}: {data.get('name', 'N/A')} - {data.get('dwjz', 'N/A')}")
                        success_count += 1
                    else:
                        print(f"❌ {fund_code}: 格式错误")
                else:
                    print(f"❌ {fund_code}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {fund_code}: {e}")
    
    print(f"\n📊 测试结果: {success_count}/{len(fund_codes)} 个基金成功")
    return success_count == len(fund_codes)


async def main():
    """主测试函数"""
    print("🚀 开始基金API测试...")
    print("=" * 50)
    
    # 测试净值API
    nav_success = await test_tiantian_fund_nav_api()
    
    # 测试基金信息API
    info_success = await test_tiantian_fund_info_api()
    
    # 测试多个基金
    multi_success = await test_multiple_funds()
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 测试总结:")
    print(f"净值API: {'✅ 正常' if nav_success else '❌ 异常'}")
    print(f"基金信息API: {'✅ 正常' if info_success else '❌ 异常'}")
    print(f"多基金测试: {'✅ 正常' if multi_success else '❌ 异常'}")
    
    if nav_success and info_success:
        print("\n🎉 天天基金网API工作正常!")
        print("💡 建议: 可以正常使用基金数据同步功能")
    else:
        print("\n⚠️  天天基金网API存在问题!")
        print("💡 建议: 检查网络连接或联系技术支持")


if __name__ == "__main__":
    asyncio.run(main())