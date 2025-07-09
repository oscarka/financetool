#!/usr/bin/env python3
"""
部署诊断脚本
"""
import os
import sys
from pathlib import Path

def check_environment():
    """检查环境变量"""
    print("=== 环境变量检查 ===")
    important_vars = [
        "PORT", "DEBUG", "APP_ENV", "DATABASE_URL", 
        "RAILWAY_ENVIRONMENT", "RAILWAY_PROJECT_ID"
    ]
    
    for var in important_vars:
        value = os.environ.get(var, "未设置")
        print(f"{var}: {value}")
    
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python路径: {sys.path[0]}")

def check_files():
    """检查关键文件"""
    print("\n=== 文件检查 ===")
    files_to_check = [
        "app/main.py",
        "app/utils/logger.py", 
        "app/utils/auto_logger.py",
        "app/api/v1/logs.py",
        "app/templates/logs.html",
        "logs"
    ]
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            if path.is_dir():
                print(f"✓ {file_path} (目录)")
                # 列出目录内容
                try:
                    for item in path.iterdir():
                        print(f"  - {item.name}")
                except Exception as e:
                    print(f"  无法读取目录: {e}")
            else:
                print(f"✓ {file_path} ({path.stat().st_size} bytes)")
        else:
            print(f"✗ {file_path} (不存在)")

def test_logging():
    """测试日志系统"""
    print("\n=== 日志系统测试 ===")
    try:
        from app.utils.logger import log_system, log_api, log_database
        from app.utils.auto_logger import quick_log
        
        print("导入日志模块成功")
        
        # 测试基础日志
        log_system("诊断脚本: 系统日志测试")
        log_api("诊断脚本: API日志测试")
        log_database("诊断脚本: 数据库日志测试")
        quick_log("诊断脚本: 快速日志测试", "business")
        
        print("日志写入测试完成")
        
        # 检查日志文件
        log_dir = Path("logs")
        if log_dir.exists():
            print("日志目录存在")
            for log_file in log_dir.glob("*.log"):
                print(f"  - {log_file.name}")
        else:
            print("日志目录不存在")
            
    except Exception as e:
        print(f"日志系统测试失败: {e}")

def test_app_import():
    """测试应用导入"""
    print("\n=== 应用导入测试 ===")
    try:
        from app.main import app
        print("✓ 应用导入成功")
        
        # 检查路由
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        print(f"注册的路由数量: {len(routes)}")
        print("主要路由:")
        for route in routes[:10]:  # 只显示前10个
            print(f"  - {route}")
            
    except Exception as e:
        print(f"✗ 应用导入失败: {e}")

if __name__ == "__main__":
    print("🚀 Railway部署诊断")
    print("=" * 50)
    
    check_environment()
    check_files()
    test_logging()
    test_app_import()
    
    print("\n" + "=" * 50)
    print("诊断完成")