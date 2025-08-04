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
from app.settings import settings

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务服务类"""
    
    def __init__(self):
        # 确保时区设置正确
        import pytz
        timezone = pytz.timezone(settings.scheduler_timezone)
        
        self.scheduler = AsyncIOScheduler(
            timezone=timezone,
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
        
        # 定投计划执行任务 - 每天10:00执行
        self.scheduler.add_job(
            self._execute_dca_plans,
            CronTrigger(hour=10, minute=0),
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
                    # 使用akshare获取最新净值
                    import akshare as ak
                    df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
                    
                    if not df.empty:
                        # 获取最新的一条数据
                        latest_row = df.iloc[0]
                        nav_date = latest_row['净值日期']
                        nav_value = latest_row['单位净值']
                        
                        success = FundOperationService.update_fund_nav(
                            db, fund_code, nav_value, nav_date
                        )
                        if success:
                            updated_count += 1
                            logger.info(f"成功更新基金 {fund_code} 净值: {nav_value} (日期: {nav_date})")
                        else:
                            logger.warning(f"更新基金 {fund_code} 净值失败")
                    else:
                        logger.warning(f"获取基金 {fund_code} 净值失败")
                except Exception as e:
                    logger.error(f"更新基金 {fund_code} 净值时出错: {e}")
            
            logger.info(f"基金净值更新任务完成，成功更新 {updated_count} 个基金")
            
            # 净值更新后，自动触发待确认操作的更新
            if updated_count > 0:
                logger.info("净值更新后，开始更新待确认操作")
                try:
                    pending_updated = FundOperationService.update_pending_operations(db)
                    logger.info(f"待确认操作更新完成，更新了 {pending_updated} 条记录")
                except Exception as e:
                    logger.error(f"更新待确认操作失败: {e}")
            
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
            
            # 更新所有待确认的操作记录（包括手动操作和定投操作）
            updated_count = FundOperationService.update_pending_operations(db)
            
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
        """同步Wise数据到数据库"""
        logger.info("开始执行Wise数据同步任务")
        try:
            # 初始化Wise服务
            wise_service = WiseAPIService()
            
            # 同步账户余额到数据库
            balance_result = await wise_service.sync_balances_to_db()
            if balance_result.get('success'):
                logger.info(f"Wise余额同步成功: {balance_result['message']}")
            else:
                logger.warning(f"Wise余额同步失败: {balance_result.get('message', '未知错误')}")
            
            # 同步交易记录到数据库
            transaction_result = await wise_service.sync_all_transactions_to_db(days=7)  # 同步最近7天的交易
            if transaction_result.get('success'):
                logger.info(f"Wise交易记录同步成功: {transaction_result['message']}")
            else:
                logger.warning(f"Wise交易记录同步失败: {transaction_result.get('message', '未知错误')}")
            
            # 同步汇率数据
            try:
                # 获取当前持有币种
                balances = await wise_service.get_all_account_balances()
                if balances:
                    currencies = list({b['currency'] for b in balances if b and 'currency' in b})
                    if currencies:
                        # 使用ExchangeRateService同步汇率数据
                        from app.services.exchange_rate_service import ExchangeRateService
                        service = ExchangeRateService(wise_service.api_token)
                        await service.fetch_and_store_history(currencies, days=30, group='day')
                        logger.info(f"Wise汇率数据同步成功，处理了{len(currencies)}个币种")
                    else:
                        logger.info("没有可用的币种进行汇率同步")
                else:
                    logger.warning("获取Wise余额失败，无法同步汇率数据")
            except Exception as e:
                logger.error(f"Wise汇率数据同步失败: {e}")
            
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