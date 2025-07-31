from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import json
import akshare as ak
import logging

from app.models.database import UserOperation, FundInfo, FundNav, AssetPosition, DCAPlan, FundDividend
from app.models.schemas import FundOperationCreate, FundOperationUpdate, FundPosition, DCAPlanCreate, DCAPlanUpdate, FundDividendCreate
from app.utils.database import get_db_context
from app.services.fund_api_service import FundAPIService
from app.utils.auto_logger import auto_log


class FundOperationService:
    """基金操作服务"""
    
    @staticmethod
    def create_operation(db: Session, operation_data: FundOperationCreate) -> UserOperation:
        """创建基金操作记录"""
        # 处理日期字段转换
        operation_date = operation_data.operation_date
        if isinstance(operation_date, str):
            try:
                from datetime import datetime
                operation_date = datetime.fromisoformat(operation_date.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("日期格式不正确")
        
        # 创建操作记录
        operation = UserOperation(
            operation_date=operation_date,
            platform="支付宝",
            asset_type="基金",
            operation_type=operation_data.operation_type,
            asset_code=operation_data.asset_code,
            asset_name=operation_data.asset_name,
            amount=operation_data.amount,
            currency="CNY",
            nav=operation_data.nav,
            fee=operation_data.fee,
            quantity=operation_data.quantity,
            strategy=operation_data.strategy,
            emotion_score=operation_data.emotion_score,
            notes=operation_data.notes,
            status="pending"
        )
        
        db.add(operation)
        db.commit()
        db.refresh(operation)
        
        # 根据操作类型进行不同的处理
        if operation_data.operation_type == "buy":
            FundOperationService._calculate_buy_shares(db, operation)
        elif operation_data.operation_type == "sell":
            FundOperationService._calculate_sell_shares(db, operation)
        
        return operation
    
    @staticmethod
    def _calculate_buy_shares(db: Session, operation: UserOperation):
        """计算买入份额，支持手续费fee，并自动同步最新净值到数据库"""
        print(f"[调试] _calculate_buy_shares 开始: operation_id={operation.id}, asset_code={operation.asset_code}")
        print(f"[调试] 当前操作数据: amount={operation.amount}, fee={operation.fee}, nav={operation.nav}, quantity={operation.quantity}")
        
        # 确保operation_date是datetime对象
        if isinstance(operation.operation_date, str):
            try:
                operation.operation_date = datetime.fromisoformat(operation.operation_date.replace('Z', '+00:00'))
                print(f"[调试] 转换operation_date为datetime: {operation.operation_date}")
            except ValueError as e:
                print(f"[调试] operation_date转换失败: {e}")
                raise ValueError(f"日期格式不正确: {operation.operation_date}")
        
        # 优先使用用户填写的净值，如果没有则从数据库查询
        nav_value = operation.nav
        nav_date = None
        if nav_value is None:
            print(f"[调试] 操作中没有净值，尝试从数据库查询")
            # 处理operation_date可能是字符串的情况
            if isinstance(operation.operation_date, str):
                nav_date = datetime.fromisoformat(operation.operation_date.replace('Z', '+00:00')).date()
            else:
                nav_date = operation.operation_date.date()
            nav_record = FundOperationService._get_nav_by_date(db, operation.asset_code, nav_date)
            nav_value = nav_record.nav if nav_record else None
            nav_date = nav_record.nav_date if nav_record else None
            print(f"[调试] 数据库查询结果: nav_value={nav_value}, nav_date={nav_date}")
        else:
            # 处理operation_date可能是字符串的情况
            if isinstance(operation.operation_date, str):
                nav_date = datetime.fromisoformat(operation.operation_date.replace('Z', '+00:00')).date()
            else:
                nav_date = operation.operation_date.date()
            print(f"[调试] 使用操作中的净值: nav_value={nav_value}, nav_date={nav_date}")
        
        fee = operation.fee or 0
        print(f"[调试] 手续费: {fee}")

        # 如果有净值，就重新计算份额（无论quantity是否为None）
        if nav_value:
            shares = (operation.amount - fee) / nav_value
            # 四舍五入保留2位小数
            shares = Decimal(shares).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            operation.quantity = shares
            operation.nav = nav_value
            operation.price = nav_value
            operation.status = "confirmed"
            operation.updated_at = datetime.utcnow()
            print(f"[调试] 重新计算份额: amount={operation.amount}, fee={fee}, nav={nav_value}, shares={shares}")
            
            # 同步最新净值到数据库
            try:
                # 使用FundAPIService获取最新净值
                api_service = FundAPIService()
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                latest_nav_data = loop.run_until_complete(api_service.get_fund_nav_latest_tiantian(operation.asset_code))
                loop.close()
                
                if latest_nav_data and latest_nav_data.get('nav'):
                    print(f"[调试] 查到最新净值数据: {latest_nav_data}")
                    # 使用API返回的净值日期和净值，而不是操作日期
                    api_nav_date = latest_nav_data.get('nav_date')
                    api_nav = latest_nav_data.get('nav')
                    if api_nav_date and api_nav:
                        print(f"[调试] 写入最新净值到数据库: fund_code={operation.asset_code}, nav_date={api_nav_date}, nav={api_nav}")
                        FundNavService.create_nav(db, operation.asset_code, api_nav_date, api_nav)
                    else:
                        print(f"[调试] API返回的净值数据不完整，跳过写入数据库")
                else:
                    print(f"[调试] 未查到最新净值数据")
            except Exception as e:
                print(f"[调试] 同步最新净值时出错: {e}")
            
            # 更新持仓
            print(f"[调试] 准备调用_update_position...")
            try:
                FundOperationService._update_position(db, operation)
                print(f"[调试] _update_position调用成功")
            except Exception as e:
                print(f"[调试] _update_position调用失败: {e}")
                print(f"[调试] 错误类型: {type(e)}")
                import traceback
                print(f"[调试] 错误堆栈: {traceback.format_exc()}")
                raise e
        else:
            print(f"[调试] 跳过份额计算: nav_value={nav_value}")
        
        print(f"[调试] _calculate_buy_shares 完成: quantity={operation.quantity}")
        return operation
    
    @staticmethod
    def _calculate_sell_shares(db: Session, operation: UserOperation):
        """计算卖出份额，支持按金额计算和按份额计算"""
        # 确保operation_date是datetime对象
        if isinstance(operation.operation_date, str):
            try:
                operation.operation_date = datetime.fromisoformat(operation.operation_date.replace('Z', '+00:00'))
                print(f"[调试] 转换operation_date为datetime: {operation.operation_date}")
            except ValueError as e:
                print(f"[调试] operation_date转换失败: {e}")
                raise ValueError(f"日期格式不正确: {operation.operation_date}")
        
        # 优先使用用户填写的净值，如果没有则从数据库查询
        nav_value = operation.nav
        if nav_value is None:
            # 处理operation_date可能是字符串的情况
            if isinstance(operation.operation_date, str):
                nav_date = datetime.fromisoformat(operation.operation_date.replace('Z', '+00:00')).date()
            else:
                nav_date = operation.operation_date.date()
            nav_record = FundOperationService._get_nav_by_date(db, operation.asset_code, nav_date)
            nav_value = nav_record.nav if nav_record else None
        
        if not nav_value:
            print(f"[调试] 卖出操作缺少净值信息，跳过自动计算")
            return
        
        # 查找现有持仓
        position = db.query(AssetPosition).filter(
            and_(
                AssetPosition.platform == operation.platform,
                AssetPosition.asset_code == operation.asset_code,
                AssetPosition.currency == operation.currency
            )
        ).first()
        
        if not position:
            print(f"[调试] 卖出操作：未找到持仓记录")
            return
        
        fee = operation.fee or 0
        
        # 如果用户填写了金额但没有填写份额，按金额计算份额
        if operation.amount and operation.quantity is None:
            shares = (operation.amount - fee) / nav_value
            if shares <= position.quantity:
                # 四舍五入保留2位小数
                shares = Decimal(shares).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                operation.quantity = shares
                operation.nav = nav_value
                operation.price = nav_value
                operation.status = "confirmed"
                db.commit()
                db.refresh(operation)
                FundOperationService._update_position(db, operation)
                print(f"[调试] 卖出操作：按金额计算份额成功，份额={shares}")
            else:
                print(f"[调试] 卖出操作：计算出的份额超过持仓，份额={shares}，持仓={position.quantity}")
        
        # 如果用户填写了份额但没有填写金额，按份额计算金额
        elif operation.quantity and operation.amount is None:
            # 按份额计算金额：金额 = 份额 * 净值 + 手续费
            amount = operation.quantity * nav_value + fee
            operation.amount = amount
            operation.nav = nav_value
            operation.price = nav_value
            operation.status = "confirmed"
            db.commit()
            db.refresh(operation)
            FundOperationService._update_position(db, operation)
            print(f"[调试] 卖出操作：按份额计算金额成功，金额={amount}")
        
        # 如果用户同时填写了金额和份额，验证一致性
        elif operation.amount and operation.quantity:
            expected_amount = operation.quantity * nav_value + fee
            if abs(operation.amount - expected_amount) < 0.01:  # 允许1分钱的误差
                operation.nav = nav_value
                operation.price = nav_value
                operation.status = "confirmed"
                db.commit()
                db.refresh(operation)
                FundOperationService._update_position(db, operation)
                print(f"[调试] 卖出操作：金额和份额一致，确认成功")
            else:
                print(f"[调试] 卖出操作：金额和份额不一致，金额={operation.amount}，期望金额={expected_amount}")
        
        # 验证卖出份额不超过持仓
        if operation.quantity and operation.quantity > position.quantity:
            print(f"[调试] 卖出操作：份额超过持仓，卖出份额={operation.quantity}，持仓份额={position.quantity}")
            print(f"[调试] 历史记录修改场景：重新计算持仓状态")
            # 在历史记录修改场景下，重新计算持仓状态
            # 先清空当前持仓，然后重新计算所有历史操作
            db.delete(position)
            db.commit()
            print(f"[调试] 已清空当前持仓，准备重新计算")
            
            # 重新计算所有历史操作
            FundOperationService.recalculate_all_positions(db)
            print(f"[调试] 持仓重新计算完成")
            
            # 重新获取持仓
            position = db.query(AssetPosition).filter(
                and_(
                    AssetPosition.platform == operation.platform,
                    AssetPosition.asset_code == operation.asset_code,
                    AssetPosition.currency == operation.currency
                )
            ).first()
            
            if not position:
                print(f"[调试] 重新计算后仍无持仓，允许执行卖出操作")
                return
            else:
                print(f"[调试] 重新计算后持仓份额: {position.quantity}")
                # 再次检查份额是否超过
                if operation.quantity > position.quantity:
                    print(f"[调试] 重新计算后仍超过持仓，允许执行（历史记录修改）")
                    return
    
    @staticmethod
    def _get_nav_by_date(db: Session, fund_code: str, nav_date: date) -> Optional[FundNav]:
        """根据日期获取基金净值"""
        return db.query(FundNav).filter(
            and_(
                FundNav.fund_code == fund_code,
                FundNav.nav_date == nav_date
            )
        ).first()
    
    @staticmethod
    def _update_position(db: Session, operation: UserOperation):
        """更新基金持仓"""
        # 查找现有持仓
        position = db.query(AssetPosition).filter(
            and_(
                AssetPosition.platform == operation.platform,
                AssetPosition.asset_code == operation.asset_code,
                AssetPosition.currency == operation.currency
            )
        ).first()
        
        if operation.operation_type == "buy":
            if position:
                # 更新现有持仓
                total_shares = position.quantity + operation.quantity
                total_cost = position.total_invested + operation.amount
                avg_cost = total_cost / total_shares
                
                position.quantity = total_shares
                position.avg_cost = avg_cost
                position.total_invested = total_cost
                position.current_price = operation.nav  # 使用净值作为当前价格
                position.current_value = total_shares * operation.nav  # 使用份额 * 净值
                position.total_profit = position.current_value - total_cost
                position.profit_rate = position.total_profit / total_cost if total_cost > 0 else Decimal("0")
                position.last_updated = datetime.now()
            else:
                # PostgreSQL序列修复：检查并重置序列
                try:
                    # 获取表中最大ID
                    max_id_result = db.execute(text("SELECT MAX(id) FROM asset_positions"))
                    max_id = max_id_result.scalar()
                    
                    if max_id is not None:
                        # 获取当前序列值
                        seq_result = db.execute(text("SELECT last_value FROM asset_positions_id_seq"))
                        current_seq = seq_result.scalar()
                        
                        # 如果序列值小于最大ID，重置序列
                        if current_seq < max_id:
                            print(f"[调试] 重置asset_positions序列: 当前={current_seq}, 最大ID={max_id}")
                            db.execute(text(f"SELECT setval('asset_positions_id_seq', {max_id})"))
                            db.commit()  # 提交序列重置
                            print(f"[调试] asset_positions序列重置完成")
                except Exception as e:
                    print(f"[调试] asset_positions序列检查失败: {e}")
                
                # 创建新持仓
                position = AssetPosition(
                    platform=operation.platform,
                    asset_type=operation.asset_type,
                    asset_code=operation.asset_code,
                    asset_name=operation.asset_name,
                    currency=operation.currency,
                    quantity=operation.quantity,
                    avg_cost=operation.nav,  # 使用净值作为平均成本
                    current_price=operation.nav,  # 使用净值作为当前价格
                    current_value=operation.quantity * operation.nav,  # 使用份额 * 净值
                    total_invested=operation.amount,
                    total_profit=Decimal("0"),
                    profit_rate=Decimal("0"),
                    last_updated=datetime.now()
                )
                db.add(position)
        
        elif operation.operation_type == "sell":
            if position and position.quantity >= operation.quantity:
                # 更新持仓（卖出）
                remaining_shares = position.quantity - operation.quantity
                sold_cost = (operation.amount / operation.quantity) * operation.quantity
                
                if remaining_shares > 0:
                    # 还有剩余份额
                    position.quantity = remaining_shares
                    position.total_invested = position.total_invested - sold_cost
                    position.current_value = remaining_shares * operation.nav  # 使用净值作为当前价格
                    position.total_profit = position.current_value - position.total_invested
                    position.profit_rate = position.total_profit / position.total_invested if position.total_invested > 0 else Decimal("0")
                else:
                    # 全部卖出，删除持仓记录
                    db.delete(position)
        
        db.commit()
    
    @staticmethod
    @auto_log("database", log_result=True)
    def get_operations(
        db: Session, 
        fund_code: Optional[str] = None,
        operation_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        dca_plan_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[UserOperation], int]:
        """获取基金操作记录"""
        query = db.query(UserOperation).filter(UserOperation.asset_type == "基金")
        
        if fund_code:
            query = query.filter(UserOperation.asset_code == fund_code)
        
        if operation_type:
            query = query.filter(UserOperation.operation_type == operation_type)
        
        if start_date:
            query = query.filter(UserOperation.operation_date >= start_date)
        
        if end_date:
            query = query.filter(UserOperation.operation_date <= end_date)
        
        if dca_plan_id:
            query = query.filter(UserOperation.dca_plan_id == dca_plan_id)
        
        if status:
            query = query.filter(UserOperation.status == status)
        
        # 获取总数
        total = query.count()
        
        # 分页
        operations = query.order_by(desc(UserOperation.operation_date)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return operations, total
    
    @staticmethod
    def update_operation(db: Session, operation_id: int, update_data: FundOperationUpdate) -> UserOperation:
        """更新基金操作记录"""
        operation = db.query(UserOperation).filter(UserOperation.id == operation_id).first()
        if not operation:
            raise ValueError("操作记录不存在")
        
        print(f"[调试] 开始更新操作: id={operation_id}, operation_type={operation.operation_type}")
        print(f"[调试] 更新数据: {update_data}")
        
        # 构建更新字典
        update_dict = {}
        for field, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                update_dict[field] = value
                print(f"[调试] 字段 {field} 将被更新为: {value}")
        
        print(f"[调试] 最终更新字典: {update_dict}")
        
        # 先处理类型转换，尤其是 operation_date
        print(f"[调试] 检查operation_date字段: {'operation_date' in update_dict}")
        if 'operation_date' in update_dict:
            print(f"[调试] operation_date的值: {update_dict['operation_date']}, 类型: {type(update_dict['operation_date'])}")
            if isinstance(update_dict['operation_date'], str):
                print(f"[调试] 开始转换operation_date字符串...")
                try:
                    print(f"[调试] 原始字符串: {update_dict['operation_date']}")
                    processed_string = update_dict['operation_date'].replace('Z', '+00:00')
                    print(f"[调试] 处理后字符串: {processed_string}")
                    # 使用完整的模块路径避免变量冲突
                    from datetime import datetime as dt
                    converted_datetime = dt.fromisoformat(processed_string)
                    print(f"[调试] 转换结果: {converted_datetime}")
                    update_dict['operation_date'] = converted_datetime
                    print(f"[调试] 转换operation_date字符串为datetime: {update_dict['operation_date']}")
                except ValueError as e:
                    print(f"[调试] operation_date转换失败: {e}")
                    raise ValueError(f"日期格式不正确: {update_dict['operation_date']}")
                except Exception as e:
                    print(f"[调试] operation_date转换出现未知错误: {e}")
                    print(f"[调试] 错误类型: {type(e)}")
                    import traceback
                    print(f"[调试] 错误堆栈: {traceback.format_exc()}")
                    raise e
            else:
                print(f"[调试] operation_date不是字符串，跳过转换")
        else:
            print(f"[调试] update_dict中没有operation_date字段")
        
        # 先更新字段
        print(f"[调试] 开始设置字段...")
        for field, value in update_dict.items():
            print(f"[调试] 准备设置字段 {field}: 值={value}, 类型={type(value)}")
            try:
                setattr(operation, field, value)
                print(f"[调试] 已更新字段 {field}: {value}")
            except Exception as e:
                print(f"[调试] 设置字段 {field} 失败: {e}")
                print(f"[调试] 错误类型: {type(e)}")
                import traceback
                print(f"[调试] 错误堆栈: {traceback.format_exc()}")
                raise e
        
        # 如果有nav字段，自动写入/更新净值表
        nav = update_dict.get('nav', None)
        if nav is not None:
            print(f"[调试] 检测到nav字段更新: {nav}")
            try:
                # 确保operation_date是datetime对象
                if isinstance(operation.operation_date, str):
                    from datetime import datetime
                    nav_date = datetime.fromisoformat(operation.operation_date.replace('Z', '+00:00')).date()
                else:
                    nav_date = operation.operation_date.date()
                print(f"[调试] 准备调用FundNavService.create_nav: fund_code={operation.asset_code}, nav_date={nav_date}, nav={nav}")
                FundNavService.create_nav(db, operation.asset_code, nav_date, nav)
                print(f"[调试] FundNavService.create_nav 调用成功")
            except Exception as e:
                print(f"[调试] FundNavService.create_nav 调用失败: {e}")
                import traceback
                print(f"[调试] 错误堆栈: {traceback.format_exc()}")
                raise e
        
        # 根据操作类型重新计算份额（在字段更新后）
        nav_check = nav is not None
        amount_check = update_dict.get('amount') is not None
        fee_check = update_dict.get('fee') is not None
        status_check = update_dict.get('status') is not None
        
        print(f"[调试] 份额重新计算条件检查:")
        print(f"[调试]   operation_type={operation.operation_type}")
        print(f"[调试]   nav_check={nav_check} (nav={nav})")
        print(f"[调试]   amount_check={amount_check} (amount={update_dict.get('amount')})")
        print(f"[调试]   fee_check={fee_check} (fee={update_dict.get('fee')})")
        print(f"[调试]   status_check={status_check} (status={update_dict.get('status')})")
        print(f"[调试]   买入条件: {operation.operation_type == 'buy'}")
        print(f"[调试]   字段变化条件: {nav_check or amount_check or fee_check}")
        print(f"[调试]   最终条件: {operation.operation_type == 'buy' and (nav_check or amount_check or fee_check)}")
        
        # 只有在真正需要重新计算时才执行，避免重复计算
        should_recalculate = (operation.operation_type == "buy" or operation.operation_type == "sell") and (nav_check or amount_check or fee_check)
        
        # 重新计算份额
        if should_recalculate:
            print(f"[调试] 开始重新计算份额...")
            try:
                if operation.operation_type == 'buy':
                    print(f"[调试] 调用_calculate_buy_shares...")
                    # 先清空现有持仓，避免重复累加
                    existing_position = db.query(AssetPosition).filter(
                        and_(
                            AssetPosition.platform == operation.platform,
                            AssetPosition.asset_code == operation.asset_code,
                            AssetPosition.currency == operation.currency
                        )
                    ).first()
                    if existing_position:
                        print(f"[调试] 清空现有持仓，避免重复计算: id={existing_position.id}")
                        db.delete(existing_position)
                        db.commit()
                    
                    FundOperationService._calculate_buy_shares(db, operation)
                    print(f"[调试] _calculate_buy_shares调用完成")
                elif operation.operation_type == 'sell':
                    print(f"[调试] 调用_calculate_sell_shares...")
                    FundOperationService._calculate_sell_shares(db, operation)
                    print(f"[调试] _calculate_sell_shares调用完成")
                print(f"[调试] 份额重新计算完成")
                
                # 份额重新计算后，重新获取操作对象以确保状态一致
                print(f"[调试] 重新获取操作对象...")
                db.refresh(operation)
                print(f"[调试] 操作对象重新获取成功")
            except Exception as e:
                print(f"[调试] 份额重新计算失败: {e}")
                print(f"[调试] 错误类型: {type(e)}")
                import traceback
                print(f"[调试] 错误堆栈: {traceback.format_exc()}")
                raise e
        
        # 设置更新时间（只有在没有重新计算份额时才设置）
        if not should_recalculate:
            print(f"[调试] 设置updated_at...")
            operation.updated_at = datetime.utcnow()
            print(f"[调试] 设置updated_at: {operation.updated_at}")
        else:
            print(f"[调试] 跳过设置updated_at（已在份额重新计算中设置）")
        
        print(f"[调试] 准备提交数据库事务...")
        try:
            db.commit()
            print(f"[调试] 数据库事务提交成功")
        except Exception as e:
            print(f"[调试] 数据库事务提交失败: {e}")
            print(f"[调试] 错误类型: {type(e)}")
            import traceback
            print(f"[调试] 错误堆栈: {traceback.format_exc()}")
            raise e
        
        print(f"[调试] 准备刷新操作对象...")
        try:
            db.refresh(operation)
            print(f"[调试] 操作对象刷新成功")
        except Exception as e:
            print(f"[调试] 操作对象刷新失败: {e}")
            print(f"[调试] 错误类型: {type(e)}")
            import traceback
            print(f"[调试] 错误堆栈: {traceback.format_exc()}")
            raise e
        
        print(f"[调试] update_operation 完成")
        return operation
    
    @staticmethod
    @auto_log("database", log_result=True)
    def get_fund_positions(db: Session) -> List[FundPosition]:
        """获取基金持仓列表 - 优化版本"""
        positions = db.query(AssetPosition).filter(
            AssetPosition.asset_type == "基金"
        ).all()
        
        if not positions:
            return []
        
        # 批量获取最新净值 - 优化：只查询数据库，避免外部API调用
        fund_codes = list(set(pos.asset_code for pos in positions))
        latest_nav_map = {}
        
        if fund_codes:
            # 批量查询数据库中的最新净值
            for fund_code in fund_codes:
                latest_nav_obj = FundNavService.get_latest_nav(db, fund_code)
                if latest_nav_obj and latest_nav_obj.nav:
                    latest_nav_map[fund_code] = latest_nav_obj.nav
                    print(f"[调试] 持仓批量获取净值: {fund_code} = {latest_nav_obj.nav}")
        
        result = []
        for pos in positions:
            try:
                # 使用批量查询的结果
                current_nav = latest_nav_map.get(pos.asset_code, pos.current_price)
                print(f"[调试] 持仓使用净值: {pos.asset_code} = {current_nav}")
                
                # 重新计算当前市值和收益
                current_value = pos.quantity * current_nav
                total_profit = current_value - pos.total_invested
                profit_rate = total_profit / pos.total_invested if pos.total_invested > 0 else Decimal("0")
                
                # 更新持仓数据
                pos.current_price = current_nav
                pos.current_value = current_value
                pos.total_profit = total_profit
                pos.profit_rate = profit_rate
                pos.last_updated = datetime.now()
                
                result.append(FundPosition(
                    asset_code=pos.asset_code,
                    asset_name=pos.asset_name,
                    total_shares=pos.quantity,
                    avg_cost=pos.avg_cost,
                    current_nav=current_nav,
                    current_value=current_value,
                    total_invested=pos.total_invested,
                    total_profit=total_profit,
                    profit_rate=profit_rate,
                    last_updated=pos.last_updated
                ))
            except Exception as e:
                print(f"[调试] 处理持仓 {pos.asset_code} 时出错: {e}")
                continue
        
        db.commit()
        return result
    
    @staticmethod
    @auto_log("database", log_result=True)
    def get_position_summary(db: Session) -> dict:
        """获取持仓汇总信息 - 优化版本（避免重复查询）"""
        try:
            # 直接查询数据库计算汇总，避免调用get_fund_positions造成重复
            positions_data = db.query(AssetPosition).filter(
                AssetPosition.asset_type == "基金"
            ).all()
            
            if not positions_data:
                return {
                    "total_invested": Decimal("0"),
                    "total_value": Decimal("0"),
                    "total_profit": Decimal("0"),
                    "total_profit_rate": Decimal("0"),
                    "asset_count": 0,
                    "profitable_count": 0,
                    "loss_count": 0
                }
            
            # 批量获取最新净值
            fund_codes = list(set(pos.asset_code for pos in positions_data))
            latest_nav_map = {}
            
            if fund_codes:
                for fund_code in fund_codes:
                    latest_nav_obj = FundNavService.get_latest_nav(db, fund_code)
                    if latest_nav_obj and latest_nav_obj.nav:
                        latest_nav_map[fund_code] = latest_nav_obj.nav
            
            # 计算汇总数据
            total_invested = Decimal("0")
            total_value = Decimal("0")
            profitable_count = 0
            loss_count = 0
            
            for pos in positions_data:
                current_nav = latest_nav_map.get(pos.asset_code, pos.current_price)
                current_value = pos.quantity * current_nav
                total_profit = current_value - pos.total_invested
                
                total_invested += pos.total_invested
                total_value += current_value
                
                if total_profit > 0:
                    profitable_count += 1
                elif total_profit < 0:
                    loss_count += 1
            
            total_profit = total_value - total_invested
            total_profit_rate = total_profit / total_invested if total_invested > 0 else Decimal("0")
            
            return {
                "total_invested": total_invested,
                "total_value": total_value,
                "total_profit": total_profit,
                "total_profit_rate": total_profit_rate,
                "asset_count": len(positions_data),
                "profitable_count": profitable_count,
                "loss_count": loss_count
            }
        except Exception as e:
            print(f"[调试] 持仓汇总计算异常: {e}")
            import traceback
            print(f"[调试] 异常堆栈: {traceback.format_exc()}")
            raise e
    
    @staticmethod
    def recalculate_all_positions(db: Session) -> dict:
        """重新计算所有持仓（基于所有已确认的操作记录）"""
        try:
            print(f"[调试] 开始重新计算所有持仓...")
            
            # 清空所有持仓
            deleted_count = db.query(AssetPosition).filter(AssetPosition.asset_type == "基金").delete()
            db.commit()
            print(f"[调试] 清空了 {deleted_count} 条持仓记录")
            
            # 获取所有已确认的操作记录，按时间排序
            operations = db.query(UserOperation).filter(
                and_(
                    UserOperation.asset_type == "基金",
                    UserOperation.status == "confirmed"
                )
            ).order_by(UserOperation.operation_date).all()
            
            print(f"[调试] 找到 {len(operations)} 条已确认的操作记录")
            
            processed_count = 0
            for operation in operations:
                try:
                    print(f"[调试] 处理操作: id={operation.id}, type={operation.operation_type}, asset_code={operation.asset_code}, quantity={operation.quantity}")
                    if operation.operation_type == "buy":
                        # 对于买入操作，直接更新持仓
                        FundOperationService._update_position(db, operation)
                        processed_count += 1
                    elif operation.operation_type == "sell":
                        # 对于卖出操作，直接更新持仓
                        FundOperationService._update_position(db, operation)
                        processed_count += 1
                except Exception as e:
                    print(f"[调试] 处理操作 {operation.id} 时出错: {e}")
                    continue
            
            print(f"[调试] 成功处理了 {processed_count} 条操作记录")
            return {
                "success": True,
                "message": f"重新计算了 {processed_count} 条操作记录的持仓",
                "processed_count": processed_count
            }
        except Exception as e:
            print(f"[调试] 重新计算持仓失败: {e}")
            return {
                "success": False,
                "message": f"重新计算持仓失败: {e}",
                "processed_count": 0
            }
    
    @staticmethod
    def update_pending_operations(db: Session) -> int:
        """更新所有待确认的操作记录的净值"""
        today = date.today()
        updated_count = 0
        
        # 查找所有待确认的操作记录
        pending_operations = db.query(UserOperation).filter(
            and_(
                UserOperation.status == "pending",
                UserOperation.operation_type == "buy",
                UserOperation.dca_plan_id.isnot(None)
            )
        ).all()
        
        for operation in pending_operations:
            # 查找对应基金的当天净值
            nav_obj = db.query(FundNav).filter(
                and_(
                    FundNav.fund_code == operation.asset_code,
                    FundNav.nav_date == today
                )
            ).first()
            
            if nav_obj:
                # 更新操作记录
                operation.nav = nav_obj.nav
                operation.status = "confirmed"
                
                # 计算份额
                shares = (operation.amount - operation.fee) / nav_obj.nav
                operation.quantity = shares
                operation.price = nav_obj.nav
                
                # 更新持仓
                FundOperationService._update_position(db, operation)
                
                updated_count += 1
        
        if updated_count > 0:
            db.commit()
        
        return updated_count


class FundInfoService:
    """基金信息服务"""
    
    @staticmethod
    def create_fund_info(db: Session, fund_code: str, fund_name: str, **kwargs) -> FundInfo:
        """创建基金信息"""
        fund_info = FundInfo(
            fund_code=fund_code,
            fund_name=fund_name,
            **kwargs
        )
        db.add(fund_info)
        db.commit()
        db.refresh(fund_info)
        return fund_info
    
    @staticmethod
    @auto_log("database", log_result=True)
    def get_fund_info(db: Session, fund_code: str) -> Optional[FundInfo]:
        """获取基金信息"""
        return db.query(FundInfo).filter(FundInfo.fund_code == fund_code).first()
    
    @staticmethod
    @auto_log("database", log_result=True)
    def get_all_funds(db: Session) -> List[FundInfo]:
        """获取所有基金信息"""
        return db.query(FundInfo).order_by(FundInfo.fund_code).all()


class FundNavService:
    """基金净值服务"""
    
    @staticmethod
    def create_nav(db: Session, fund_code: str, nav_date: date, nav: Decimal, **kwargs) -> FundNav:
        """创建基金净值记录"""
        print(f"[调试] FundNavService.create_nav 开始: fund_code={fund_code}, nav_date={nav_date}, nav={nav}, kwargs={kwargs}")
        
        # 检查是否已存在
        existing = db.query(FundNav).filter(
            and_(
                FundNav.fund_code == fund_code,
                FundNav.nav_date == nav_date
            )
        ).first()
        
        print(f"[调试] 检查现有记录: existing={existing}")
        
        if existing:
            print(f"[调试] 更新现有记录: id={existing.id}")
            # 更新现有记录
            for key, value in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
                    print(f"[调试] 更新字段: {key}={value}")
            existing.nav = nav
            print(f"[调试] 更新净值: nav={nav}")
            # 移除db.commit()，让外层事务统一管理
            db.refresh(existing)
            print(f"[调试] 更新完成: id={existing.id}")
            return existing
        else:
            print(f"[调试] 创建新记录")
            
            # PostgreSQL序列修复：检查并重置序列
            try:
                # 获取表中最大ID
                max_id_result = db.execute(text("SELECT MAX(id) FROM fund_nav"))
                max_id = max_id_result.scalar()
                
                if max_id is not None:
                    # 获取当前序列值
                    seq_result = db.execute(text("SELECT last_value FROM fund_nav_id_seq"))
                    current_seq = seq_result.scalar()
                    
                    # 如果序列值小于最大ID，重置序列
                    if current_seq < max_id:
                        print(f"[调试] 重置序列: 当前={current_seq}, 最大ID={max_id}")
                        db.execute(text(f"SELECT setval('fund_nav_id_seq', {max_id})"))
                        db.commit()  # 提交序列重置
                        print(f"[调试] 序列重置完成")
            except Exception as e:
                print(f"[调试] 序列检查失败: {e}")
            
            # 创建新记录
            nav_record = FundNav(
                fund_code=fund_code,
                nav_date=nav_date,
                nav=nav,
                **kwargs
            )
            print(f"[调试] 创建 FundNav 对象: {nav_record}")
            db.add(nav_record)
            print(f"[调试] 添加到数据库会话")
            # 移除db.commit()，让外层事务统一管理
            print(f"[调试] 创建完成，等待外层事务提交")
            return nav_record
    
    @staticmethod
    @auto_log("database", log_result=True)
    def get_latest_nav(db: Session, fund_code: str) -> Optional[FundNav]:
        """获取基金最新净值"""
        return db.query(FundNav).filter(
            FundNav.fund_code == fund_code
        ).order_by(desc(FundNav.nav_date)).first()
    
    @staticmethod
    @auto_log("database", log_result=True)
    def get_nav_history(db: Session, fund_code: str, days: int = 30) -> List[FundNav]:
        """获取基金净值历史"""
        return db.query(FundNav).filter(
            FundNav.fund_code == fund_code
        ).order_by(desc(FundNav.nav_date)).limit(days).all()

    @staticmethod
    def fetch_and_cache_nav_history(db: Session, fund_code: str) -> int:
        """用akshare拉取指定基金的历史净值并写入数据库，返回写入条数"""
        try:
            print(f"[调试] 开始用akshare拉取基金 {fund_code} 的历史净值")
            df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
            print(f"[调试] akshare返回数据行数: {len(df)}")
            
            count = 0
            for _, row in df.iterrows():
                try:
                    nav_date_value = row['净值日期']
                    # 处理日期可能是字符串或datetime.date对象的情况
                    if isinstance(nav_date_value, str):
                        nav_date = datetime.strptime(nav_date_value, '%Y-%m-%d').date()
                    elif hasattr(nav_date_value, 'date'):
                        nav_date = nav_date_value.date()
                    else:
                        nav_date = nav_date_value
                    
                    nav = Decimal(str(row['单位净值']))
                    acc_nav = Decimal(str(row.get('累计净值', 0))) if row.get('累计净值') else None
                    
                    # 插入或更新
                    existing = db.query(FundNav).filter(
                        FundNav.fund_code == fund_code,
                        FundNav.nav_date == nav_date
                    ).first()
                    
                    if existing:
                        existing.nav = nav
                        existing.accumulated_nav = acc_nav
                        existing.source = "akshare"
                    else:
                        nav_record = FundNav(
                            fund_code=fund_code,
                            nav_date=nav_date,
                            nav=nav,
                            accumulated_nav=acc_nav,
                            source="akshare"
                        )
                        db.add(nav_record)
                        count += 1
                except Exception as e:
                    print(f"[调试] 处理单条净值记录失败: {e}, row={row}")
                    continue
            
            db.commit()
            print(f"[调试] 成功写入 {count} 条历史净值记录")
            return count
        except Exception as e:
            print(f"[调试] akshare拉取历史净值失败: {e}")
            db.rollback()
            raise e

    @staticmethod
    @auto_log("database", log_result=True)
    def get_batch_latest_nav(db: Session, fund_codes: List[str]) -> dict:
        """批量获取基金最新净值 - 优化性能"""
        if not fund_codes:
            return {}
        
        # 子查询：获取每个基金的最新净值日期
        latest_dates = db.query(
            FundNav.fund_code,
            func.max(FundNav.nav_date).label('max_date')
        ).filter(
            FundNav.fund_code.in_(fund_codes)
        ).group_by(FundNav.fund_code).subquery()
        
        # 主查询：获取最新净值记录
        latest_navs = db.query(FundNav).join(
            latest_dates,
            and_(
                FundNav.fund_code == latest_dates.c.fund_code,
                FundNav.nav_date == latest_dates.c.max_date
            )
        ).all()
        
        # 构建结果字典
        result = {}
        for nav_obj in latest_navs:
            result[nav_obj.fund_code] = nav_obj
        
        return result


class DCAService:
    """定投计划服务类"""
    
    @staticmethod
    def create_dca_plan(db: Session, plan_data: DCAPlanCreate) -> DCAPlan:
        """创建定投计划"""
        print(f"[调试] 创建定投计划 - 接收到的日期数据:")
        print(f"[调试]   start_date: {plan_data.start_date}, 类型: {type(plan_data.start_date)}")
        print(f"[调试]   end_date: {plan_data.end_date}, 类型: {type(plan_data.end_date)}")
        
        # 计算下次执行日期
        next_execution_date = DCAService._calculate_next_execution_date(
            plan_data.start_date, 
            plan_data.frequency, 
            plan_data.frequency_value
        )
        
        # 创建定投计划
        plan = DCAPlan(
            plan_name=plan_data.plan_name,
            platform=plan_data.platform,
            asset_type=plan_data.asset_type,
            asset_code=plan_data.asset_code,
            asset_name=plan_data.asset_name,
            amount=plan_data.amount,
            currency=plan_data.currency,
            frequency=plan_data.frequency,
            frequency_value=plan_data.frequency_value,
            start_date=plan_data.start_date,
            end_date=plan_data.end_date,
            strategy=plan_data.strategy,
            execution_time=plan_data.execution_time,
            next_execution_date=next_execution_date,  # 添加下次执行日期
            smart_dca=plan_data.smart_dca,
            base_amount=plan_data.base_amount,
            max_amount=plan_data.max_amount,
            increase_rate=plan_data.increase_rate,
            min_nav=plan_data.min_nav,
            max_nav=plan_data.max_nav,
            skip_holidays=plan_data.skip_holidays,
            enable_notification=plan_data.enable_notification,
            notification_before=plan_data.notification_before,
            fee_rate=plan_data.fee_rate,
            exclude_dates=json.dumps(plan_data.exclude_dates) if plan_data.exclude_dates else None
        )
        
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan
    
    @staticmethod
    @auto_log("database", log_result=True)
    def get_dca_plans(db: Session, status: Optional[str] = None) -> List[dict]:
        """获取定投计划列表，返回dict，exclude_dates为list，ORM对象不被污染"""
        query = db.query(DCAPlan)
        if status:
            query = query.filter(DCAPlan.status == status)
        plans = query.order_by(DCAPlan.created_at.desc()).all()
        result = []
        for plan in plans:
            exclude_dates = []
            if plan.exclude_dates:
                try:
                    exclude_dates = json.loads(plan.exclude_dates)
                except (json.JSONDecodeError, TypeError):
                    exclude_dates = []
            plan_dict = {**plan.__dict__, 'exclude_dates': exclude_dates}
            # 去除SQLAlchemy内部属性
            plan_dict.pop('_sa_instance_state', None)
            result.append(plan_dict)
        return result
    
    @staticmethod
    @auto_log("database", log_result=True)
    def get_dca_plan_by_id(db: Session, plan_id: int) -> Optional[dict]:
        """根据ID获取定投计划，返回dict，exclude_dates为list，ORM对象不被污染"""
        plan = db.query(DCAPlan).filter(DCAPlan.id == plan_id).first()
        if not plan:
            return None
        exclude_dates = []
        if plan.exclude_dates:
            try:
                exclude_dates = json.loads(plan.exclude_dates)
            except (json.JSONDecodeError, TypeError):
                exclude_dates = []
        plan_dict = {**plan.__dict__, 'exclude_dates': exclude_dates}
        plan_dict.pop('_sa_instance_state', None)
        return plan_dict
    
    @staticmethod
    def update_dca_plan(db: Session, plan_id: int, update_data: DCAPlanUpdate) -> Optional[DCAPlan]:
        """更新定投计划"""
        logger = logging.getLogger("dca_plan")
        logger.info(f"[日志] update_dca_plan called, plan_id={plan_id}, update_data={update_data}")
        plan = db.query(DCAPlan).filter(DCAPlan.id == plan_id).first()
        if not plan:
            logger.warning(f"[日志] update_dca_plan: plan_id={plan_id} not found")
            return None
        try:
            # 更新字段
            for field, value in update_data.dict(exclude_unset=True).items():
                if hasattr(plan, field):
                    if field == 'exclude_dates' and value is not None:
                        # 特殊处理exclude_dates字段，转换为JSON字符串
                        setattr(plan, field, json.dumps(value))
                    else:
                        logger.info(f"[日志] update_dca_plan: set {field}={value}")
                        setattr(plan, field, value)
            # 如果更新了频率、频率值或开始日期，重新计算下次执行日期
            if (update_data.frequency is not None or update_data.frequency_value is not None or update_data.start_date is not None):
                logger.info(f"[日志] update_dca_plan: recalculate next_execution_date")
                plan.next_execution_date = DCAService._calculate_next_execution_date(
                    plan.start_date,
                    plan.frequency,
                    plan.frequency_value
                )
            db.commit()
            db.refresh(plan)
            logger.info(f"[日志] update_dca_plan: commit success, plan_id={plan_id}")
            return plan
        except Exception as e:
            logger.error(f"[日志] update_dca_plan: exception {e}", exc_info=True)
            db.rollback()
            return None
    
    @staticmethod
    def delete_dca_plan(db: Session, plan_id: int) -> bool:
        """删除定投计划（不删除操作）"""
        plan = db.query(DCAPlan).filter(DCAPlan.id == plan_id).first()
        if not plan:
            return False
        db.delete(plan)
        db.commit()
        return True
    
    @staticmethod
    def delete_dca_plan_with_operations(db: Session, plan_id: int) -> bool:
        """删除定投计划及其所有关联操作记录"""
        from app.models.database import UserOperation
        plan = db.query(DCAPlan).filter(DCAPlan.id == plan_id).first()
        if not plan:
            return False
        # 删除所有关联操作
        db.query(UserOperation).filter(UserOperation.dca_plan_id == plan_id).delete()
        db.delete(plan)
        db.commit()
        return True
    
    @staticmethod
    def execute_dca_plan(db: Session, plan_id: int, execution_type: str = "scheduled") -> Optional[UserOperation]:
        """执行定投计划"""
        plan = db.query(DCAPlan).filter(DCAPlan.id == plan_id).first()
        if not plan or plan.status != "active":
            return None
        
        # 检查是否为历史定投计划（结束日期早于今天）
        today = date.today()
        if plan.end_date and plan.end_date < today:
            raise ValueError(f"历史定投计划（结束日期：{plan.end_date}）不能手动执行")
        
        # 计算定投金额
        if plan.smart_dca:
            amount = DCAService._calculate_smart_amount(db, plan)
        else:
            amount = plan.amount
        
        # 获取当天净值（如果存在）
        today = date.today()
        latest_nav = None
        nav_obj = db.query(FundNav).filter(
            and_(
                FundNav.fund_code == plan.asset_code,
                FundNav.nav_date == today
            )
        ).first()
        
        if nav_obj:
            latest_nav = nav_obj.nav
        
        # 计算手续费
        fee_rate = plan.fee_rate or 0
        fee = (amount * fee_rate).quantize(Decimal('0.0001')) if fee_rate else Decimal('0')
        
        # 创建操作记录（先不计算份额）
        operation = UserOperation(
            operation_date=datetime.now(),
            platform=plan.platform,
            asset_type=plan.asset_type,
            operation_type="buy",
            asset_code=plan.asset_code,
            asset_name=plan.asset_name,
            amount=amount,
            currency=plan.currency,
            quantity=None,  # 先不计算份额
            price=None,
            nav=latest_nav,  # 如果有净值就记录
            fee=fee,
            strategy=f"定投计划: {plan.plan_name}",
            dca_plan_id=plan.id,
            dca_execution_type=execution_type,
            status="pending" if latest_nav is None else "confirmed"
        )
        
        db.add(operation)
        db.commit()
        db.refresh(operation)
        
        # 如果有净值，立即计算份额并确认
        if latest_nav:
            DCAService._calculate_and_confirm_operation(db, operation, latest_nav)
        
        # 更新下次执行日期
        if plan.next_execution_date:
            # 基于当前执行日期计算下次执行日期
            next_execution_date = DCAService._calculate_next_execution_date(
                plan.next_execution_date,  # 使用当前执行日期作为基准
                plan.frequency,
                plan.frequency_value
            )
            plan.next_execution_date = next_execution_date
            db.commit()
        
        # 更新定投计划统计
        DCAService.update_plan_statistics(db, plan_id)
        
        return operation
    
    @staticmethod
    def _calculate_and_confirm_operation(db: Session, operation: UserOperation, nav: Decimal):
        """计算份额并确认操作"""
        # 计算份额：份额 = (金额 - 手续费) / 净值
        shares = (operation.amount - operation.fee) / nav
        operation.quantity = shares
        operation.price = nav
        operation.status = "confirmed"
        
        db.commit()
        db.refresh(operation)
        
        # 更新持仓
        FundOperationService._update_position(db, operation)
    
    @staticmethod
    def _update_plan_statistics(db: Session, plan_id: int):
        """手动更新定投计划统计信息"""
        plan = db.query(DCAPlan).filter(DCAPlan.id == plan_id).first()
        if not plan:
            return False
        
        # 重新计算计划统计信息
        operations = db.query(UserOperation).filter(
            UserOperation.dca_plan_id == plan_id
        ).all()
        
        plan.execution_count = len(operations)
        plan.total_invested = sum(op.amount for op in operations)
        plan.total_shares = sum(op.quantity for op in operations if op.quantity is not None)
        plan.last_execution_date = max(op.operation_date.date() for op in operations) if operations else None
        plan.updated_at = datetime.now()
        
        db.commit()
        return True
    
    @staticmethod
    def check_and_execute_dca_plans(db: Session) -> List[UserOperation]:
        """检查并执行到期的定投计划"""
        today = datetime.now().date()
        active_plans = DCAService.get_dca_plans(db, "active")
        
        print(f"[调试] 检查定投计划执行 - 今天: {today}")
        print(f"[调试] 找到 {len(active_plans)} 个活跃计划")
        
        executed_operations = []
        for plan in active_plans:
            # 使用字典键值访问，因为get_dca_plans返回的是字典列表
            next_execution_date = plan.get('next_execution_date')
            end_date = plan.get('end_date')
            plan_id = plan.get('id')
            start_date = plan.get('start_date')
            frequency = plan.get('frequency')
            frequency_value = plan.get('frequency_value')
            
            # 检查计划是否已过期
            # 对于已过期的计划，跳过执行，让用户在前端修改
            if end_date and end_date < today:
                print(f"[警告] 定投计划 {plan_id} 已过期 (结束日期: {end_date})，跳过执行")
                continue
            
            # 如果next_execution_date为null，说明是第一次运行，应该执行今天的定投
            if not next_execution_date:
                if start_date and frequency and frequency_value:
                    print(f"[信息] 计划 {plan_id} 是第一次运行，设置为今天执行")
                    # 设置为今天执行
                    next_execution_date = today
                else:
                    # 无法计算下次执行日期，跳过
                    print(f"[警告] 计划 {plan_id} 缺少必要信息，跳过")
                    continue
            
            # 检查是否应该执行
            print(f"[调试] 计划 {plan_id}: next_execution_date={next_execution_date}, end_date={end_date}")
            
            if (next_execution_date and 
                next_execution_date <= today and
                (not end_date or end_date >= today)):
                
                print(f"[调试] 执行计划 {plan_id}")
                operation = DCAService.execute_dca_plan(db, plan_id, "scheduled")
                if operation:
                    executed_operations.append(operation)
                    print(f"[调试] 计划 {plan_id} 执行成功")
                else:
                    print(f"[调试] 计划 {plan_id} 执行失败")
            else:
                print(f"[调试] 计划 {plan_id} 不满足执行条件")
        
        return executed_operations
    
    @staticmethod
    def _calculate_next_execution_date(start_date: date, frequency: str, frequency_value: int) -> date:
        """计算下次执行日期"""
        from datetime import timedelta
        
        if frequency == "daily":
            return start_date + timedelta(days=frequency_value)
        elif frequency == "weekly":
            return start_date + timedelta(weeks=frequency_value)
        elif frequency == "monthly":
            # 简单的月份计算，实际应该考虑月份天数差异
            year = start_date.year
            month = start_date.month + frequency_value
            while month > 12:
                year += 1
                month -= 12
            return date(year, month, start_date.day)
        else:
            return start_date + timedelta(days=frequency_value)
    
    @staticmethod
    def _calculate_smart_amount(db: Session, plan: DCAPlan) -> Decimal:
        """计算智能定投金额"""
        if not plan.smart_dca:
            return plan.amount
        
        # 获取最新净值
        latest_nav = FundNavService.get_latest_nav(db, plan.asset_code)
        if not latest_nav:
            return plan.amount
        
        # 获取历史净值数据（用于计算平均净值）
        nav_history = db.query(FundNav).filter(
            FundNav.fund_code == plan.asset_code
        ).order_by(FundNav.nav_date.desc()).limit(30).all()
        
        if not nav_history:
            return plan.amount
        
        # 计算平均净值
        avg_nav = sum(nav.nav for nav in nav_history) / len(nav_history)
        
        # 计算净值偏离度
        nav_deviation = (avg_nav - latest_nav) / avg_nav
        
        # 根据偏离度调整金额
        if nav_deviation > 0 and plan.increase_rate:  # 净值下跌
            increase_amount = plan.base_amount * nav_deviation * plan.increase_rate
            new_amount = plan.base_amount + increase_amount
            return min(new_amount, plan.max_amount) if plan.max_amount else new_amount
        else:
            return plan.base_amount or plan.amount
    
    @staticmethod
    @auto_log("database", log_result=True)
    def get_dca_statistics(db: Session, plan_id: int) -> dict:
        """获取定投计划统计信息"""
        print(f'[统计] 查询plan_id={plan_id}')
        plan = DCAService.get_dca_plan_by_id(db, plan_id)
        if not plan:
            print(f'[统计] 未找到定投计划 plan_id={plan_id}')
            return {}
        
        # 获取该计划的所有操作记录
        operations = db.query(UserOperation).filter(
            UserOperation.dca_plan_id == plan_id
        ).order_by(UserOperation.operation_date).all()
        print(f'[统计] 操作记录数: {len(operations)}')
        if not operations:
            print(f'[统计] 无操作记录，返回全为0')
            return {
                "plan_id": plan_id,
                "total_operations": 0,
                "total_invested": 0,
                "total_shares": 0,
                "avg_cost": 0,
                "current_value": 0,
                "total_profit": 0,
                "profit_rate": 0
            }
        
        total_invested = sum(float(op.amount or 0) for op in operations)
        total_shares = sum(float(op.quantity or 0) for op in operations)
        avg_cost = float(total_invested / total_shares) if total_shares else 0

        # 获取最新净值，修复为取nav字段
        latest_nav_obj = db.query(FundNav).filter(FundNav.fund_code == plan.asset_code).order_by(FundNav.nav_date.desc()).first()
        if latest_nav_obj:
            latest_nav = float(getattr(latest_nav_obj, 'nav', 0) or 0)
        else:
            latest_nav = 0.0
        print(f'[统计] latest_nav={latest_nav}')

        current_value = float(total_shares * latest_nav)
        total_profit = float(current_value - total_invested)
        profit_rate = float(total_profit / total_invested) if total_invested else 0

        print(f'[统计] total_invested={total_invested}')
        print(f'[统计] total_shares={total_shares}')
        print(f'[统计] avg_cost={avg_cost}')
        print(f'[统计] current_value={current_value}')
        print(f'[统计] total_profit={total_profit}')
        print(f'[统计] profit_rate={profit_rate}')

        return {
            "plan_id": plan_id,
            "total_operations": len(operations),
            "total_invested": total_invested,
            "total_shares": total_shares,
            "avg_cost": avg_cost,
            "current_value": current_value,
            "total_profit": total_profit,
            "profit_rate": profit_rate
        }

    @staticmethod
    def generate_historical_operations(db: Session, plan_id: int, end_date: Optional[date] = None, skip_holidays: bool = True, exclude_dates: Optional[List[date]] = None) -> int:
        """批量生成历史定投记录，支持排除指定日期"""
        print(f'[历史生成] plan_id={plan_id}, end_date={end_date}, exclude_dates原始值={exclude_dates}')
        plan = db.query(DCAPlan).filter(DCAPlan.id == plan_id).first()
        if not plan:
            print('[历史生成] 未找到定投计划')
            return 0
        
        if not end_date:
            end_date = plan.end_date or date.today()
        
        execution_dates = DCAService._calculate_execution_dates(
            plan.start_date, 
            end_date, 
            plan.frequency, 
            plan.frequency_value
        )
        print(f'[历史生成] 计算得到执行日期: {execution_dates}')
        
        # 强制转换exclude_dates为date类型
        exclude_set = set()
        if exclude_dates:
            print(f'[历史生成] 开始处理exclude_dates，原始类型: {type(exclude_dates)}')
            for d in exclude_dates:
                print(f'[历史生成] 处理排除日期: {d}, 类型: {type(d)}')
                if isinstance(d, date):
                    exclude_set.add(d)
                    print(f'[历史生成] 添加date类型: {d}')
                elif isinstance(d, str):
                    parsed_date = datetime.strptime(d, "%Y-%m-%d").date()
                    exclude_set.add(parsed_date)
                    print(f'[历史生成] 转换字符串并添加: {d} -> {parsed_date}')
                else:
                    # 兜底
                    parsed_date = date.fromisoformat(str(d))
                    exclude_set.add(parsed_date)
                    print(f'[历史生成] 兜底转换并添加: {d} -> {parsed_date}')
        
        print(f'[历史生成] 最终排除日期集合: {exclude_set}')
        print(f'[历史生成] 排除集合类型: {type(exclude_set)}')
        
        # 过滤掉排除的日期
        original_count = len(execution_dates)
        execution_dates = [d for d in execution_dates if d not in exclude_set]
        filtered_count = len(execution_dates)
        print(f'[历史生成] 过滤前日期数: {original_count}, 过滤后日期数: {filtered_count}')
        
        created_count = 0
        for exec_date in execution_dates:
            print(f'[历史生成] 处理日期: {exec_date}, 类型: {type(exec_date)}')
            print(f'[历史生成] 该日期是否在排除集合中: {exec_date in exclude_set}')
            
            # 检查是否已存在操作记录
            existing_operation = db.query(UserOperation).filter(
                UserOperation.dca_plan_id == plan_id,
                UserOperation.operation_date >= exec_date,
                UserOperation.operation_date < exec_date + timedelta(days=1)
            ).first()
            
            if existing_operation:
                print(f'[历史生成] 已存在操作记录，跳过: {exec_date}')
                continue
            
            # 获取净值
            nav_record = db.query(FundNav).filter(
                FundNav.fund_code == plan.asset_code,
                FundNav.nav_date == exec_date
            ).first()
            
            if not nav_record:
                print(f'[历史生成] 无净值，跳过 {exec_date}')
                continue
            
            # 计算手续费和份额
            fee = plan.amount * (plan.fee_rate or 0) / 100
            net_amount = plan.amount - fee
            quantity = net_amount / nav_record.nav
            
            # PostgreSQL序列修复：检查并重置序列
            try:
                max_id_result = db.execute(text("SELECT MAX(id) FROM user_operations"))
                max_id = max_id_result.scalar()
                
                if max_id is not None:
                    seq_result = db.execute(text("SELECT last_value FROM user_operations_id_seq"))
                    current_seq = seq_result.scalar()
                    
                    if current_seq < max_id:
                        print(f'[历史生成] 重置序列: 当前={current_seq}, 最大ID={max_id}')
                        db.execute(text(f"SELECT setval('user_operations_id_seq', {max_id})"))
                        db.commit()  # Commit sequence reset
                        print(f'[历史生成] 序列重置完成')
            except Exception as e:
                print(f'[历史生成] 序列检查失败: {e}')
            
            # 创建操作记录
            operation = UserOperation(
                operation_date=exec_date,
                platform=plan.platform,
                asset_type=plan.asset_type,
                operation_type='buy',
                asset_code=plan.asset_code,
                asset_name=plan.asset_name,
                amount=plan.amount,
                currency=plan.currency,
                quantity=quantity,
                nav=nav_record.nav,
                fee=fee,
                dca_plan_id=plan_id,
                dca_execution_type='historical',
                status='confirmed'
            )
            
            db.add(operation)
            db.commit()
            
            created_count += 1
            print(f'[历史生成] 成功创建操作记录: {exec_date}')
        
        print(f'[历史生成] 总共生成 {created_count} 条操作记录')
        return created_count

    @staticmethod
    def _calculate_execution_dates(start_date: date, end_date: date, frequency: str, frequency_value: int) -> List[date]:
        """计算执行日期列表"""
        dates = []
        current_date = start_date
        
        while current_date <= end_date:
            dates.append(current_date)
            
            if frequency == 'daily':
                current_date += timedelta(days=frequency_value)
            elif frequency == 'weekly':
                current_date += timedelta(weeks=frequency_value)
            elif frequency == 'monthly':
                # 简单的月份计算，实际应该考虑月末日期
                year = current_date.year
                month = current_date.month + frequency_value
                while month > 12:
                    year += 1
                    month -= 12
                try:
                    current_date = current_date.replace(year=year, month=month)
                except ValueError:
                    # 如果日期无效（如2月30日），使用月末
                    if month == 2:
                        current_date = current_date.replace(year=year, month=month, day=28)
                    else:
                        current_date = current_date.replace(year=year, month=month, day=30)
        
        return dates

    @staticmethod
    def update_plan_status(db: Session, plan_id: int) -> bool:
        """更新定投计划状态"""
        plan = db.query(DCAPlan).filter(DCAPlan.id == plan_id).first()
        if not plan:
            return False
        
        # 如果计划有结束日期且已过期，状态改为已完成
        if plan.end_date and plan.end_date < date.today():
            plan.status = 'completed'
            db.commit()
            return True
        
        return False

    @staticmethod
    def update_all_plan_statuses(db: Session) -> int:
        """批量更新所有定投计划状态"""
        updated_count = 0
        plans = db.query(DCAPlan).filter(DCAPlan.status == 'active').all()
        
        for plan in plans:
            if plan.end_date and plan.end_date < date.today():
                plan.status = 'completed'
                updated_count += 1
        
        if updated_count > 0:
            db.commit()
        
        return updated_count

    @staticmethod
    def delete_plan_operations(db: Session, plan_id: int) -> int:
        """删除定投计划的所有操作记录"""
        operations = db.query(UserOperation).filter(
            UserOperation.dca_plan_id == plan_id
        ).all()
        
        deleted_count = len(operations)
        for operation in operations:
            db.delete(operation)
        
        # 重置计划统计
        plan = db.query(DCAPlan).filter(DCAPlan.id == plan_id).first()
        if plan:
            plan.execution_count = 0
            plan.total_invested = Decimal('0')
            plan.total_shares = Decimal('0')
            plan.last_execution_date = None
            plan.updated_at = datetime.now()
        
        db.commit()
        return deleted_count

    @staticmethod
    def update_plan_statistics(db: Session, plan_id: int) -> bool:
        """手动更新定投计划统计信息"""
        plan = db.query(DCAPlan).filter(DCAPlan.id == plan_id).first()
        if not plan:
            return False
        
        # 重新计算计划统计信息
        operations = db.query(UserOperation).filter(
            UserOperation.dca_plan_id == plan_id
        ).all()
        
        plan.execution_count = len(operations)
        plan.total_invested = sum(op.amount for op in operations)
        plan.total_shares = sum(op.quantity for op in operations if op.quantity is not None)
        plan.last_execution_date = max(op.operation_date.date() for op in operations) if operations else None
        plan.updated_at = datetime.now()
        
        db.commit()
        return True

    @staticmethod
    def clean_plan_operations_by_date_range(db: Session, plan_id: int, start_date: date, end_date: date) -> int:
        """清理定投计划超出新区间的历史操作记录"""
        # 查找所有不在新区间内的操作记录
        operations_to_delete = db.query(UserOperation).filter(
            and_(
                UserOperation.dca_plan_id == plan_id,
                or_(
                    UserOperation.operation_date < start_date,
                    UserOperation.operation_date > end_date
                )
            )
        ).all()
        
        deleted_count = len(operations_to_delete)
        
        # 删除超出区间的操作记录
        for operation in operations_to_delete:
            db.delete(operation)
        
        # 重置计划统计
        plan = db.query(DCAPlan).filter(DCAPlan.id == plan_id).first()
        if plan:
            # 重新计算剩余操作的统计
            remaining_operations = db.query(UserOperation).filter(
                UserOperation.dca_plan_id == plan_id
            ).all()
            
            plan.execution_count = len(remaining_operations)
            plan.total_invested = sum(op.amount for op in remaining_operations)
            plan.total_shares = sum(op.quantity for op in remaining_operations if op.quantity is not None)
            plan.last_execution_date = max(op.operation_date.date() for op in remaining_operations) if remaining_operations else None
            
            # 如果没有历史操作了，状态改为active，但保持其他状态不变
            if len(remaining_operations) == 0:
                # 只有在状态为completed时才改为active
                if plan.status == 'completed':
                    plan.status = 'active'
            
            plan.updated_at = datetime.now()
        
        db.commit()
        return deleted_count

    @staticmethod
    def update_pending_operations(db: Session) -> int:
        """更新所有待确认的定投操作记录"""
        updated_count = 0
        
        # 查找所有待确认的定投操作
        pending_operations = db.query(UserOperation).filter(
            and_(
                UserOperation.status == "pending",
                UserOperation.dca_plan_id.isnot(None)
            )
        ).all()
        
        for operation in pending_operations:
            try:
                # 获取当天净值
                today = date.today()
                nav_record = db.query(FundNav).filter(
                    and_(
                        FundNav.fund_code == operation.asset_code,
                        FundNav.nav_date == today
                    )
                ).first()
                
                if nav_record:
                    # 计算份额并确认操作
                    DCAService._calculate_and_confirm_operation(db, operation, nav_record.nav)
                    updated_count += 1
                    
            except Exception as e:
                print(f"更新待确认操作 {operation.id} 失败: {e}")
                continue
        
        return updated_count

    @staticmethod
    def update_fund_nav(db: Session, fund_code: str, nav: Decimal, nav_date: date) -> bool:
        """更新或插入基金净值记录"""
        try:
            # 检查是否已存在当天的净值记录
            existing_nav = db.query(FundNav).filter(
                and_(
                    FundNav.fund_code == fund_code,
                    FundNav.nav_date == nav_date
                )
            ).first()
            
            if existing_nav:
                # 更新现有记录
                existing_nav.nav = nav
                existing_nav.updated_at = datetime.now()
            else:
                # 创建新记录
                new_nav = FundNav(
                    fund_code=fund_code,
                    nav_date=nav_date,
                    nav=nav,
                    source="scheduler"
                )
                db.add(new_nav)
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"更新基金 {fund_code} 净值失败: {e}")
            db.rollback()
            return False


class FundDividendService:
    """基金分红服务"""
    
    @staticmethod
    def create_dividend(db: Session, dividend_data: FundDividendCreate) -> FundDividend:
        """创建分红记录"""
        dividend = FundDividend(
            fund_code=dividend_data.fund_code,
            dividend_date=dividend_data.dividend_date,
            record_date=dividend_data.record_date,
            dividend_amount=dividend_data.dividend_amount,
            total_dividend=dividend_data.total_dividend,
            announcement_date=dividend_data.announcement_date
        )
        
        db.add(dividend)
        db.commit()
        db.refresh(dividend)
        return dividend
    
    @staticmethod
    @auto_log("database", log_result=True)
    def get_dividends_by_fund(db: Session, fund_code: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[FundDividend]:
        """获取基金的分红记录"""
        query = db.query(FundDividend).filter(FundDividend.fund_code == fund_code)
        
        if start_date:
            query = query.filter(FundDividend.dividend_date >= start_date)
        if end_date:
            query = query.filter(FundDividend.dividend_date <= end_date)
        
        return query.order_by(desc(FundDividend.dividend_date)).all()
    
    @staticmethod
    def save_dividend_data(db: Session, fund_code: str, dividend_data: List[dict]) -> int:
        """批量保存分红数据"""
        saved_count = 0
        
        for item in dividend_data:
            try:
                # 检查是否已存在相同的分红记录
                existing = db.query(FundDividend).filter(
                    and_(
                        FundDividend.fund_code == fund_code,
                        FundDividend.dividend_date == item['dividend_date']
                    )
                ).first()
                
                if existing:
                    continue  # 跳过已存在的记录
                
                # 创建新的分红记录
                dividend = FundDividend(
                    fund_code=fund_code,
                    dividend_date=item['dividend_date'],
                    record_date=item.get('record_date'),
                    dividend_amount=item['dividend_amount'],
                    total_dividend=item.get('total_dividend'),
                    announcement_date=item.get('announcement_date')
                )
                
                db.add(dividend)
                saved_count += 1
                
            except Exception as e:
                print(f"[调试] 保存分红记录失败: {e}")
                continue
        
        if saved_count > 0:
            db.commit()
        
        return saved_count 