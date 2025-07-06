from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.utils.database import init_database
from app.api.v1 import funds, exchange_rates, wise
from app.services.scheduler_service import scheduler_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("正在初始化数据库...")
    init_database()
    print("正在启动定时任务...")
    scheduler_service.start()
    print("应用启动完成")
    
    yield
    
    # 关闭时执行
    print("正在停止定时任务...")
    scheduler_service.stop()
    print("应用正在关闭...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="多资产投资记录与收益分析系统API",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "个人财务管理系统API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 