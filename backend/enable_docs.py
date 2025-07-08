#!/usr/bin/env python3
"""
临时启用API文档的脚本
在生产环境也可以访问Swagger文档
"""
import os
import uvicorn
from app.main import app

def enable_docs():
    """强制启用API文档"""
    # 临时覆盖文档配置
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"
    app.openapi_url = "/openapi.json"
    
    print("🔓 API文档已临时启用!")
    print(f"📚 Swagger文档: http://localhost:8000/docs")
    print(f"📖 ReDoc文档: http://localhost:8000/redoc")
    print("⚠️  注意: 这是临时启用，重启后会恢复原设置")
    print("\n🚀 启动服务器...")

if __name__ == "__main__":
    enable_docs()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )