#!/usr/bin/env python3
"""
测试脚本
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试导入"""
    try:
        from app.settings import settings
        print("✅ 配置导入成功")
        
        from app.models.database import UserOperation, FundInfo, FundNav
        print("✅ 数据库模型导入成功")
        
        from app.services.fund_service import FundOperationService
        print("✅ 服务导入成功")
        
        from app.utils.database import init_database
        print("✅ 数据库工具导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_database():
    """测试数据库"""
    try:
        from app.utils.database import init_database
        init_database()
        print("✅ 数据库初始化成功")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def test_api():
    """测试API"""
    try:
        from app.main import app
        print("✅ API应用创建成功")
        return True
    except Exception as e:
        print(f"❌ API应用创建失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始测试后端...")
    
    # 测试导入
    if not test_imports():
        sys.exit(1)
    
    # 测试数据库
    if not test_database():
        sys.exit(1)
    
    # 测试API
    if not test_api():
        sys.exit(1)
    
    print("🎉 所有测试通过！") 