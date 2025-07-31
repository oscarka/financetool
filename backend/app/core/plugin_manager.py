"""
插件管理器
"""
import importlib
import inspect
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
import asyncio
from loguru import logger

from .base_plugin import BaseTaskPlugin, BaseTask
from .context import TaskContext, TaskResult


class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self._plugins: Dict[str, BaseTaskPlugin] = {}
        self._tasks: Dict[str, Type[BaseTask]] = {}
        self._task_registry: Dict[str, Dict[str, Any]] = {}
        
    async def load_plugin(self, plugin_path: str) -> bool:
        """加载插件"""
        try:
            # 动态导入插件模块
            module = importlib.import_module(plugin_path)
            
            # 查找插件类
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseTaskPlugin) and 
                    obj != BaseTaskPlugin):
                    plugin_class = obj
                    break
                    
            if not plugin_class:
                logger.error(f"插件模块 {plugin_path} 中未找到有效的插件类")
                return False
                
            # 实例化插件
            plugin = plugin_class()
            
            # 初始化插件
            if not await plugin.initialize():
                logger.error(f"插件 {plugin.plugin_id} 初始化失败")
                return False
                
            # 注册插件
            self._plugins[plugin.plugin_id] = plugin
            
            # 注册任务
            task_definitions = await plugin.register_tasks()
            for task_def in task_definitions:
                await self._register_task(task_def, plugin)
                
            logger.info(f"插件 {plugin.plugin_id} 加载成功")  # 保留插件加载成功日志
            return True
            
        except Exception as e:
            logger.error(f"加载插件 {plugin_path} 失败: {e}")
            return False
            
    async def _register_task(self, task_def: Dict[str, Any], plugin: BaseTaskPlugin):
        """注册任务"""
        task_id = task_def["task_id"]
        task_class_path = task_def["class"]
        
        try:
            # 动态导入任务类
            module_path, class_name = task_class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            task_class = getattr(module, class_name)
            
            # 验证任务类
            if not (inspect.isclass(task_class) and issubclass(task_class, BaseTask)):
                logger.error(f"任务类 {task_class_path} 不是有效的任务类")
                return
                
            # 注册任务
            self._tasks[task_id] = task_class
            self._task_registry[task_id] = {
                "plugin_id": plugin.plugin_id,
                "name": task_def["name"],
                "description": task_def.get("description", ""),
                "class_path": task_class_path
            }
            
            # logger.debug(f"任务 {task_id} 注册成功")  # 精简日志，去掉任务注册成功的DEBUG日志
            
        except Exception as e:
            logger.error(f"注册任务 {task_id} 失败: {e}")
            
    async def create_task_instance(self, task_id: str, config: Dict[str, Any]) -> Optional[BaseTask]:
        """创建任务实例"""
        if task_id not in self._tasks:
            logger.error(f"任务 {task_id} 未注册")
            return None
            
        try:
            task_class = self._tasks[task_id]
            task_info = self._task_registry[task_id]
            
            # 创建任务实例
            task = task_class(
                task_id=task_id,
                name=task_info["name"],
                description=task_info["description"]
            )
            
            # 如果配置为空，使用默认配置
            if not config:
                default_config = self._get_default_config(task_id)
                if default_config:
                    logger.info(f"任务 {task_id} 使用默认配置: {default_config}")
                    config = default_config
                else:
                    logger.warning(f"任务 {task_id} 无默认配置")
            
            # 验证配置
            if not await task.validate_config(config):
                logger.error(f"任务 {task_id} 配置验证失败")
                return None
                
            return task
            
        except Exception as e:
            logger.error(f"创建任务实例 {task_id} 失败: {e}")
            return None
            
    def _get_default_config(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务的默认配置"""
        # 从配置文件读取默认配置
        try:
            import json
            import os
            from pathlib import Path
            
            config_path = Path(__file__).parent.parent / "config" / "scheduler_tasks.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    tasks_config = json.load(f)
                    
                for task_config in tasks_config:
                    if task_config.get("id") == task_id:
                        return task_config.get("args", {})
                        
        except Exception as e:
            logger.error(f"读取任务 {task_id} 默认配置失败: {e}")
            
        return None
            
    async def execute_task(self, task_id: str, execution_id: str, 
                          config: Dict[str, Any]) -> TaskResult:
        """执行任务"""
        try:
            # 创建任务实例（可能会更新配置为默认配置）
            task = await self.create_task_instance(task_id, config)
            if not task:
                return TaskResult(success=False, error=f"任务 {task_id} 创建失败")
                
            # 如果配置被更新为默认配置，重新获取
            if not config and task_id in self._task_registry:
                default_config = self._get_default_config(task_id)
                if default_config:
                    config = default_config
                
            # 创建执行上下文
            context = TaskContext(task_id, execution_id, config)
            
            # 设置事件总线（从调度器服务获取）
            from app.services.extensible_scheduler_service import get_scheduler_service
            scheduler_service = get_scheduler_service()
            context.event_bus = scheduler_service.event_bus
            
            # 执行任务
            result = await task.execute(context)
            
            logger.info(f"任务 {task_id} 执行完成: {'成功' if result.success else '失败'}")
            return result
            
        except Exception as e:
            logger.error(f"执行任务 {task_id} 失败: {e}")
            return TaskResult(success=False, error=str(e))
            
    def get_plugins(self) -> List[Dict[str, Any]]:
        """获取所有插件信息"""
        plugins = []
        for plugin_id, plugin in self._plugins.items():
            plugins.append({
                "plugin_id": plugin_id,
                "plugin_name": plugin.plugin_name,
                "version": plugin.version,
                "description": plugin.description,
                "author": plugin.author
            })
        return plugins
        
    def get_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务信息"""
        tasks = []
        for task_id, task_info in self._task_registry.items():
            tasks.append({
                "task_id": task_id,
                "name": task_info["name"],
                "description": task_info["description"],
                "plugin_id": task_info["plugin_id"]
            })
        return tasks
        
    async def unload_plugin(self, plugin_id: str) -> bool:
        """卸载插件"""
        if plugin_id not in self._plugins:
            return False
            
        try:
            plugin = self._plugins[plugin_id]
            
            # 清理插件
            await plugin.cleanup()
            
            # 移除相关任务
            tasks_to_remove = [task_id for task_id, info in self._task_registry.items() 
                             if info["plugin_id"] == plugin_id]
            for task_id in tasks_to_remove:
                self._tasks.pop(task_id, None)
                self._task_registry.pop(task_id, None)
                
            # 移除插件
            self._plugins.pop(plugin_id)
            
            logger.info(f"插件 {plugin_id} 卸载成功")
            return True
            
        except Exception as e:
            logger.error(f"卸载插件 {plugin_id} 失败: {e}")
            return False 