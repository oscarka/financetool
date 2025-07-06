import logging
from datetime import datetime, time
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.services.fund_service import FundOperationService, DCAService
from app.services.fund_api_service import FundAPIService
from app.services.wise_api_service import WiseAPIService
from app.config import settings

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务服务类"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            timezone=settings.scheduler_timezone,
            job_defaults={
                'coalesce': True,
                'max_instances': 1
            }
        )
        self._setup_jobs()
    
    def _setup_jobs(self):
        """设置定时任务"""
        # 净值更新任务 - 每天15:30执行
        self.scheduler.add_job(
            self._update_fund_navs,
            CronTrigger(hour=15, minute=30),
            id='update_fund_navs',
            name='更新基金净值',
            replace_existing=True
        )
        
        # 定投计划执行任务 - 每天15:45执行
        self.scheduler.add_job(
            self._execute_dca_plans,
            CronTrigger(hour=15, minute=45),
            id='execute_dca_plans',
            name='执行定投计划',
            replace_existing=True
        )
        
        # 更新待确认操作任务 - 每天16:00执行
        self.scheduler.add_job(
            self._update_pending_operations,
            CronTrigger(hour=16, minute=0),
            id='update_pending_operations',
            name='更新待确认操作',
            replace_existing=True
        )
        
        # 更新定投计划状态任务 - 每天16:15执行
        self.scheduler.add_job(
            self._update_plan_statuses,
            CronTrigger(hour=16, minute=15),
            id='update_plan_statuses',
            name='更新定投计划状态',
            replace_existing=True
        )
        
        # Wise数据同步任务 - 每天16:30执行
        self.scheduler.add_job(
            self._sync_wise_data,
            CronTrigger(hour=16, minute=30),
            id='sync_wise_data',
            name='同步Wise数据',
            replace_existing=True
        )
    
    async def _update_fund_navs(self):
        """更新持仓基金的净值"""
        logger.info("开始执行基金净值更新任务")
        try:
            db = next(get_db())
            
            # 获取所有持仓的基金代码（只更新有持仓的基金）
            positions = FundOperationService.get_fund_positions(db)
            fund_codes = list(set([pos.fund_code for pos in positions if pos.fund_code]))
            
            if not fund_codes:
                logger.info("没有持仓基金，跳过净值更新")
                return
            
            logger.info(f"需要更新净值的基金: {fund_codes}")
            
            updated_count = 0
            for fund_code in fund_codes:
                try:
                    # 获取最新净值
                    api_service = FundAPIService()
                    nav_data = await api_service.get_fund_nav_latest_tiantian(fund_code)
                    if nav_data and nav_data.get('nav'):
                        # 更新或插入净值记录
                        from datetime import date
                        today = date.today()
                        success = FundOperationService.update_fund_nav(
                            db, fund_code, nav_data['nav'], today
                        )
                        if success:
                            updated_count += 1
                            logger.info(f"成功更新基金 {fund_code} 净值: {nav_data['nav']}")
                        else:
                            logger.warning(f"更新基金 {fund_code} 净值失败")
                    else:
                        logger.warning(f"获取基金 {fund_code} 净值失败")
                except Exception as e:
                    logger.error(f"更新基金 {fund_code} 净值时出错: {e}")
            
            logger.info(f"基金净值更新任务完成，成功更新 {updated_count} 个基金")
            
        except Exception as e:
            logger.error(f"基金净值更新任务执行失败: {e}")
        finally:
            db.close()
    
    async def _execute_dca_plans(self):
        """执行定投计划"""
        logger.info("开始执行定投计划任务")
        try:
            db = next(get_db())
            
            # 检查并执行到期的定投计划
            executed_operations = DCAService.check_and_execute_dca_plans(db)
            
            logger.info(f"定投计划执行任务完成，执行了 {len(executed_operations)} 个计划")
            
        except Exception as e:
            logger.error(f"定投计划执行任务失败: {e}")
        finally:
            db.close()
    
    async def _update_pending_operations(self):
        """更新待确认的操作记录"""
        logger.info("开始执行更新待确认操作任务")
        try:
            db = next(get_db())
            
            # 更新所有待确认的定投操作记录
            updated_count = DCAService.update_pending_operations(db)
            
            logger.info(f"更新待确认操作任务完成，更新了 {updated_count} 条记录")
            
        except Exception as e:
            logger.error(f"更新待确认操作任务失败: {e}")
        finally:
            db.close()
    
    async def _update_plan_statuses(self):
        """更新定投计划状态"""
        logger.info("开始执行更新定投计划状态任务")
        try:
            db = next(get_db())
            
            # 批量更新所有定投计划状态
            updated_count = DCAService.update_all_plan_statuses(db)
            
            logger.info(f"更新定投计划状态任务完成，更新了 {updated_count} 个计划")
            
        except Exception as e:
            logger.error(f"更新定投计划状态任务失败: {e}")
        finally:
            db.close()
    
    async def _sync_wise_data(self):
        """同步Wise数据"""
        logger.info("开始执行Wise数据同步任务")
        try:
            # 初始化Wise服务
            wise_service = WiseAPIService()
            
            # 同步账户余额
            balances = await wise_service.get_all_account_balances()
            if balances:
                logger.info(f"成功获取Wise账户余额，共 {len(balances)} 个账户")
                # TODO: 将余额数据保存到数据库
                for balance in balances:
                    logger.debug(f"账户 {balance['account_id']} - {balance['currency']}: {balance['available_balance']}")
            else:
                logger.warning("获取Wise账户余额失败")
            
            # 同步最近交易记录
            transactions = await wise_service.get_recent_transactions(1)  # 获取最近1天的交易
            if transactions:
                logger.info(f"成功获取Wise交易记录，共 {len(transactions)} 条")
                # TODO: 将交易记录保存到数据库
                for transaction in transactions[:5]:  # 只记录前5条
                    logger.debug(f"交易: {transaction['type']} - {transaction['amount']} {transaction['currency']}")
            else:
                logger.info("没有新的Wise交易记录")
            
            # 同步汇率数据
            try:
                rates = await wise_service.get_exchange_rates("USD", "CNY")
                if rates:
                    logger.info("成功获取Wise汇率数据")
                    # TODO: 将汇率数据保存到数据库
                else:
                    logger.warning("获取Wise汇率数据失败")
            except Exception as e:
                logger.error(f"获取Wise汇率数据时出错: {e}")
            
            logger.info("Wise数据同步任务完成")
            
        except Exception as e:
            logger.error(f"Wise数据同步任务执行失败: {e}")
    
    async def start_async(self):
        """异步启动调度器"""
        try:
            # 检查调度器状态并安全停止
            if hasattr(self.scheduler, 'running') and self.scheduler.running:
                logger.info("正在停止运行中的调度器...")
                self.scheduler.shutdown(wait=True)
                logger.info("调度器已停止")
            
            # 重新设置任务
            self._setup_jobs()
            
            # 启动调度器
            self.scheduler.start()
            logger.info("定时任务调度器已启动")
            
        except Exception as e:
            logger.error(f"启动调度器时出错: {e}")
            raise e
    
    async def stop_async(self):
        """异步停止调度器"""
        try:
            if hasattr(self.scheduler, 'running') and self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                logger.info("定时任务调度器已停止")
            else:
                logger.info("调度器未运行，无需停止")
        except Exception as e:
            logger.error(f"停止调度器时出错: {e}")
            raise e
    
    async def restart_async(self):
        """异步重启调度器"""
        try:
            # 检查调度器状态并安全停止
            if hasattr(self.scheduler, 'running') and self.scheduler.running:
                logger.info("正在停止运行中的调度器...")
                self.scheduler.shutdown(wait=True)
                logger.info("调度器已停止")
            
            # 重新初始化调度器
            logger.info("正在重新初始化调度器...")
            self.scheduler = AsyncIOScheduler(
                timezone=settings.scheduler_timezone,
                job_defaults={
                    'coalesce': True,
                    'max_instances': 1
                }
            )
            
            # 重新设置任务
            self._setup_jobs()
            
            # 启动调度器
            self.scheduler.start()
            logger.info("定时任务调度器已重启")
            
        except Exception as e:
            logger.error(f"重启调度器时出错: {e}")
            # 尝试重新初始化
            try:
                self.scheduler = AsyncIOScheduler(
                    timezone=settings.scheduler_timezone,
                    job_defaults={
                        'coalesce': True,
                        'max_instances': 1
                    }
                )
                self._setup_jobs()
                self.scheduler.start()
                logger.info("调度器重新初始化成功")
            except Exception as retry_error:
                logger.error(f"重新初始化调度器失败: {retry_error}")
                raise retry_error
    
    def get_jobs(self) -> List[dict]:
        """获取所有定时任务信息"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs
    
    def update_job_schedule(self, job_id: str, hour: int, minute: int):
        """更新任务执行时间"""
        try:
            self.scheduler.reschedule_job(
                job_id,
                trigger=CronTrigger(hour=hour, minute=minute)
            )
            logger.info(f"任务 {job_id} 执行时间已更新为 {hour:02d}:{minute:02d}")
            return True
        except Exception as e:
            logger.error(f"更新任务 {job_id} 执行时间失败: {e}")
            return False

    def start(self):
        """启动调度器（同步版本）"""
        try:
            # 检查调度器状态并安全停止
            if hasattr(self.scheduler, 'running') and self.scheduler.running:
                logger.info("正在停止运行中的调度器...")
                self.scheduler.shutdown(wait=True)
                logger.info("调度器已停止")
            
            # 重新设置任务
            self._setup_jobs()
            
            # 启动调度器
            self.scheduler.start()
            logger.info("定时任务调度器已启动")
            
        except Exception as e:
            logger.error(f"启动调度器时出错: {e}")
            raise e
    
    def stop(self):
        """停止调度器（同步版本）"""
        try:
            if hasattr(self.scheduler, 'running') and self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                logger.info("定时任务调度器已停止")
            else:
                logger.info("调度器未运行，无需停止")
        except Exception as e:
            logger.error(f"停止调度器时出错: {e}")
            raise e
    
    def restart(self):
        """重启调度器（同步版本）"""
        try:
            # 检查调度器状态并安全停止
            if hasattr(self.scheduler, 'running') and self.scheduler.running:
                logger.info("正在停止运行中的调度器...")
                self.scheduler.shutdown(wait=True)
                logger.info("调度器已停止")
            
            # 重新初始化调度器
            logger.info("正在重新初始化调度器...")
            self.scheduler = AsyncIOScheduler(
                timezone=settings.scheduler_timezone,
                job_defaults={
                    'coalesce': True,
                    'max_instances': 1
                }
            )
            
            # 重新设置任务
            self._setup_jobs()
            
            # 启动调度器
            self.scheduler.start()
            logger.info("定时任务调度器已重启")
            
        except Exception as e:
            logger.error(f"重启调度器时出错: {e}")
            # 尝试重新初始化
            try:
                self.scheduler = AsyncIOScheduler(
                    timezone=settings.scheduler_timezone,
                    job_defaults={
                        'coalesce': True,
                        'max_instances': 1
                    }
                )
                self._setup_jobs()
                self.scheduler.start()
                logger.info("调度器重新初始化成功")
            except Exception as retry_error:
                logger.error(f"重新初始化调度器失败: {retry_error}")
                raise retry_error


# 全局调度器实例
scheduler_service = SchedulerService() 