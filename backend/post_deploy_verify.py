#!/usr/bin/env python3
"""
部署后验证脚本
在Railway部署完成后验证数据持久化是否正常工作
"""
import os
import sys
import sqlite3
import requests
import time
from pathlib import Path
from datetime import datetime
import json

def wait_for_service(url, max_retries=30, delay=2):
    """等待服务启动"""
    print(f"⏳ 等待服务启动: {url}")
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ 服务已启动 (尝试 {i+1}/{max_retries})")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"  ⏳ 等待中... ({i+1}/{max_retries})")
        time.sleep(delay)
    
    print(f"❌ 服务启动超时")
    return False

def check_service_health(base_url):
    """检查服务健康状态"""
    print(f"\n🏥 检查服务健康状态...")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务健康检查通过")
            print(f"  状态: {data.get('status')}")
            print(f"  版本: {data.get('version')}")
            print(f"  环境: {data.get('environment')}")
            
            # 检查数据库信息
            if 'database' in data:
                db_info = data['database']
                print(f"  数据库路径: {db_info.get('path')}")
                print(f"  数据库存在: {db_info.get('exists')}")
                print(f"  数据库大小: {db_info.get('size_bytes', 0) / (1024*1024):.2f}MB")
            
            return True
        else:
            print(f"❌ 服务健康检查失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 服务健康检查异常: {e}")
        return False

def check_debug_info(base_url):
    """检查调试信息"""
    print(f"\n🐛 检查调试信息...")
    
    try:
        response = requests.get(f"{base_url}/debug", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 调试信息获取成功")
            print(f"  工作目录: {data.get('working_directory')}")
            print(f"  数据目录: {data.get('data_directory')}")
            print(f"  数据文件: {data.get('data_files', [])}")
            
            # 检查环境变量
            env_vars = data.get('environment_vars', {})
            print(f"  环境变量:")
            for key, value in env_vars.items():
                status = "✅" if value and value != "未设置" else "❌"
                print(f"    {status} {key}: {value}")
            
            return True
        else:
            print(f"❌ 调试信息获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 调试信息获取异常: {e}")
        return False

def test_database_operations(base_url):
    """测试数据库操作"""
    print(f"\n📊 测试数据库操作...")
    
    try:
        # 测试基金信息API
        response = requests.get(f"{base_url}/api/v1/funds/info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 基金信息API正常")
            print(f"  基金数量: {len(data.get('data', []))}")
        else:
            print(f"❌ 基金信息API失败: {response.status_code}")
        
        # 测试基金净值API
        response = requests.get(f"{base_url}/api/v1/funds/nav", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 基金净值API正常")
            print(f"  净值记录数: {len(data.get('data', []))}")
        else:
            print(f"❌ 基金净值API失败: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库操作测试异常: {e}")
        return False

def check_data_persistence(base_url):
    """检查数据持久化"""
    print(f"\n💾 检查数据持久化...")
    
    try:
        # 获取当前数据状态
        response = requests.get(f"{base_url}/api/v1/funds/nav", timeout=10)
        if response.status_code == 200:
            initial_data = response.json()
            initial_count = len(initial_data.get('data', []))
            print(f"  初始数据量: {initial_count} 条记录")
            
            # 等待一段时间
            print("  ⏳ 等待30秒...")
            time.sleep(30)
            
            # 再次检查数据
            response = requests.get(f"{base_url}/api/v1/funds/nav", timeout=10)
            if response.status_code == 200:
                final_data = response.json()
                final_count = len(final_data.get('data', []))
                print(f"  最终数据量: {final_count} 条记录")
                
                if initial_count == final_count:
                    print("  ✅ 数据持久化正常")
                    return True
                else:
                    print("  ❌ 数据持久化异常，数据量发生变化")
                    return False
            else:
                print(f"  ❌ 数据检查失败: {response.status_code}")
                return False
        else:
            print(f"  ❌ 初始数据获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ 数据持久化检查异常: {e}")
        return False

def generate_deployment_report(base_url, results):
    """生成部署报告"""
    print(f"\n📋 生成部署报告...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "base_url": base_url,
        "checks": results,
        "summary": {
            "total_checks": len(results),
            "passed_checks": sum(1 for r in results.values() if r),
            "failed_checks": sum(1 for r in results.values() if not r)
        }
    }
    
    # 保存报告
    report_file = "post_deploy_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 部署报告已保存: {report_file}")
    
    # 打印总结
    print(f"\n🎯 部署验证总结:")
    print(f"  总检查项: {report['summary']['total_checks']}")
    print(f"  通过: {report['summary']['passed_checks']}")
    print(f"  失败: {report['summary']['failed_checks']}")
    
    if report['summary']['failed_checks'] == 0:
        print("  🎉 所有检查通过！部署成功！")
    else:
        print("  ⚠️  部分检查失败，请检查配置")

def main():
    """主函数"""
    print("🚀 Railway部署后验证工具")
    print("=" * 50)
    
    # 获取服务URL
    base_url = os.getenv("SERVICE_URL", "http://localhost:8000")
    print(f"📍 服务地址: {base_url}")
    
    # 等待服务启动
    if not wait_for_service(base_url):
        print("❌ 服务启动失败，退出验证")
        return
    
    # 执行检查
    results = {}
    
    results["service_health"] = check_service_health(base_url)
    results["debug_info"] = check_debug_info(base_url)
    results["database_operations"] = test_database_operations(base_url)
    results["data_persistence"] = check_data_persistence(base_url)
    
    # 生成报告
    generate_deployment_report(base_url, results)

if __name__ == "__main__":
    main()