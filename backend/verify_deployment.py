#!/usr/bin/env python3
"""
部署验证脚本
用于验证Railway部署后数据持久化是否正常工作
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

def get_service_url():
    """获取服务URL"""
    # 从环境变量获取服务URL
    service_url = os.getenv('RAILWAY_SERVICE_URL')
    if not service_url:
        print("❌ 未设置RAILWAY_SERVICE_URL环境变量")
        return None
    return service_url

def check_service_health(service_url):
    """检查服务健康状态"""
    try:
        print(f"🔍 检查服务健康状态: {service_url}")
        
        # 检查基础健康端点
        response = requests.get(f"{service_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ 基础健康检查通过")
            return True
        else:
            print(f"❌ 基础健康检查失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 服务健康检查失败: {e}")
        return False

def check_data_health(service_url):
    """检查数据健康状态"""
    try:
        print(f"🔍 检查数据健康状态: {service_url}")
        
        # 检查数据健康端点
        response = requests.get(f"{service_url}/health/data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 数据健康检查通过")
            print(f"  - 状态: {data.get('status')}")
            if 'data_integrity' in data:
                integrity = data['data_integrity']
                print(f"  - IBKR账户: {integrity.get('ibkr_accounts', 0)}")
                print(f"  - IBKR余额: {integrity.get('ibkr_balances', 0)}")
                print(f"  - 有数据: {integrity.get('has_data', False)}")
            return True
        else:
            print(f"❌ 数据健康检查失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 数据健康检查失败: {e}")
        return False

def check_fund_data(service_url):
    """检查基金数据"""
    try:
        print(f"🔍 检查基金数据: {service_url}")
        
        # 检查基金信息
        response = requests.get(f"{service_url}/api/v1/funds/info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            fund_count = len(data.get('data', []))
            print(f"✅ 基金信息检查通过: {fund_count} 个基金")
        else:
            print(f"❌ 基金信息检查失败: {response.status_code}")
        
        # 检查基金操作记录
        response = requests.get(f"{service_url}/api/v1/funds/operations?page_size=1", timeout=10)
        if response.status_code == 200:
            data = response.json()
            operation_count = data.get('total', 0)
            print(f"✅ 基金操作记录检查通过: {operation_count} 条记录")
        else:
            print(f"❌ 基金操作记录检查失败: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ 基金数据检查失败: {e}")
        return False

def check_ibkr_data(service_url):
    """检查IBKR数据"""
    try:
        print(f"🔍 检查IBKR数据: {service_url}")
        
        # 检查IBKR账户
        response = requests.get(f"{service_url}/api/v1/ibkr/accounts", timeout=10)
        if response.status_code == 200:
            data = response.json()
            account_count = len(data.get('data', []))
            print(f"✅ IBKR账户检查通过: {account_count} 个账户")
        else:
            print(f"❌ IBKR账户检查失败: {response.status_code}")
        
        # 检查IBKR余额
        response = requests.get(f"{service_url}/api/v1/ibkr/balances", timeout=10)
        if response.status_code == 200:
            data = response.json()
            balance_count = len(data.get('data', []))
            print(f"✅ IBKR余额检查通过: {balance_count} 条记录")
        else:
            print(f"❌ IBKR余额检查失败: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ IBKR数据检查失败: {e}")
        return False

def check_wise_data(service_url):
    """检查Wise数据"""
    try:
        print(f"🔍 检查Wise数据: {service_url}")
        
        # 检查Wise交易记录
        response = requests.get(f"{service_url}/api/v1/wise/transactions", timeout=10)
        if response.status_code == 200:
            data = response.json()
            transaction_count = len(data.get('data', []))
            print(f"✅ Wise交易记录检查通过: {transaction_count} 条记录")
        else:
            print(f"❌ Wise交易记录检查失败: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ Wise数据检查失败: {e}")
        return False

def check_local_data_integrity():
    """检查本地数据完整性"""
    try:
        print("🔍 检查本地数据完整性")
        
        # 运行数据完整性检查脚本
        import subprocess
        result = subprocess.run([sys.executable, "check_data_integrity.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 本地数据完整性检查通过")
            return True
        else:
            print("❌ 本地数据完整性检查失败")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 本地数据完整性检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始部署验证...")
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 获取服务URL
    service_url = get_service_url()
    if not service_url:
        print("❌ 无法获取服务URL，跳过远程检查")
        service_url = "http://localhost:8000"  # 使用本地URL作为备选
    
    checks = [
        ("本地数据完整性", check_local_data_integrity),
        ("服务健康状态", lambda: check_service_health(service_url)),
        ("数据健康状态", lambda: check_data_health(service_url)),
        ("基金数据", lambda: check_fund_data(service_url)),
        ("IBKR数据", lambda: check_ibkr_data(service_url)),
        ("Wise数据", lambda: check_wise_data(service_url))
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}验证:")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}验证异常: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 验证结果汇总:")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  - {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 项验证通过")
    
    if passed == total:
        print("🎉 部署验证全部通过！数据持久化配置正常。")
        return 0
    else:
        print("⚠️  部署验证发现问题，请检查上述失败项")
        return 1

if __name__ == "__main__":
    sys.exit(main())