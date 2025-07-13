from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from .context import TaskContext


class BaseTask(ABC):
    """基础任务类"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.enabled = True
        self.last_run = None
        self.next_run = None
        self.run_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.last_error = None
        self.avg_duration = 0.0
        
    @abstractmethod
    async def execute(self, context: TaskContext) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            context: 任务上下文
            
        Returns:
            执行结果
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """获取任务状态"""
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "run_count": self.run_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": (self.success_count / self.run_count * 100) if self.run_count > 0 else 0,
            "last_error": self.last_error,
            "avg_duration": self.avg_duration
        }
    
    def update_stats(self, success: bool, duration: float, error: Optional[str] = None):
        """更新任务统计信息"""
        self.run_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
            self.last_error = error
        
        # 更新平均执行时间
        if self.avg_duration == 0:
            self.avg_duration = duration
        else:
            self.avg_duration = (self.avg_duration + duration) / 2
        
        self.last_run = datetime.now()
    
    def enable(self):
        """启用任务"""
        self.enabled = True
        logger.info(f"任务 {self.name} 已启用")
    
    def disable(self):
        """禁用任务"""
        self.enabled = False
        logger.info(f"任务 {self.name} 已禁用")
    
    def reset_stats(self):
        """重置统计信息"""
        self.run_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.last_error = None
        self.avg_duration = 0.0
        self.last_run = None
        self.next_run = None
        logger.info(f"任务 {self.name} 统计信息已重置")


class SimpleTask(BaseTask):
    """简单任务类，用于快速创建任务"""
    
    def __init__(self, name: str, func, description: str = ""):
        super().__init__(name, description)
        self.func = func
    
    async def execute(self, context: TaskContext) -> Dict[str, Any]:
        """执行简单任务"""
        try:
            start_time = datetime.now()
            
            if asyncio.iscoroutinefunction(self.func):
                result = await self.func(context)
            else:
                result = self.func(context)
            
            duration = (datetime.now() - start_time).total_seconds()
            self.update_stats(True, duration)
            
            return {
                "success": True,
                "result": result,
                "duration": duration
            }
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.update_stats(False, duration, str(e))
            
            logger.error(f"任务 {self.name} 执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration": duration
            }


class RetryableTask(BaseTask):
    """可重试任务类"""
    
    def __init__(self, name: str, description: str = "", max_retries: int = 3, retry_delay: float = 1.0):
        super().__init__(name, description)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def execute(self, context: TaskContext) -> Dict[str, Any]:
        """执行可重试任务"""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                start_time = datetime.now()
                result = await self._execute_impl(context)
                duration = (datetime.now() - start_time).total_seconds()
                
                self.update_stats(True, duration)
                return {
                    "success": True,
                    "result": result,
                    "duration": duration,
                    "attempts": attempt + 1
                }
            except Exception as e:
                last_error = e
                duration = (datetime.now() - start_time).total_seconds()
                
                if attempt < self.max_retries:
                    logger.warning(f"任务 {self.name} 第 {attempt + 1} 次尝试失败: {e}, {self.retry_delay}秒后重试")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"任务 {self.name} 执行失败，已重试 {self.max_retries} 次: {e}")
                    self.update_stats(False, duration, str(e))
                    return {
                        "success": False,
                        "error": str(e),
                        "duration": duration,
                        "attempts": attempt + 1
                    }
    
    @abstractmethod
    async def _execute_impl(self, context: TaskContext) -> Any:
        """实际执行逻辑"""
        pass


# 导入asyncio模块
import asyncio 