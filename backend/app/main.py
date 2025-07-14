from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os
from pathlib import Path
from datetime import datetime

from app.settings import settings
from app.utils.database import init_database, get_data_directory, get_database_path
from app.api.v1 import funds, exchange_rates, wise, paypal, upload_db_router, logs, ibkr, scheduler, config
from app.services.extensible_scheduler_service import ExtensibleSchedulerService
from app.utils.middleware import RequestLoggingMiddleware
from app.utils.logger import log_system


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global extensible_scheduler
    
    # 启动时执行
    log_system("正在初始化数据库...")
    
    # 检查Railway环境
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
    log_system(f"运行环境: {'Railway' if is_railway else '本地/其他'}")
    
    # 检查数据目录和数据库文件
    data_dir = get_data_directory()
    db_path = get_database_path()
    log_system(f"数据目录: {data_dir}")
    log_system(f"数据库文件: {db_path}")
    
    # 检查数据库文件是否存在
    db_exists = os.path.exists(db_path)
    log_system(f"数据库文件存在: {db_exists}")
    
    init_database()
    
    # 初始化可扩展调度器
    extensible_scheduler = ExtensibleSchedulerService()
    
    # 生产环境延迟启动定时任务，避免启动时阻塞
    if os.environ.get("ENABLE_SCHEDULER", "true").lower() == "true":
        log_system("正在启动可扩展定时任务...")
        await extensible_scheduler.initialize()
    else:
        log_system("定时任务已禁用")
    
    log_system("应用启动完成")
    
    yield
    
    # 关闭时执行
    log_system("正在停止定时任务...")
    await extensible_scheduler.shutdown()
    log_system("应用正在关闭...")


# 全局调度器实例
extensible_scheduler = None

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="多资产投资记录与收益分析系统API",
    lifespan=lifespan,
    # 生产环境可以禁用文档来提高启动速度
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 注册路由
app.include_router(
    funds.router,
    prefix=f"{settings.api_v1_prefix}/funds",
    tags=["基金管理"]
)

app.include_router(
    exchange_rates.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["汇率管理"]
)

app.include_router(
    wise.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["Wise管理"]
)

app.include_router(
    paypal.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["PayPal管理"]
)

# IBKR API接口
app.include_router(
    ibkr.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["IBKR管理"]
)

# 临时：注册数据库上传接口
app.include_router(
    upload_db_router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["临时工具"]
)

# 注册日志管理接口
app.include_router(
    logs.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["日志管理"]
)

# 注册可扩展调度器管理接口
app.include_router(
    scheduler.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["调度器管理"]
)

# 注册配置管理接口
app.include_router(
    config.router,
    prefix=f"{settings.api_v1_prefix}/config",
    tags=["配置管理"]
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "个人财务管理系统API",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "文档已禁用"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    # 检查数据库文件状态
    db_path = get_database_path()
    db_exists = os.path.exists(db_path)
    db_size = os.path.getsize(db_path) if db_exists else 0
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "environment": "production" if not settings.debug else "development",
        "database": {
            "path": db_path,
            "exists": db_exists,
            "size_bytes": db_size
        }
    }

@app.get("/debug")
async def debug_info():
    """调试信息"""
    import os
    from pathlib import Path
    
    # 检查日志目录
    log_dir = Path("./logs")
    log_files = []
    if log_dir.exists():
        log_files = [f.name for f in log_dir.glob("*.log")]
    
    # 检查数据目录
    data_dir = get_data_directory()
    data_files = []
    if os.path.exists(data_dir):
        data_files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    
    return {
        "timestamp": datetime.now().isoformat(),
        "working_directory": os.getcwd(),
        "python_path": os.environ.get("PYTHONPATH", "未设置"),
        "port": os.environ.get("PORT", "未设置"),
        "debug": settings.debug,
        "data_directory": data_dir,
        "data_files": data_files,
        "log_directory_exists": log_dir.exists(),
        "log_files": log_files,
        "environment_vars": {
            "APP_ENV": os.environ.get("APP_ENV", "未设置"),
            "RAILWAY_ENVIRONMENT": os.environ.get("RAILWAY_ENVIRONMENT", "未设置"),
            "RAILWAY_PROJECT_ID": os.environ.get("RAILWAY_PROJECT_ID", "未设置"),
            "DATABASE_PERSISTENT_PATH": os.environ.get("DATABASE_PERSISTENT_PATH", "未设置"),
            "DATABASE_URL": os.environ.get("DATABASE_URL", "未设置")
        }
    }


@app.get("/logs-viewer", response_class=HTMLResponse)
async def logs_viewer():
    """日志查看页面"""
    try:
        html_file = Path(__file__).parent / "templates" / "logs.html"
        if html_file.exists():
            return HTMLResponse(content=html_file.read_text(encoding='utf-8'))
        else:
            return HTMLResponse(content="<h1>日志查看页面未找到</h1>", status_code=404)
    except Exception as e:
        return HTMLResponse(content=f"<h1>加载日志页面失败: {str(e)}</h1>", status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 