#!/usr/bin/env python3
"""
测试前端聚合数据功能
"""
import requests
import json
import time

def test_frontend_aggregation():
    """测试前端聚合数据功能"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 开始测试前端聚合数据功能...")
    
    # 1. 测试聚合统计数据
    print("\n📊 1. 测试聚合统计数据")
    try:
        response = requests.get(f"{base_url}/aggregation/stats?base_currency=CNY", timeout=10)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('data', {})
            print(f"✅ 总资产价值: {stats.get('total_value', 0):,.2f} CNY")
            print(f"✅ 资产数量: {stats.get('asset_count', 0)} 个")
            print(f"✅ 平台数量: {stats.get('platform_count', 0)} 个")
            print(f"✅ 资产类型数: {stats.get('asset_type_count', 0)} 种")
            
            # 显示平台分布
            platform_stats = stats.get('platform_stats', {})
            if platform_stats:
                print("📈 平台分布:")
                for platform, value in platform_stats.items():
                    print(f"   - {platform}: {value:,.2f} CNY")
            
            # 显示资产类型分布
            asset_type_stats = stats.get('asset_type_stats', {})
            if asset_type_stats:
                print("📊 资产类型分布:")
                for asset_type, value in asset_type_stats.items():
                    print(f"   - {asset_type}: {value:,.2f} CNY")
        else:
            print(f"❌ 聚合统计API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 聚合统计API异常: {e}")
    
    # 2. 测试趋势数据
    print("\n📈 2. 测试趋势数据")
    try:
        response = requests.get(f"{base_url}/aggregation/trend?days=30&base_currency=CNY", timeout=10)
        if response.status_code == 200:
            data = response.json()
            trend_data = data.get('data', [])
            print(f"✅ 趋势数据: {len(trend_data)} 条记录")
            if trend_data:
                print(f"   最新数据: {trend_data[-1] if trend_data else '无'}")
        else:
            print(f"❌ 趋势数据API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 趋势数据API异常: {e}")
    
    # 3. 测试资产类型分布
    print("\n📊 3. 测试资产类型分布")
    try:
        response = requests.get(f"{base_url}/aggregation/distribution/asset-type?base_currency=CNY", timeout=10)
        if response.status_code == 200:
            data = response.json()
            distribution_data = data.get('data', [])
            print(f"✅ 资产类型分布: {len(distribution_data)} 种类型")
            for item in distribution_data:
                print(f"   - {item.get('type', 'N/A')}: {item.get('value', 0):,.2f} CNY")
        else:
            print(f"❌ 资产类型分布API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 资产类型分布API异常: {e}")
    
    # 4. 测试平台分布
    print("\n🏦 4. 测试平台分布")
    try:
        response = requests.get(f"{base_url}/aggregation/distribution/platform?base_currency=CNY", timeout=10)
        if response.status_code == 200:
            data = response.json()
            distribution_data = data.get('data', [])
            print(f"✅ 平台分布: {len(distribution_data)} 个平台")
            for item in distribution_data:
                print(f"   - {item.get('platform', 'N/A')}: {item.get('value', 0):,.2f} CNY")
        else:
            print(f"❌ 平台分布API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 平台分布API异常: {e}")
    
    # 5. 测试完整仪表板数据
    print("\n📊 5. 测试完整仪表板数据")
    try:
        response = requests.get(f"{base_url}/aggregation/dashboard?base_currency=CNY&days=30", timeout=15)
        if response.status_code == 200:
            data = response.json()
            dashboard_data = data.get('data', {})
            print(f"✅ 仪表板数据获取成功")
            print(f"   基准货币: {dashboard_data.get('base_currency', 'N/A')}")
            print(f"   趋势天数: {dashboard_data.get('trend_days', 0)} 天")
            
            stats = dashboard_data.get('stats', {})
            if stats:
                print(f"   总资产价值: {stats.get('total_value', 0):,.2f} CNY")
                print(f"   资产数量: {stats.get('asset_count', 0)} 个")
        else:
            print(f"❌ 仪表板数据API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 仪表板数据API异常: {e}")
    
    print("\n🎉 前端聚合数据测试完成!")
    print("\n💡 提示:")
    print("1. 访问 http://localhost:5173 查看前端页面")
    print("2. 检查图表组件是否显示真实数据")
    print("3. 检查统计数据是否与API返回一致")

if __name__ == "__main__":
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(2)
    test_frontend_aggregation()