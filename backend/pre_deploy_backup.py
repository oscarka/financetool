#!/usr/bin/env python3
"""
部署前自动备份脚本
在Railway部署前自动备份重要数据
"""

import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path

def get_railway_service_url():
    """获取Railway服务URL"""
    # 从环境变量获取服务URL
    service_url = os.getenv('RAILWAY_SERVICE_URL')
    if not service_url:
        print("❌ 未设置RAILWAY_SERVICE_URL环境变量")
        return None
    return service_url

def backup_ibkr_data(service_url):
    """备份IBKR数据"""
    try:
        print("🔄 开始备份IBKR数据...")
        
        # 获取IBKR账户数据
        accounts_response = requests.get(f"{service_url}/api/v1/ibkr/accounts", timeout=30)
        if accounts_response.status_code == 200:
            accounts_data = accounts_response.json()
            print(f"✅ 获取到 {len(accounts_data.get('data', []))} 个IBKR账户")
        else:
            print(f"⚠️  获取IBKR账户失败: {accounts_response.status_code}")
        
        # 获取IBKR余额数据
        balances_response = requests.get(f"{service_url}/api/v1/ibkr/balances", timeout=30)
        if balances_response.status_code == 200:
            balances_data = balances_response.json()
            print(f"✅ 获取到 {len(balances_data.get('data', []))} 条余额记录")
        else:
            print(f"⚠️  获取IBKR余额失败: {balances_response.status_code}")
        
        # 获取IBKR持仓数据
        positions_response = requests.get(f"{service_url}/api/v1/ibkr/positions", timeout=30)
        if positions_response.status_code == 200:
            positions_data = positions_response.json()
            print(f"✅ 获取到 {len(positions_data.get('data', []))} 条持仓记录")
        else:
            print(f"⚠️  获取IBKR持仓失败: {positions_response.status_code}")
        
        # 获取同步日志
        logs_response = requests.get(f"{service_url}/api/v1/ibkr/logs?limit=100", timeout=30)
        if logs_response.status_code == 200:
            logs_data = logs_response.json()
            print(f"✅ 获取到 {len(logs_data.get('data', []))} 条同步日志")
        else:
            print(f"⚠️  获取IBKR日志失败: {logs_response.status_code}")
        
        # 保存备份数据
        backup_data = {
            "backup_time": datetime.now().isoformat(),
            "accounts": accounts_data.get('data', []) if accounts_response.status_code == 200 else [],
            "balances": balances_data.get('data', []) if balances_response.status_code == 200 else [],
            "positions": positions_data.get('data', []) if positions_response.status_code == 200 else [],
            "logs": logs_data.get('data', []) if logs_response.status_code == 200 else []
        }
        
        # 创建备份目录
        backup_dir = Path("./backups")
        backup_dir.mkdir(exist_ok=True)
        
        # 保存备份文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"ibkr_backup_{timestamp}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ IBKR数据备份完成: {backup_file}")
        return str(backup_file)
        
    except Exception as e:
        print(f"❌ IBKR数据备份失败: {e}")
        return None

def backup_other_data(service_url):
    """备份其他重要数据"""
    try:
        print("🔄 开始备份其他数据...")
        
        backup_data = {
            "backup_time": datetime.now().isoformat(),
            "wise_transactions": [],
            "wise_balances": [],
            "user_operations": [],
            "asset_positions": [],
            "fund_info": [],
            "dca_plans": []
        }
        
        # 获取Wise数据
        try:
            wise_response = requests.get(f"{service_url}/api/v1/wise/transactions", timeout=30)
            if wise_response.status_code == 200:
                backup_data["wise_transactions"] = wise_response.json().get('data', [])
                print(f"✅ 获取到 {len(backup_data['wise_transactions'])} 条Wise交易记录")
        except Exception as e:
            print(f"⚠️  获取Wise数据失败: {e}")
        
        # 获取用户操作记录
        try:
            operations_response = requests.get(f"{service_url}/api/v1/operations", timeout=30)
            if operations_response.status_code == 200:
                backup_data["user_operations"] = operations_response.json().get('data', [])
                print(f"✅ 获取到 {len(backup_data['user_operations'])} 条用户操作记录")
        except Exception as e:
            print(f"⚠️  获取用户操作记录失败: {e}")
        
        # 获取资产持仓
        try:
            positions_response = requests.get(f"{service_url}/api/v1/positions", timeout=30)
            if positions_response.status_code == 200:
                backup_data["asset_positions"] = positions_response.json().get('data', [])
                print(f"✅ 获取到 {len(backup_data['asset_positions'])} 条资产持仓记录")
        except Exception as e:
            print(f"⚠️  获取资产持仓失败: {e}")
        
        # 保存备份文件
        backup_dir = Path("./backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"other_data_backup_{timestamp}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 其他数据备份完成: {backup_file}")
        return str(backup_file)
        
    except Exception as e:
        print(f"❌ 其他数据备份失败: {e}")
        return None

def main():
    """主函数"""
    print("🚀 开始部署前数据备份...")
    
    # 获取服务URL
    service_url = get_railway_service_url()
    if not service_url:
        print("❌ 无法获取服务URL，跳过备份")
        return
    
    print(f"📍 服务URL: {service_url}")
    
    # 备份IBKR数据
    ibkr_backup_file = backup_ibkr_data(service_url)
    
    # 备份其他数据
    other_backup_file = backup_other_data(service_url)
    
    # 输出备份结果
    print("\n📋 备份结果:")
    if ibkr_backup_file:
        print(f"  ✅ IBKR数据: {ibkr_backup_file}")
    else:
        print("  ❌ IBKR数据备份失败")
    
    if other_backup_file:
        print(f"  ✅ 其他数据: {other_backup_file}")
    else:
        print("  ❌ 其他数据备份失败")
    
    print("\n🎉 部署前备份完成！")

if __name__ == "__main__":
    main()