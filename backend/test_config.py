#!/usr/bin/env python3
"""
配置验证脚本
用于测试统一配置管理系统的功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_import():
    """测试配置导入"""
    print("🔧 测试配置导入...")
    
    try:
        from app.settings import settings, get_settings, BaseConfig, TestConfig, ProdConfig
        print("✅ 配置模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 配置模块导入失败: {e}")
        return False

def test_config_validation():
    """测试配置验证"""
    print("\n🔍 测试配置验证...")
    
    try:
        from app.settings import settings
        
        # 验证基础配置
        if not settings.validate_config():
            print("❌ 配置验证失败")
            return False
        
        print("✅ 配置验证通过")
        return True
    except Exception as e:
        print(f"❌ 配置验证异常: {e}")
        return False

def test_environment_config():
    """测试环境配置"""
    print("\n🌍 测试环境配置...")
    
    try:
        from app.settings import settings
        
        print(f"当前环境: {settings.app_env}")
        print(f"调试模式: {settings.debug}")
        print(f"数据库URL: {settings.database_url}")
        print(f"CORS Origins: {settings.get_cors_origins_list()}")
        print(f"日志级别: {settings.log_level}")
        
        # 测试环境判断
        if settings.is_development():
            print("✅ 开发环境检测正确")
        elif settings.is_production():
            print("✅ 生产环境检测正确")
        
        return True
    except Exception as e:
        print(f"❌ 环境配置测试失败: {e}")
        return False

def test_api_config():
    """测试API配置"""
    print("\n🔌 测试API配置...")
    
    try:
        from app.settings import settings
        
        # 检查各API配置
        apis = [
            ("OKX", settings.okx_api_key, settings.okx_sandbox),
            ("Wise", settings.wise_api_token, True),
            ("PayPal", settings.paypal_client_id, "sandbox" in settings.paypal_api_base_url),
            ("IBKR", settings.ibkr_api_key, settings.ibkr_enable_ip_whitelist)
        ]
        
        for name, key, env_info in apis:
            status = "✅ 已配置" if key else "⚠️ 未配置"
            print(f"{name} API: {status} ({env_info})")
        
        return True
    except Exception as e:
        print(f"❌ API配置测试失败: {e}")
        return False

def test_scheduler_config():
    """测试调度器配置"""
    print("\n⏰ 测试调度器配置...")
    
    try:
        from app.settings import settings
        
        print(f"调度器启用: {settings.enable_scheduler}")
        print(f"时区: {settings.scheduler_timezone}")
        print(f"任务默认配置: {settings.scheduler_job_defaults}")
        
        return True
    except Exception as e:
        print(f"❌ 调度器配置测试失败: {e}")
        return False

def test_security_config():
    """测试安全配置"""
    print("\n🔒 测试安全配置...")
    
    try:
        from app.settings import settings
        
        print(f"速率限制: {settings.security_enable_rate_limiting}")
        print(f"速率限制值: {settings.security_rate_limit_per_minute}/分钟")
        print(f"请求日志: {settings.security_enable_request_logging}")
        print(f"IBKR IP白名单: {settings.get_allowed_ips_list()}")
        
        return True
    except Exception as e:
        print(f"❌ 安全配置测试失败: {e}")
        return False

def test_performance_config():
    """测试性能配置"""
    print("\n⚡ 测试性能配置...")
    
    try:
        from app.settings import settings
        
        print(f"性能监控: {settings.performance_monitoring_enabled}")
        print(f"采样率: {settings.performance_sampling_rate}")
        print(f"缓存启用: {settings.cache_enabled}")
        print(f"缓存TTL: {settings.cache_default_ttl}秒")
        print(f"同步批量大小: {settings.sync_batch_size}")
        
        return True
    except Exception as e:
        print(f"❌ 性能配置测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始配置系统测试")
    print("=" * 50)
    
    # 设置测试环境
    os.environ["APP_ENV"] = "test"
    
    tests = [
        test_config_import,
        test_config_validation,
        test_environment_config,
        test_api_config,
        test_scheduler_config,
        test_security_config,
        test_performance_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有配置测试通过！")
        return 0
    else:
        print("⚠️ 部分配置测试失败，请检查配置")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 