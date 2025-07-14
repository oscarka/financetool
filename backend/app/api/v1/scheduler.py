"""
可扩展调度器管理API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from app.services.extensible_scheduler_service import ExtensibleSchedulerService
from app.models.schemas import BaseResponse

router = APIRouter(prefix="/scheduler", tags=["调度器管理"])

# 全局调度器实例
scheduler_service = None


def get_scheduler_service() -> ExtensibleSchedulerService:
    """获取调度器服务实例"""
    from app.main import extensible_scheduler
    if extensible_scheduler is None:
        raise RuntimeError("调度器服务未初始化")
    return extensible_scheduler


@router.get("/test")
async def test_scheduler():
    """测试接口"""
    logger.info("[DEBUG] test_scheduler 接口被调用")
    return {"message": "scheduler test ok", "timestamp": datetime.now().isoformat()}


@router.post("/test-create-job", response_model=BaseResponse)
async def test_create_job():
    """测试创建任务接口"""
    try:
        service = get_scheduler_service()
        
        # 获取可用任务
        tasks = service.get_tasks()
        if not tasks:
            return BaseResponse(success=False, message="没有可用的任务")
        
        # 使用第一个任务进行测试
        test_task = tasks[0]
        
        # 创建测试任务配置
        job_config = {
            "task_id": test_task['task_id'],
            "name": "测试任务",
            "schedule": {
                "type": "cron",
                "hour": 15,
                "minute": 30
            },
            "config": {}
        }
        
        logger.info(f"测试创建任务配置: {job_config}")
        
        # 创建任务
        job_id = await service.create_job(job_config)
        
        # 清理测试任务
        await service.remove_job(job_id)
        
        return BaseResponse(
            success=True, 
            message="测试任务创建成功", 
            data={
                "job_id": job_id,
                "task_id": test_task['task_id'],
                "available_tasks": [t['task_id'] for t in tasks]
            }
        )
    except Exception as e:
        logger.error(f"测试创建任务失败: {e}")
        return BaseResponse(success=False, message=f"测试失败: {str(e)}")


@router.get("/status", response_model=BaseResponse)
async def get_scheduler_status():
    """获取调度器状态"""
    try:
        service = get_scheduler_service()
        status = {
            "scheduler_running": service.scheduler.running,
            "job_count": len(service.get_jobs()),
            "plugin_count": len(service.get_plugins()),
            "task_count": len(service.get_tasks()),
            "timestamp": datetime.now().isoformat()
        }
        return BaseResponse(success=True, message="获取调度器状态成功", data=status)
    except Exception as e:
        logger.error(f"获取调度器状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plugins", response_model=BaseResponse)
async def get_plugins():
    """获取所有插件"""
    try:
        service = get_scheduler_service()
        try:
            plugins = service.get_plugins()
            if not isinstance(plugins, list):
                logger.error(f"[DEBUG] get_plugins() 返回非list: {plugins}，类型: {type(plugins)}，自动转为[]")
                plugins = []
        except Exception as e:
            logger.error(f"[DEBUG] get_plugins() 抛出异常: {e}")
            plugins = []
        return BaseResponse(success=True, message="获取插件列表成功", data={"plugins": plugins})
    except Exception as e:
        logger.error(f"获取插件列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks")
async def get_tasks():
    """获取所有任务定义"""
    try:
        service = get_scheduler_service()
        
        tasks = service.get_tasks()
        
        if tasks is None:
            logger.warning("[DEBUG] get_tasks()返回None，使用空列表")
            tasks = []
        elif not isinstance(tasks, list):
            logger.warning(f"[DEBUG] get_tasks()返回非list类型: {type(tasks)}，转换为空列表")
            tasks = []
            
        return {"success": True, "message": "获取任务列表成功", "data": {"tasks": tasks}}
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        logger.error(f"[DEBUG] 异常类型: {type(e)}")
        logger.error(f"[DEBUG] 异常详情: {str(e)}")
        import traceback
        logger.error(f"[DEBUG] 异常堆栈: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=BaseResponse)
async def get_jobs():
    """获取所有定时任务"""
    try:
        service = get_scheduler_service()
        try:
            jobs = service.get_jobs()
            # 只保留异常日志
            if not isinstance(jobs, list):
                logger.error(f"[DEBUG] get_jobs() 返回非list: {jobs}，类型: {type(jobs)}，自动转为[]")
                jobs = []
        except Exception as e:
            logger.error(f"[DEBUG] get_jobs() 抛出异常: {e}")
            jobs = []
        return BaseResponse(success=True, message="获取任务列表成功", data={"jobs": jobs})
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs", response_model=BaseResponse)
async def create_job(job_config: Dict[str, Any]):
    """创建定时任务"""
    try:
        service = get_scheduler_service()
        job_id = await service.create_job(job_config)
        return BaseResponse(success=True, message="任务创建成功", data={"job_id": job_id})
    except Exception as e:
        logger.error(f"创建任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{task_id}/execute", response_model=BaseResponse)
async def execute_task_now(task_id: str, config: Dict[str, Any] = None):
    """立即执行任务"""
    try:
        service = get_scheduler_service()
        result = await service.execute_task_now(task_id, config or {})
        
        if result.success:
            return BaseResponse(success=True, message="任务执行成功", data=result.to_dict())
        else:
            return BaseResponse(success=False, message=f"任务执行失败: {result.error}", data=result.to_dict())
    except Exception as e:
        logger.error(f"执行任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/jobs/{job_id}", response_model=BaseResponse)
async def remove_job(job_id: str):
    """移除定时任务"""
    try:
        service = get_scheduler_service()
        success = await service.remove_job(job_id)
        
        if success:
            return BaseResponse(success=True, message="任务移除成功")
        else:
            return BaseResponse(success=False, message="任务移除失败")
    except Exception as e:
        logger.error(f"移除任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{job_id}/pause", response_model=BaseResponse)
async def pause_job(job_id: str):
    """暂停定时任务"""
    try:
        service = get_scheduler_service()
        success = await service.pause_job(job_id)
        
        if success:
            return BaseResponse(success=True, message="任务暂停成功")
        else:
            return BaseResponse(success=False, message="任务暂停失败")
    except Exception as e:
        logger.error(f"暂停任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{job_id}/resume", response_model=BaseResponse)
async def resume_job(job_id: str):
    """恢复定时任务"""
    try:
        service = get_scheduler_service()
        success = await service.resume_job(job_id)
        
        if success:
            return BaseResponse(success=True, message="任务恢复成功")
        else:
            return BaseResponse(success=False, message="任务恢复失败")
    except Exception as e:
        logger.error(f"恢复任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events", response_model=BaseResponse)
async def get_events(
    event_type: Optional[str] = Query(None, description="事件类型"),
    limit: int = Query(100, description="返回数量限制")
):
    """获取事件历史"""
    try:
        service = get_scheduler_service()
        events = service.event_bus.get_event_history(event_type, limit)
        return BaseResponse(success=True, message="获取事件历史成功", data={"events": events if events else []})
    except Exception as e:
        logger.error(f"获取事件历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize", response_model=BaseResponse)
async def initialize_scheduler():
    """初始化调度器"""
    try:
        service = get_scheduler_service()
        await service.initialize()
        return BaseResponse(success=True, message="调度器初始化成功")
    except Exception as e:
        logger.error(f"调度器初始化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shutdown", response_model=BaseResponse)
async def shutdown_scheduler():
    """关闭调度器"""
    try:
        service = get_scheduler_service()
        await service.shutdown()
        return BaseResponse(success=True, message="调度器关闭成功")
    except Exception as e:
        logger.error(f"调度器关闭失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 