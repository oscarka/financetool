from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os
from pathlib import Path

from app.config import settings
from app.utils.database import init_database
from app.api.v1 import funds, exchange_rates, wise, paypal, upload_db_router, logs
from app.services.scheduler_service import scheduler_service
from app.utils.middleware import RequestLoggingMiddleware
from app.utils.logger import log_system


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    log_system("正在初始化数据库...")
    init_database()
    
    # 生产环境延迟启动定时任务，避免启动时阻塞
    if os.environ.get("ENABLE_SCHEDULER", "true").lower() == "true":
        log_system("正在启动定时任务...")
        scheduler_service.start()
    else:
        log_system("定时任务已禁用")
    
    log_system("应用启动完成")
    
    yield
    
    # 关闭时执行
    log_system("正在停止定时任务...")
    scheduler_service.stop()
    log_system("应用正在关闭...")


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
    allow_origins=settings.cors_origins,
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
    return {"status": "healthy"}


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