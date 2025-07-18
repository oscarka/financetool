"""
可扩展定时任务调度器服务
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from loguru import logger

from app.core.plugin_manager import PluginManager
from app.core.event_bus import EventBus
from app.core.context import TaskContext, TaskResult
from app.settings import settings


class ExtensibleSchedulerService:
    """可扩展定时任务调度器服务"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            timezone=settings.scheduler_timezone,
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 300  # 5分钟宽限期
            }
        )
        self.plugin_manager = PluginManager()
        self.event_bus = EventBus()
        self._setup_event_handlers()
            
    def _setup_event_handlers(self):
        """设置事件处理器"""
        # 任务完成事件处理
        self.event_bus.subscribe('task.completed', self._handle_task_completed)
        self.event_bus.subscribe('task.failed', self._handle_task_failed)
        
        # 业务事件处理
        self.event_bus.subscribe('fund.nav.updated', self._handle_fund_nav_updated)
        self.event_bus.subscribe('wise.balance.synced', self._handle_wise_balance_synced)
        self.event_bus.subscribe('okx.balance.synced', self._handle_okx_balance_synced)
        self.event_bus.subscribe('ibkr.balance.synced', self._handle_ibkr_balance_synced)
        self.event_bus.subscribe('web3.balance.synced', self._handle_web3_balance_synced)
        
    async def initialize(self):
        """初始化调度器"""
        try:
            # 加载插件
            await self._load_plugins()
            
            # 启动调度器
            self.scheduler.start()
            
            # 启动事件总线
            logger.info("可扩展调度器初始化完成")
            
        except Exception as e:
            logger.error(f"可扩展调度器初始化失败: {e}")
            raise
            
    async def _load_plugins(self):
        """加载插件"""
        # 加载金融操作插件
        await self.plugin_manager.load_plugin('app.plugins.financial_operations.plugin')
        
        # 可以在这里加载更多插件
        # await self.plugin_manager.load_plugin('app.plugins.custom_plugin')
        
        logger.info(f"已加载 {len(self.plugin_manager.get_plugins())} 个插件")
        
    async def create_job(self, job_config: Dict[str, Any]) -> str:
        """创建定时任务"""
        try:
            job_id = job_config.get('job_id') or f"job_{uuid.uuid4().hex[:8]}"
            task_id = job_config['task_id']
            schedule_config = job_config['schedule']
            config = job_config.get('config', {})

            logger.info(f"[DEBUG] create_job 收到配置: {job_config}")
            
            # 获取所有可用任务
            all_tasks = self.plugin_manager.get_tasks()
            logger.info(f"[DEBUG] 当前可用任务ID: {[t['task_id'] for t in all_tasks]}")
            
            # 验证任务是否存在
            if task_id not in [t['task_id'] for t in all_tasks]:
                raise ValueError(f"任务 {task_id} 不存在")

            # 只保留有值的调度参数，防止 None 传入 APScheduler
            schedule_type = schedule_config.get('type')
            schedule_args = {k: v for k, v in schedule_config.items() if v is not None and k != 'type'}
            
            logger.info(f"[DEBUG] 调度配置: type={schedule_type}, args={schedule_args}")

            if schedule_type == 'interval':
                from apscheduler.triggers.interval import IntervalTrigger
                trigger = IntervalTrigger(**schedule_args)
            elif schedule_type == 'cron':
                from apscheduler.triggers.cron import CronTrigger
                trigger = CronTrigger(**schedule_args)
            else:
                raise ValueError(f"不支持的调度类型: {schedule_type}")

            # 添加任务到调度器
            self.scheduler.add_job(
                func=self._execute_task_wrapper,
                trigger=trigger,
                args=[task_id, config],
                id=job_id,
                name=job_config.get('name', task_id),
                replace_existing=True
            )
            
            logger.info(f"任务 {job_id} 创建成功")
            return job_id
            
        except Exception as e:
            logger.error(f"创建任务失败: {e}")
            raise
            
    def _create_trigger(self, schedule_config: Dict[str, Any]):
        """创建触发器"""
        schedule_type = schedule_config['type']
        
        if schedule_type == 'cron':
            return CronTrigger(
                year=schedule_config.get('year'),
                month=schedule_config.get('month'),
                day=schedule_config.get('day'),
                week=schedule_config.get('week'),
                day_of_week=schedule_config.get('day_of_week'),
                hour=schedule_config.get('hour'),
                minute=schedule_config.get('minute'),
                second=schedule_config.get('second')
            )
        elif schedule_type == 'interval':
            return IntervalTrigger(
                seconds=schedule_config.get('seconds'),
                minutes=schedule_config.get('minutes'),
                hours=schedule_config.get('hours'),
                days=schedule_config.get('days')
            )
        elif schedule_type == 'date':
            return DateTrigger(
                run_date=schedule_config['run_date']
            )
        else:
            raise ValueError(f"不支持的调度类型: {schedule_type}")
            
    async def _execute_task_wrapper(self, task_id: str, config: Dict[str, Any]):
        """任务执行包装器"""
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        
        try:
            # 发布任务开始事件
            await self.event_bus.publish('task.started', {
                'task_id': task_id,
                'execution_id': execution_id,
                'config': config
            })
            
            # 执行任务
            result = await self.plugin_manager.execute_task(task_id, execution_id, config)
            
            # 设置事件总线到结果中
            result.event_bus = self.event_bus
            
            # 发布任务完成事件
            if result.success:
                await self.event_bus.publish('task.completed', {
                    'task_id': task_id,
                    'execution_id': execution_id,
                    'result': result.to_dict()
                })
            else:
                await self.event_bus.publish('task.failed', {
                    'task_id': task_id,
                    'execution_id': execution_id,
                    'error': result.error
                })
                
        except Exception as e:
            logger.error(f"任务执行异常: {task_id}, 错误: {e}")
            await self.event_bus.publish('task.failed', {
                'task_id': task_id,
                'execution_id': execution_id,
                'error': str(e)
            })
            
    async def execute_task_now(self, task_id: str, config: Dict[str, Any] = None) -> TaskResult:
        """立即执行任务"""
        execution_id = f"manual_{uuid.uuid4().hex[:8]}"
        config = config or {}
        
        try:
            logger.info(f"手动执行任务: {task_id}")
            result = await self.plugin_manager.execute_task(task_id, execution_id, config)
            return result
        except Exception as e:
            logger.error(f"手动执行任务失败: {task_id}, 错误: {e}")
            return TaskResult(success=False, error=str(e))
            
    def get_jobs(self) -> List[Dict[str, Any]]:
        """获取所有任务"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'job_id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs
        
    def get_plugins(self) -> List[Dict[str, Any]]:
        """获取所有插件"""
        return self.plugin_manager.get_plugins()
        
    def get_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务定义"""
        return self.plugin_manager.get_tasks()
        
    def _job_exists(self, job_id: str) -> bool:
        return self.scheduler.get_job(job_id) is not None

    async def remove_job(self, job_id: str) -> bool:
        """移除任务"""
        try:
            if not self._job_exists(job_id):
                logger.error(f"移除任务失败: {job_id} 不存在")
                return False
            self.scheduler.remove_job(job_id)
            logger.info(f"任务 {job_id} 已移除")
            return True
        except Exception as e:
            logger.error(f"移除任务失败: {job_id}, 错误: {e}")
            return False
            
    async def pause_job(self, job_id: str) -> bool:
        """暂停任务"""
        try:
            if not self._job_exists(job_id):
                logger.error(f"暂停任务失败: {job_id} 不存在")
                return False
            self.scheduler.pause_job(job_id)
            logger.info(f"任务 {job_id} 已暂停")
            return True
        except Exception as e:
            logger.error(f"暂停任务失败: {job_id}, 错误: {e}")
            return False
            
    async def resume_job(self, job_id: str) -> bool:
        """恢复任务"""
        try:
            if not self._job_exists(job_id):
                logger.error(f"恢复任务失败: {job_id} 不存在")
                return False
            self.scheduler.resume_job(job_id)
            logger.info(f"任务 {job_id} 已恢复")
            return True
        except Exception as e:
            logger.error(f"恢复任务失败: {job_id}, 错误: {e}")
            return False
            
    # 事件处理方法
    async def _handle_task_completed(self, event: Dict[str, Any]):
        """处理任务完成事件"""
        logger.info(f"任务完成: {event['task_id']}")
        
    async def _handle_task_failed(self, event: Dict[str, Any]):
        """处理任务失败事件"""
        logger.error(f"任务失败: {event['task_id']}, 错误: {event['error']}")
        
    async def _handle_fund_nav_updated(self, event: Dict[str, Any]):
        """处理基金净值更新事件"""
        logger.info(f"基金净值已更新: {event['data']['updated_count']} 个基金")
        
    async def _handle_wise_balance_synced(self, event: Dict[str, Any]):
        """处理Wise余额同步事件"""
        logger.info(f"Wise余额已同步: {event['data']['account_count']} 个账户")
        
    async def _handle_okx_balance_synced(self, event: Dict[str, Any]):
        """处理OKX余额同步事件"""
        logger.info(f"OKX余额已同步: {event['data']['currency_count']} 个币种")
        
    async def _handle_ibkr_balance_synced(self, event: Dict[str, Any]):
        """处理IBKR余额同步事件"""
        logger.info(f"IBKR余额已同步: {event['data']['account_count']} 个账户")
        
    async def _handle_web3_balance_synced(self, event: Dict[str, Any]):
        """处理Web3余额同步事件"""
        logger.info(f"Web3余额已同步: 总余额 {event['data']['total_balance']}")
        
    async def shutdown(self):
        """关闭调度器"""
        try:
            self.scheduler.shutdown()
            logger.info("可扩展调度器已关闭")
        except Exception as e:
            logger.error(f"关闭调度器失败: {e}") 