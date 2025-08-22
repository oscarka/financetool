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
        "BACKEND_URL": os.getenv("BACKEND_URL", "未设置"),
        "PORT": os.getenv("PORT", "未设置"),
        "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT", "未设置")
    }
    
    logger.info(f"📋 环境变量检查: {env_check}")
    
    # 检查服务状态
    service_status = {
        "mcp_server_initialized": mcp_server is not None,
        "ai_service_initialized": ai_service is not None,
        "chart_generator_initialized": chart_generator is not None
    }
    
    logger.info(f"🔧 服务状态检查: {service_status}")
    
    # 检查端口绑定状态
    port_status = "unknown"
    try:
        import socket
        current_port = int(os.getenv("PORT", "3001"))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', current_port))
        sock.close()
        
        if result == 0:
            port_status = f"port_{current_port}_available"
            logger.info(f"✅ 端口 {current_port} 可用")
        else:
            port_status = f"port_{current_port}_unavailable"
            logger.warning(f"⚠️ 端口 {current_port} 不可用")
    except Exception as e:
        port_status = f"port_check_error: {str(e)}"
        logger.error(f"❌ 端口检查失败: {e}")
    
    # 测试数据库连接
    db_connection_status = "unknown"
    db_error_details = ""
    try:
        if mcp_server and hasattr(mcp_server, 'db_config'):
            import psycopg2
            db_config = mcp_server.db_config
            logger.info(f"🔍 测试数据库连接: {db_config['host']}:{db_config['port']}/{db_config['database']}")
            logger.info(f"  用户: {db_config['user']}")
            logger.info(f"  密码: {'已设置' if db_config['password'] else '未设置'}")
            
            # 测试网络连通性
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((db_config['host'], db_config['port']))
                sock.close()
                
                if result == 0:
                    logger.info(f"✅ 网络连通性测试成功: {db_config['host']}:{db_config['port']}")
                else:
                    logger.warning(f"⚠️ 网络连通性测试失败: {db_config['host']}:{db_config['port']}")
                    db_error_details += f"网络不通: {db_config['host']}:{db_config['port']}; "
            except Exception as net_e:
                logger.warning(f"⚠️ 网络连通性测试异常: {net_e}")
                db_error_details += f"网络测试异常: {net_e}; "
            
            # 测试数据库连接
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database'],
                user=db_config['user'],
                password=db_config['password'],
                connect_timeout=10
            )
            
            # 测试简单查询
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result and result[0] == 1:
                db_connection_status = "connected"
                logger.info("✅ 数据库连接测试成功")
            else:
                db_connection_status = "query_failed"
                logger.warning("⚠️ 数据库连接成功但查询失败")
                
        else:
            db_connection_status = "no_config"
            db_error_details = "MCP服务器未初始化或缺少数据库配置"
            logger.warning("⚠️ 无法获取数据库配置")
            
    except psycopg2.OperationalError as e:
        db_connection_status = f"operational_error: {e.pgcode}"
        db_error_details = f"操作错误: {e}"
        logger.error(f"❌ 数据库连接操作错误: {e}")
    except psycopg2.InterfaceError as e:
        db_connection_status = f"interface_error: {str(e)}"
        db_error_details = f"接口错误: {e}"
        logger.error(f"❌ 数据库连接接口错误: {e}")
    except Exception as e:
        db_connection_status = f"error: {type(e).__name__}"
        db_error_details = f"异常: {str(e)}"
        logger.error(f"❌ 数据库连接测试失败: {e}")
    
    # 检查AI服务状态
    ai_services_status = {}
    ai_error_details = ""
    if mcp_server:
        try:
            ai_services_status = mcp_server.get_available_ai_services()
            logger.info(f"🤖 AI服务状态: {ai_services_status}")
        except Exception as e:
            logger.error(f"❌ 获取AI服务状态失败: {e}")
            ai_services_status = {"error": str(e)}
            ai_error_details = str(e)
    else:
        ai_error_details = "MCP服务器未初始化"
    
    # 检查后端服务连通性
    backend_connectivity = "unknown"
    backend_error_details = ""
    try:
        backend_url = os.getenv("BACKEND_URL")
        if backend_url:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{backend_url}/health")
                if response.status_code == 200:
                    backend_connectivity = "connected"
                    logger.info(f"✅ 后端服务连通性测试成功: {backend_url}")
                else:
                    backend_connectivity = f"http_error: {response.status_code}"
                    backend_error_details = f"HTTP状态码: {response.status_code}"
                    logger.warning(f"⚠️ 后端服务响应异常: {response.status_code}")
        else:
            backend_connectivity = "no_url"
            backend_error_details = "BACKEND_URL未设置"
            logger.warning("⚠️ BACKEND_URL未设置")
    except Exception as e:
        backend_connectivity = f"connection_error: {type(e).__name__}"
        backend_error_details = f"连接异常: {str(e)}"
        logger.error(f"❌ 后端服务连通性测试失败: {e}")
    
    # 构建响应
    overall_status = "healthy"
    if db_connection_status != "connected":
        overall_status = "degraded"
    if "error" in db_connection_status or "error" in ai_services_status:
        overall_status = "unhealthy"
    
    response = {
        "status": overall_status,
        "service": "mcp-service",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "diagnostics": {
            "environment_variables": env_check,
            "service_status": service_status,
            "port_status": port_status,
            "database_connection": {
                "status": db_connection_status,
                "error_details": db_error_details
            },
            "ai_services": ai_services_status,
            "ai_error_details": ai_error_details,
            "backend_connectivity": {
                "status": backend_connectivity,
                "error_details": backend_error_details
            }
        }
    }
    
    logger.info(f"📤 健康检查响应: {response}")
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
