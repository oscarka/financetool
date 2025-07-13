"""
插件基类定义
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .context import TaskContext, TaskResult


class BaseTaskPlugin(ABC):
    """任务插件基类"""
    
    def __init__(self):
        self.plugin_id = None
        self.plugin_name = None
        self.version = None
        self.description = None
        self.config_schema = None  # JSON Schema
        self.author = None
        
    @abstractmethod
    async def register_tasks(self) -> List[Dict[str, Any]]:
        """注册任务，返回任务定义列表"""
        pass
        
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # 默认实现：如果有schema则验证，否则返回True
        if self.config_schema:
            # TODO: 实现JSON Schema验证
            pass
        return True
        
    async def get_status(self) -> Dict[str, Any]:
        """获取插件状态"""
        return {
            "plugin_id": self.plugin_id,
            "plugin_name": self.plugin_name,
            "version": self.version,
            "status": "active"
        }
        
    async def initialize(self) -> bool:
        """插件初始化"""
        return True
        
    async def cleanup(self) -> bool:
        """插件清理"""
        return True


class BaseTask(ABC):
    """任务基类"""
    
    def __init__(self, task_id: str, name: str, description: str = ""):
        self.task_id = task_id
        self.name = name
        self.description = description
        
    @abstractmethod
    async def execute(self, context: TaskContext) -> TaskResult:
        """执行任务"""
        pass
        
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证任务配置"""
        return True
        
    def get_task_info(self) -> Dict[str, Any]:
        """获取任务信息"""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description
        } 