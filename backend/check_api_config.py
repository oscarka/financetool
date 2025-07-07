#!/usr/bin/env python3
"""
API配置检查脚本
用于诊断和验证Wise和OKX API配置问题
"""

import os
import asyncio
from typing import Dict, List, Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

def check_environment_variables() -> Dict[str, bool]:
    """检查必要的环境变量是否存在"""
    required_vars = {
        'OKX_API_KEY': os.getenv('OKX_API_KEY'),
        'OKX_SECRET_KEY': os.getenv('OKX_SECRET_KEY'),
        'OKX_PASSPHRASE': os.getenv('OKX_PASSPHRASE'),
        'OKX_SANDBOX': os.getenv('OKX_SANDBOX'),
        'WISE_API_TOKEN': os.getenv('WISE_API_TOKEN'),
    }
    
    results = {}
    for var_name, var_value in required_vars.items():
        results[var_name] = bool(var_value and var_value.strip() and var_value != '你的APIKey' and var_value != '你的实际OKX_API_KEY')
    
    return results

async def test_api_endpoints(base_url: str = "http://localhost:8000") -> Dict[str, bool]:
    """测试API端点是否正常响应"""
    if not HTTPX_AVAILABLE:
        raise ImportError("httpx not available")
        
    endpoints = {
        'wise_config': f'{base_url}/api/v1/wise/config',
        'wise_test': f'{base_url}/api/v1/wise/test', 
        'okx_config': f'{base_url}/api/v1/funds/okx/config',
        'okx_test': f'{base_url}/api/v1/funds/okx/test',
    }
    
    results = {}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for name, url in endpoints.items():
            try:
                response = await client.get(url)
                results[name] = response.status_code == 200
                print(f"✓ {name}: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    if 'success' in data:
                        print(f"  Success: {data['success']}")
                    if 'data' in data:
                        print(f"  Data: {data['data']}")
                else:
                    print(f"  Error: {response.text}")
            except Exception as e:
                results[name] = False
                print(f"✗ {name}: {str(e)}")
    
    return results

def print_diagnosis_report(env_results: Dict[str, bool], api_results: Optional[Dict[str, bool]] = None):
    """打印诊断报告"""
    print("\n" + "="*60)
    print("Wise和OKX API配置诊断报告")
    print("="*60)
    
    print("\n1. 环境变量检查:")
    print("-" * 30)
    all_env_ok = True
    for var_name, is_ok in env_results.items():
        status = "✓" if is_ok else "✗"
        print(f"{status} {var_name}: {'已配置' if is_ok else '未配置或无效'}")
        if not is_ok:
            all_env_ok = False
    
    if api_results:
        print("\n2. API端点测试:")
        print("-" * 30)
        all_api_ok = True
        for endpoint, is_ok in api_results.items():
            status = "✓" if is_ok else "✗"
            print(f"{status} {endpoint}: {'正常' if is_ok else '异常'}")
            if not is_ok:
                all_api_ok = False
    
    print("\n3. 诊断结果:")
    print("-" * 30)
    if all_env_ok and (api_results is None or all(api_results.values())):
        print("✓ 所有配置正常！")
    else:
        print("✗ 发现配置问题:")
        if not all_env_ok:
            missing_vars = [var for var, ok in env_results.items() if not ok]
            print(f"  - 缺少环境变量: {', '.join(missing_vars)}")
        if api_results and not all(api_results.values()):
            failed_apis = [api for api, ok in api_results.items() if not ok]
            print(f"  - API端点异常: {', '.join(failed_apis)}")
    
    print("\n4. 解决方案:")
    print("-" * 30)
    if not all_env_ok:
        print("请在Railway项目设置中添加以下环境变量:")
        for var_name, is_ok in env_results.items():
            if not is_ok:
                if 'OKX' in var_name:
                    print(f"  {var_name}=你的实际{var_name}")
                elif 'WISE' in var_name:
                    print(f"  {var_name}=你的实际WISE_API_TOKEN")
        print("\n配置完成后重新部署应用。")
    
    print("\n5. 验证步骤:")
    print("-" * 30)
    print("1. 在Railway中配置环境变量")
    print("2. 重新部署应用")
    print("3. 运行此脚本验证: python check_api_config.py")
    print("4. 检查前端功能是否恢复")

def create_env_template():
    """创建环境变量配置模板"""
    template = """# API配置模板 - 请填入实际值
# 复制以下配置到Railway项目的环境变量设置中

# OKX API配置
OKX_API_KEY=你的实际OKX_API_KEY
OKX_SECRET_KEY=你的实际OKX_SECRET_KEY
OKX_PASSPHRASE=你的实际OKX_PASSPHRASE
OKX_SANDBOX=false  # 生产环境设为false，测试环境设为true

# Wise API配置  
WISE_API_TOKEN=你的实际WISE_API_TOKEN

# 其他配置
APP_ENV=prod
DEBUG=false
"""
    
    with open('env_template.txt', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"✓ 已创建环境变量配置模板: env_template.txt")

async def main():
    """主函数"""
    print("开始检查Wise和OKX API配置...")
    
    # 检查环境变量
    env_results = check_environment_variables()
    
    # 尝试测试API端点（如果服务正在运行）
    api_results: Optional[Dict[str, bool]] = None
    if HTTPX_AVAILABLE:
        try:
            print("\n尝试测试API端点...")
            api_results = await test_api_endpoints()
        except Exception as e:
            print(f"\n⚠️ 无法连接到API服务，可能服务未启动: {e}")
    else:
        print("\n⚠️ httpx模块未安装，跳过API端点测试")
    
    # 打印诊断报告
    print_diagnosis_report(env_results, api_results)
    
    # 创建配置模板
    print("\n" + "="*60)
    create_env_template()

if __name__ == "__main__":
    if HTTPX_AVAILABLE:
        asyncio.run(main())
    else:
        print("缺少依赖包，请先安装:")
        print("pip install httpx")
        print("\n或者只检查环境变量:")
        env_results = check_environment_variables()
        print_diagnosis_report(env_results)
        create_env_template()