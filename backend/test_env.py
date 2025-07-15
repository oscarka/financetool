#!/usr/bin/env python3
"""
测试环境变量
"""

import os

def test_environment():
    """测试环境变量"""
    print("🔍 环境变量测试")
    print("=" * 50)
    
    # 测试关键环境变量
    key_vars = [
        "DATABASE_URL",
        "APP_ENV", 
        "RAILWAY_ENVIRONMENT",
        "DATABASE_PERSISTENT_PATH"
    ]
    
    for var in key_vars:
        value = os.getenv(var)
        if value:
            if var == "DATABASE_URL":
                # 隐藏敏感信息
                display_value = value[:50] + "..." if len(value) > 50 else value
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: 未设置")
    
    # 测试数据库连接
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgresql://"):
            print("🎯 检测到PostgreSQL连接")
        elif database_url.startswith("sqlite://"):
            print("🎯 检测到SQLite连接")
        else:
            print("⚠️  未知的数据库连接类型")
    else:
        print("⚠️  未设置DATABASE_URL")

if __name__ == "__main__":
    test_environment() 