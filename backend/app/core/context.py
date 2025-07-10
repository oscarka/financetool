"""
任务执行上下文和结果类
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from loguru import logger


class TaskContext:
    """任务执行上下文"""
    
    def __init__(self, job_id: str, execution_id: str, config: Dict[str, Any]):
        self.job_id = job_id
        self.execution_id = execution_id
        self.config = config
        self.variables = {}  # 运行时变量
        self.event_bus = None
        self.storage = None
        self.logger = logger
        self.start_time = datetime.now()
        
    def set_variable(self, key: str, value: Any):
        """设置运行时变量"""
        self.variables[key] = value
        
    def get_variable(self, key: str, default: Any = None) -> Any:
        """获取运行时变量"""
        return self.variables.get(key, default)
        
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置参数"""
        return self.config.get(key, default)
        
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        if hasattr(self.logger, level.lower()):
            getattr(self.logger, level.lower())(f"[{self.job_id}] {message}")


class TaskResult:
    """任务执行结果"""
    
    def __init__(self, success: bool = True, data: Dict[str, Any] = None, 
                 error: Optional[str] = None, events: List[str] = None, 
                 next_tasks: List[str] = None):
        self.success = success
        self.data = data or {}
        self.error = error
        self.events = events or []
        self.next_tasks = next_tasks or []
        self.timestamp = datetime.now()
        
    def add_event(self, event_type: str, event_data: Dict[str, Any] = None):
        """添加事件"""
        event = {
            "type": event_type,
            "data": event_data or {},
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        
    def add_next_task(self, task_id: str, condition: str = "always"):
        """添加下一步任务"""
        self.next_tasks.append({
            "task_id": task_id,
            "condition": condition
        })
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "events": self.events,
            "next_tasks": self.next_tasks,
            "timestamp": self.timestamp.isoformat()
        } 