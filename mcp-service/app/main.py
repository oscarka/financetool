"""
MCP智能服务主应用
独立部署的MCP协议服务，提供AI分析和智能图表功能
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import asyncio
import json
import os
from datetime import datetime

from app.services.mcp_server import MCPServer
from app.services.ai_service import DeepSeekAIService
from app.services.chart_service import ChartConfigGenerator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="MCP智能服务",
    version="1.0.0",
    description="独立部署的MCP协议服务，提供AI分析和智能图表功能"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局服务实例
mcp_server = None
ai_service = None
chart_generator = None

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化服务"""
    global mcp_server, ai_service, chart_generator
    
    logger.info("🚀 MCP智能服务正在启动...")
    
    # 检查环境变量
    logger.info("📋 检查环境变量...")
    env_vars = {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": "已设置" if os.getenv("DB_PASSWORD") else "未设置",
        "DEEPSEEK_API_KEY": "已设置" if os.getenv("DEEPSEEK_API_KEY") else "未设置",
        "BACKEND_URL": os.getenv("BACKEND_URL")
    }
    
    for key, value in env_vars.items():
        if key == "DB_PASSWORD" or key == "DEEPSEEK_API_KEY":
            logger.info(f"  {key}: {value}")
        else:
            logger.info(f"  {key}: {value or '未设置'}")
    
    try:
        # 初始化AI服务
        logger.info("🤖 初始化DeepSeek AI服务...")
        ai_service = DeepSeekAIService()
        logger.info("✅ DeepSeek AI服务初始化成功")
        
        # 初始化图表生成器
        logger.info("🎨 初始化图表配置生成器...")
        chart_generator = ChartConfigGenerator()
        logger.info("✅ 图表配置生成器初始化成功")
        
        # 初始化MCP服务器
        logger.info("🔧 初始化MCP服务器...")
        mcp_server = MCPServer(ai_service, chart_generator)
        logger.info("✅ MCP服务器初始化成功")
        
        # 测试数据库连接
        logger.info("🔍 测试数据库连接...")
        try:
            import psycopg2
            db_config = mcp_server.db_config
            logger.info(f"  连接信息: {db_config['host']}:{db_config['port']}/{db_config['database']}")
            
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database'],
                user=db_config['user'],
                password=db_config['password'],
                connect_timeout=10
            )
            conn.close()
            logger.info("✅ 数据库连接测试成功")
        except Exception as e:
            logger.error(f"❌ 数据库连接测试失败: {e}")
            raise
        
        # 显示可用AI服务
        logger.info("📊 检查可用AI服务...")
        ai_services = mcp_server.get_available_ai_services()
        logger.info("📊 可用AI服务:")
        for service, info in ai_services.items():
            status = "✅" if info["available"] else "❌"
            logger.info(f"  {status} {service}: {info['description']}")
        
        logger.info("🎉 MCP智能服务启动完成")
        
    except Exception as e:
        logger.error(f"❌ 服务初始化失败: {e}")
        logger.error(f"❌ 错误详情: {str(e)}")
        import traceback
        logger.error(f"❌ 堆栈跟踪: {traceback.format_exc()}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    logger.info("🔄 MCP智能服务正在关闭...")

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    logger.info("🔍 收到健康检查请求")
    
    # 检查环境变量
    env_check = {
        "DB_HOST": os.getenv("DB_HOST", "未设置"),
        "DB_PORT": os.getenv("DB_PORT", "未设置"),
        "DB_NAME": os.getenv("DB_NAME", "未设置"),
        "DB_USER": os.getenv("DB_USER", "未设置"),
        "DB_PASSWORD": "已设置" if os.getenv("DB_PASSWORD") else "未设置",
        "DEEPSEEK_API_KEY": "已设置" if os.getenv("DEEPSEEK_API_KEY") else "未设置",
        "BACKEND_URL": os.getenv("BACKEND_URL", "未设置")
    }
    
    logger.info(f"📋 环境变量检查: {env_check}")
    
    # 检查服务状态
    service_status = {
        "mcp_server_initialized": mcp_server is not None,
        "ai_service_initialized": ai_service is not None,
        "chart_generator_initialized": chart_generator is not None
    }
    
    logger.info(f"🔧 服务状态检查: {service_status}")
    
    # 测试数据库连接
    db_connection_status = "unknown"
    try:
        if mcp_server and hasattr(mcp_server, 'db_config'):
            import psycopg2
            db_config = mcp_server.db_config
            logger.info(f"🔍 测试数据库连接: {db_config['host']}:{db_config['port']}/{db_config['database']}")
            
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database'],
                user=db_config['user'],
                password=db_config['password'],
                connect_timeout=5
            )
            conn.close()
            db_connection_status = "connected"
            logger.info("✅ 数据库连接测试成功")
        else:
            db_connection_status = "no_config"
            logger.warning("⚠️ 无法获取数据库配置")
            if not mcp_server:
                logger.error("❌ mcp_server 未初始化")
            elif not hasattr(mcp_server, 'db_config'):
                logger.error("❌ mcp_server 缺少 db_config 属性")
    except Exception as e:
        db_connection_status = f"error: {str(e)}"
        logger.error(f"❌ 数据库连接测试失败: {e}")
        logger.error(f"❌ 错误类型: {type(e).__name__}")
        import traceback
        logger.error(f"❌ 堆栈跟踪: {traceback.format_exc()}")
    
    # 检查AI服务状态
    ai_services_status = {}
    if mcp_server:
        try:
            ai_services_status = mcp_server.get_available_ai_services()
            logger.info(f"🤖 AI服务状态: {ai_services_status}")
        except Exception as e:
            logger.error(f"❌ 获取AI服务状态失败: {e}")
            ai_services_status = {"error": str(e)}
    else:
        logger.warning("⚠️ mcp_server 未初始化，无法检查AI服务状态")
        ai_services_status = {"error": "mcp_server not initialized"}
    
    # 构建响应
    overall_status = "healthy"
    if db_connection_status != "connected":
        overall_status = "degraded"
        logger.warning(f"⚠️ 服务状态降级: 数据库连接状态 = {db_connection_status}")
    
    response = {
        "status": overall_status,
        "service": "mcp-service",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "diagnostics": {
            "environment_variables": env_check,
            "service_status": service_status,
            "database_connection": db_connection_status,
            "ai_services": ai_services_status
        }
    }
    
    logger.info(f"📤 健康检查响应: status={overall_status}, db_status={db_connection_status}")
    return response

@app.get("/ai-services")
async def get_ai_services():
    """获取可用的AI服务信息"""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="服务未初始化")
    
    return mcp_server.get_available_ai_services()

# MCP查询端点
@app.post("/query")
async def mcp_query(request: Dict[str, Any]):
    """MCP查询处理"""
    try:
        method = request.get("method", "")
        params = request.get("params", {})
        
        logger.info(f"🔍 收到MCP查询: method={method}")
        
        if method == "execute_sql":
            # 执行SQL查询
            sql = params.get("sql", "")
            max_rows = params.get("max_rows", 1000)
            
            if not sql:
                raise HTTPException(status_code=400, detail="SQL语句不能为空")
            
            result = await mcp_server.execute_sql(sql, max_rows)
            return result
            
        elif method == "natural_query":
            # 自然语言查询
            question = params.get("question", "")
            context = params.get("context", {})
            max_rows = params.get("max_rows", 1000)
            
            if not question:
                raise HTTPException(status_code=400, detail="问题不能为空")
            
            ai_service = params.get("ai_service", "auto")
            result = await mcp_server.natural_language_query(question, context, max_rows, ai_service)
            return result
            
        else:
            raise HTTPException(status_code=400, detail=f"不支持的方法: {method}")
            
    except Exception as e:
        logger.error(f"❌ MCP查询处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 自然语言查询端点
@app.post("/nl-query")
async def natural_language_query(request: Dict[str, Any]):
    """自然语言查询处理"""
    try:
        question = request.get("question", "")
        context = request.get("context", {})
        max_rows = request.get("max_rows", 1000)
        
        if not question:
            raise HTTPException(status_code=400, detail="问题不能为空")
        
        logger.info(f"🔍 收到自然语言查询: {question}")
        
        ai_service = request.get("ai_service", "auto")
        result = await mcp_server.natural_language_query(question, context, max_rows, ai_service)
        return result
        
    except Exception as e:
        logger.error(f"❌ 自然语言查询处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Schema查询端点
@app.post("/schema")
async def get_schema(request: Dict[str, Any]):
    """获取数据库Schema信息"""
    try:
        method = request.get("method", "")
        params = request.get("params", {})
        
        if method == "describe_tables":
            tables = params.get("tables", [])
            schema = await mcp_server.get_database_schema(tables)
            return schema
        else:
            raise HTTPException(status_code=400, detail=f"不支持的方法: {method}")
            
    except Exception as e:
        logger.error(f"❌ Schema查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 图表生成端点
@app.post("/generate-chart")
async def generate_chart(request: Dict[str, Any]):
    """生成智能图表"""
    try:
        question = request.get("question", "")
        data = request.get("data", [])
        chart_type = request.get("chart_type", "auto")
        
        if not question or not data:
            raise HTTPException(status_code=400, detail="问题和数据不能为空")
        
        logger.info(f"🎨 生成图表: {question}")
        
        chart_config = await mcp_server.generate_chart_config(question, data, chart_type)
        return chart_config
        
    except Exception as e:
        logger.error(f"❌ 图表生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3001))
    uvicorn.run(app, host="0.0.0.0", port=port)
