"""
事件总线系统
"""
import asyncio
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
import json
from loguru import logger


class EventBus:
    """事件总线"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[Dict[str, Any]] = []
        self._max_history = 1000  # 最大历史记录数
        
    async def publish(self, event_type: str, event_data: Dict[str, Any] = None):
        """发布事件"""
        event = {
            "type": event_type,
            "data": event_data or {},
            "timestamp": datetime.now().isoformat(),
            "id": f"{event_type}_{datetime.now().timestamp()}"
        }
        
        # 记录事件历史
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
            
        # 通知订阅者
        if event_type in self._subscribers:
            tasks = []
            for callback in self._subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        tasks.append(callback(event))
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"事件处理失败: {event_type}, 错误: {e}")
                    
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        logger.debug(f"事件已发布: {event_type}")
        
    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"事件订阅: {event_type}")
        
    def unsubscribe(self, event_type: str, callback: Callable):
        """取消订阅"""
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
                logger.debug(f"事件取消订阅: {event_type}")
            except ValueError:
                pass
                
    def get_event_history(self, event_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取事件历史"""
        if event_type:
            filtered_events = [e for e in self._event_history if e["type"] == event_type]
            return filtered_events[-limit:]
        return self._event_history[-limit:]
        
    def get_subscribers(self, event_type: str = None) -> Dict[str, int]:
        """获取订阅者信息"""
        if event_type:
            return {event_type: len(self._subscribers.get(event_type, []))}
        return {k: len(v) for k, v in self._subscribers.items()}
        
    def clear_history(self):
        """清空事件历史"""
        self._event_history.clear() 