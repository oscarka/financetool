"""
基金净值更新任务
"""
from typing import Dict, Any, List
from datetime import date
from app.core.base_plugin import BaseTask
from app.core.context import TaskContext, TaskResult
from app.services.fund_service import FundOperationService, FundNavService
from app.services.fund_api_service import FundAPIService
from app.utils.database import get_db
import logging

logger = logging.getLogger(__name__)


class FundNavUpdateTask(BaseTask):
    """基金净值更新任务"""
    
    def __init__(self, task_id: str, name: str, description: str = ""):
        super().__init__(task_id, name, description)
        
    async def execute(self, context: TaskContext) -> TaskResult:
        """执行基金净值更新"""
        try:
            context.log("开始执行基金净值更新任务")
            
            # 获取配置参数
            fund_codes = context.get_config('fund_codes', [])
            update_all = context.get_config('update_all', False)
            data_source = context.get_config('data_source', 'tiantian')
            retry_times = context.get_config('retry_times', 3)
            
            db = next(get_db())
            
            try:
                # 获取需要更新的基金代码
                if update_all:
                    # 获取所有持仓的基金代码
                    positions = FundOperationService.get_fund_positions(db)
                    fund_codes = list(set([pos.fund_code for pos in positions if pos.fund_code]))
                    context.log(f"获取到 {len(fund_codes)} 个持仓基金")
                else:
                    context.log(f"更新指定基金: {fund_codes}")
                
                if not fund_codes:
                    context.log("没有需要更新的基金")
                    return TaskResult(success=True, data={'updated_count': 0})
                
                # 执行更新
                updated_count = 0
                failed_codes = []
                
                for fund_code in fund_codes:
                    try:
                        # 获取最新净值
                        api_service = FundAPIService()
                        nav_data = await api_service.get_fund_nav_latest_tiantian(fund_code)
                        
                        if nav_data and nav_data.get('nav'):
                            # 更新或插入净值记录
                            today = date.today()
                            nav_value = nav_data['nav']
                            
                            # 确保nav是Decimal类型
                            from decimal import Decimal
                            if isinstance(nav_value, str):
                                nav_value = Decimal(nav_value)
                            elif isinstance(nav_value, (int, float)):
                                nav_value = Decimal(str(nav_value))
                            
                            context.log(f"准备更新基金 {fund_code} 净值: {nav_value} (类型: {type(nav_value)})")
                            
                            # 添加调试日志
                            context.log(f"🔍 FundNavService 类型: {type(FundNavService)}")
                            context.log(f"🔍 FundNavService 属性: {dir(FundNavService)}")
                            context.log(f"🔍 检查 update_fund_nav 方法是否存在: {'update_fund_nav' in dir(FundNavService)}")
                            
                            try:
                                # 使用 create_nav 方法创建或更新净值记录
                                nav_record = FundNavService.create_nav(
                                    db, fund_code, today, nav_value
                                )
                                success = nav_record is not None
                                context.log(f"🔍 create_nav 返回结果: {nav_record}")
                            except Exception as e:
                                context.log(f"❌ 调用 create_nav 时出错: {e}", "ERROR")
                                context.log(f"❌ 错误类型: {type(e)}", "ERROR")
                                context.log(f"❌ 错误详情: {str(e)}", "ERROR")
                                raise
                            
                            if success:
                                updated_count += 1
                                context.log(f"成功更新基金 {fund_code} 净值: {nav_data['nav']}")
                                
                                # 发布事件
                                context.set_variable(f'fund_{fund_code}_nav', nav_data['nav'])
                            else:
                                failed_codes.append(fund_code)
                                context.log(f"更新基金 {fund_code} 净值失败", "WARNING")
                        else:
                            failed_codes.append(fund_code)
                            context.log(f"获取基金 {fund_code} 净值失败", "WARNING")
                            
                    except Exception as e:
                        failed_codes.append(fund_code)
                        context.log(f"更新基金 {fund_code} 净值时出错: {e}", "ERROR")
                
                # 记录结果
                result_data = {
                    'updated_count': updated_count,
                    'total_count': len(fund_codes),
                    'failed_codes': failed_codes,
                    'success_rate': updated_count / len(fund_codes) if fund_codes else 0
                }
                
                context.log(f"基金净值更新任务完成，成功更新 {updated_count}/{len(fund_codes)} 个基金")
                
                # 发布事件
                if context.event_bus:
                    await context.event_bus.publish('fund.nav.updated', result_data)
                
                return TaskResult(
                    success=True,
                    data=result_data,
                    events=['fund.nav.updated']
                )
                
            finally:
                db.close()
                
        except Exception as e:
            context.log(f"基金净值更新任务执行失败: {e}", "ERROR")
            return TaskResult(success=False, error=str(e))
            
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # 添加调试日志
        logger.info(f"🔍 fund_nav_update 收到配置: {config}")
        logger.info(f"🔍 配置类型: {type(config)}")
        
        # 检查必需参数
        if 'update_all' not in config and 'fund_codes' not in config:
            logger.error(f"❌ 配置验证失败: 缺少 update_all 或 fund_codes 参数")
            logger.error(f"❌ 当前配置键: {list(config.keys()) if config else 'None'}")
            return False
            
        # 如果指定基金代码，检查格式
        if 'fund_codes' in config:
            logger.info(f"🔍 fund_codes 值: {config['fund_codes']}")
            logger.info(f"🔍 fund_codes 类型: {type(config['fund_codes'])}")
            if not isinstance(config['fund_codes'], list):
                logger.error(f"❌ 配置验证失败: fund_codes 不是 list 类型，实际类型: {type(config['fund_codes'])}")
                return False
            logger.info(f"✅ fund_codes 格式正确，包含 {len(config['fund_codes'])} 个基金代码")
            
        if 'update_all' in config:
            logger.info(f"🔍 update_all 值: {config['update_all']}")
            logger.info(f"🔍 update_all 类型: {type(config['update_all'])}")
            if not isinstance(config['update_all'], bool):
                logger.error(f"❌ 配置验证失败: update_all 不是 bool 类型，实际类型: {type(config['update_all'])}")
                return False
            logger.info(f"✅ update_all 格式正确")
            
        logger.info(f"✅ fund_nav_update 配置验证通过")
        return True 