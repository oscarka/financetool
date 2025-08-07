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
        # 确保时区设置正确
        import pytz
        timezone = pytz.timezone(settings.scheduler_timezone)
        
        self.scheduler = AsyncIOScheduler(
            timezone=timezone,
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
        """初始化调度器，并从配置文件加载任务"""
        import os
        import json
        try:
            # 添加时区调试信息
            import pytz
            from datetime import datetime
            
            logger.info("=== 调度器初始化时区调试 ===")
            logger.info(f"调度器时区设置: {settings.scheduler_timezone}")
            logger.info(f"系统当前时间: {datetime.now()}")
            logger.info(f"系统UTC时间: {datetime.utcnow()}")
            logger.info(f"调度器时区对象: {self.scheduler.timezone}")
            logger.info("=== 调度器初始化时区调试结束 ===")
            
            # 加载插件
            await self._load_plugins()

            # ===== 新增：加载调度任务配置文件 =====
            config_path = os.path.join(os.path.dirname(__file__), '../config/scheduler_tasks.json')
            config_path = os.path.abspath(config_path)
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                all_tasks = self.plugin_manager.get_tasks()
                all_task_ids = {t['task_id']: t for t in all_tasks}
                for task in tasks:
                    if not task.get('enabled', True):
                        continue
                    # plugin路径转task_id（假设plugin_manager注册时task_id就是文件名）
                    plugin_path = task['plugin']
                    task_id = plugin_path.split('.')[-1]  # 例如 web3_balance_sync
                    if task_id not in all_task_ids:
                        logger.warning(f"调度任务配置中指定的task_id {task_id} 不存在于插件注册任务列表中，已跳过")
                        continue
                    # 解析cron表达式
                    cron_expr = task['cron']
                    try:
                        from apscheduler.triggers.cron import CronTrigger
                        cron_fields = cron_expr.strip().split()
                        
                        # 添加cron解析调试信息
                        logger.info(f"=== Cron表达式调试: {task['id']} ===")
                        logger.info(f"Cron表达式: {cron_expr}")
                        logger.info(f"Cron字段: {cron_fields}")
                        
                        if len(cron_fields) == 5:
                            trigger = CronTrigger(
                                minute=cron_fields[0], 
                                hour=cron_fields[1], 
                                day=cron_fields[2], 
                                month=cron_fields[3], 
                                day_of_week=cron_fields[4],
                                timezone=self.scheduler.timezone  # 明确设置时区
                            )
                        elif len(cron_fields) == 6:
                            trigger = CronTrigger(
                                second=cron_fields[0], 
                                minute=cron_fields[1], 
                                hour=cron_fields[2], 
                                day=cron_fields[3], 
                                month=cron_fields[4], 
                                day_of_week=cron_fields[5],
                                timezone=self.scheduler.timezone  # 明确设置时区
                            )
                        else:
                            logger.error(f"无效的cron表达式: {cron_expr}")
                            continue
                        
                        logger.info(f"创建的触发器: {trigger}")
                        logger.info(f"触发器时区: {trigger.timezone}")
                        logger.info("=== Cron表达式调试结束 ===")
                        
                    except Exception as e:
                        logger.error(f"解析cron表达式失败: {cron_expr}, 错误: {e}")
                        continue
                    # 注册任务
                    self.scheduler.add_job(
                        func=self._execute_task_wrapper,
                        trigger=trigger,
                        args=[task_id, task.get('args', {})],
                        id=task['id'],
                        name=task.get('name', task_id),
                        replace_existing=True
                    )
                    logger.info(f"已注册调度任务: {task['id']} ({task.get('name', task_id)}) [{cron_expr}]")
            else:
                logger.warning(f"未找到调度任务配置文件: {config_path}")
            # ===== 结束 =====

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
            # 检查任务状态 - 暂停的任务next_run_time为None
            state = 'running'  # 默认状态
            if job.next_run_time is None:
                state = 'paused'
            elif job.next_run_time:
                state = 'running'
            
            # 添加调试信息
            logger.info(f"任务调试信息: {job.id}")
            logger.info(f"  - 名称: {job.name}")
            logger.info(f"  - 触发器: {job.trigger}")
            logger.info(f"  - 下次执行时间: {job.next_run_time}")
            logger.info(f"  - 状态: {state}")
            
            # 特别关注定投任务
            if 'dca' in job.id.lower() or '定投' in job.name:
                logger.info(f"*** 定投任务详细信息 ***")
                logger.info(f"  - 任务ID: {job.id}")
                logger.info(f"  - 任务名称: {job.name}")
                logger.info(f"  - 触发器原始配置: {job.trigger}")
                logger.info(f"  - 下次执行时间: {job.next_run_time}")
                logger.info(f"  - 时区: {job.next_run_time.tzinfo if job.next_run_time else 'None'}")
                logger.info(f"  - 状态: {state}")
                logger.info(f"*** 定投任务信息结束 ***")
                
            # APScheduler已经返回了正确的时区感知时间，直接使用
            next_run_time = None
            if job.next_run_time:
                # 添加简化的调试信息
                logger.info(f"=== 时区调试信息: {job.id} ===")
                logger.info(f"APScheduler原始时间: {job.next_run_time}")
                logger.info(f"APScheduler原始时间类型: {type(job.next_run_time)}")
                logger.info(f"APScheduler原始时间时区: {job.next_run_time.tzinfo}")
                
                # 直接使用APScheduler的时间，不做任何转换
                next_run_time = job.next_run_time.isoformat()
                logger.info(f"最终ISO格式: {next_run_time}")
                logger.info(f"=== 时区调试信息结束 ===")
            
            jobs.append({
                'job_id': job.id,
                'name': job.name,
                'next_run_time': next_run_time,
                'trigger': str(job.trigger),
                'state': state
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
        logger.info(f"🔍 收到基金净值更新事件: {event}")
        logger.info(f"基金净值已更新: {event['data']['updated_count']} 个基金")
        
        # 后续操作：更新待确认的操作记录
        try:
            from app.utils.database import get_db
            from app.services.fund_service import DCAService, FundOperationService
            
            logger.info("🔍 开始更新待确认操作...")
            db = next(get_db())
            try:
                # 更新定投相关的待确认操作
                dca_updated = DCAService.update_pending_operations(db)
                logger.info(f"✅ 更新了 {dca_updated} 个定投待确认操作")
                
                # 更新所有待确认操作
                nav_updated = FundOperationService.update_pending_operations(db)
                logger.info(f"✅ 更新了 {nav_updated} 个待确认操作")
                
                # 提交数据库事务
                db.commit()
                logger.info("✅ 待确认操作更新完成")
                
            except Exception as e:
                logger.error(f"❌ 更新待确认操作失败: {e}")
                db.rollback()
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ 处理基金净值更新后续操作失败: {e}")
        
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