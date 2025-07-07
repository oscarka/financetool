#!/usr/bin/env python3
"""
启动脚本
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
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