#!/usr/bin/env python3
"""
启动脚本
"""
import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_railway_environment():
    """检查Railway环境配置"""
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
    data_path = os.getenv("DATABASE_PERSISTENT_PATH", "/app/data")
    
    print(f"🚀 启动个人财务管理系统")
    print(f"📍 运行环境: {'Railway' if is_railway else '本地/其他'}")
    print(f"📁 数据目录: {data_path}")
    
    # 确保数据目录存在
    Path(data_path).mkdir(parents=True, exist_ok=True)
    print(f"✅ 数据目录已确保存在")
    
    # 在Railway环境中修复volume权限
    if is_railway:
        try:
            import subprocess
            import pwd
            
            # 获取当前用户ID
            current_uid = os.getuid()
            current_gid = os.getgid()
            
            print(f"🔧 修复volume权限...")
            print(f"   当前用户ID: {current_uid}")
            print(f"   当前组ID: {current_gid}")
            
            # 修复数据目录权限
            subprocess.run(["chown", "-R", f"{current_uid}:{current_gid}", data_path], check=True)
            subprocess.run(["chmod", "-R", "755", data_path], check=True)
            print(f"✅ 数据目录权限已修复")
            
            # 检查数据库文件权限
            db_file = os.path.join(data_path, "personalfinance.db")
            if os.path.exists(db_file):
                subprocess.run(["chown", f"{current_uid}:{current_gid}", db_file], check=True)
                subprocess.run(["chmod", "644", db_file], check=True)
                print(f"✅ 数据库文件权限已修复")
                
        except Exception as e:
            print(f"⚠️  权限修复失败: {e}")
            print(f"   继续启动，但可能遇到权限问题")
    
    # 检查数据库文件
    db_file = os.path.join(data_path, "personalfinance.db")
    if os.path.exists(db_file):
        size_mb = os.path.getsize(db_file) / (1024 * 1024)
        print(f"📊 数据库文件: {db_file} (大小: {size_mb:.2f}MB)")
    else:
        print(f"📊 数据库文件: {db_file} (不存在，将创建新文件)")

if __name__ == "__main__":
    import uvicorn
    
    # 检查环境
    check_railway_environment()
    
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    print(f"🌐 服务端口: {port}")
    print(f"🐛 调试模式: {debug}")
    
    # 生产环境优化配置
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,  # 生产环境禁用reload
        workers=1 if debug else int(os.environ.get("WORKERS", "2")),  # 生产环境使用多进程
        access_log=debug,  # 生产环境可以禁用访问日志以提高性能
        log_level="info" if not debug else "debug"
    ) 