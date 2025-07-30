from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from app.services.wise_api_service import WiseAPIService
from loguru import logger
from app.services.exchange_rate_service import ExchangeRateService
from app.models.database import WiseExchangeRate, WiseBalance, WiseTransaction
from app.utils.database import SessionLocal

router = APIRouter(prefix="/wise", tags=["Wise"])

class WiseRouter:
    def __init__(self):
        self.wise_service = WiseAPIService()
    
    async def _fetch_specific_currency_pair(
        self, 
        exchange_service: ExchangeRateService, 
        source: str, 
        target: str, 
        missing_from: date, 
        missing_to: date, 
        group: str
    ) -> Dict[str, Any]:
        """只获取特定币种对的缺失数据"""
        from datetime import datetime, timedelta
        
        logger.info(f"[智能同步] 获取特定币种对: {source}->{target}, 时间范围: {missing_from} 到 {missing_to}")
        
        # 计算查询范围：如果缺失范围很小，扩大查询范围以确保能获取到数据
        days_diff = (missing_to - missing_from).days
        
        if days_diff <= 1:
            # 如果缺失范围很小（1天或更少），扩大查询范围
            # 向前扩展3天，向后扩展3天，确保能获取到数据
            start_date = missing_from - timedelta(days=3)
            end_date = missing_to + timedelta(days=3)
            logger.info(f"[智能同步] 扩大查询范围: {start_date} 到 {end_date} (原范围: {missing_from} 到 {missing_to})")
        else:
            # 如果缺失范围较大，使用原始范围
            start_date = missing_from
            end_date = missing_to
        
        # 转换为datetime对象
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.min.time())
        
        # 获取汇率数据
        rates_data = await exchange_service._fetch_rates_with_date_range(source, target, start_datetime, end_datetime, group)
        
        if not rates_data:
            logger.warning(f"[智能同步] 币种对 {source}->{target} 无数据")
            return {
                'success': True,
                'total_inserted': 0,
                'total_updated': 0,
                'message': f'币种对 {source}->{target} 无数据'
            }
        
        logger.info(f"[智能同步] 获取到 {len(rates_data)} 条汇率数据")
        
        # 存储到数据库
        db = SessionLocal()
        total_inserted = 0
        total_updated = 0
        
        try:
            for rate_data in rates_data:
                rate = rate_data.get('rate')
                time_str = rate_data.get('time')
                
                if not rate or not time_str:
                    logger.warning(f"[智能同步] 跳过无效数据: rate={rate}, time={time_str}")
                    continue
                
                # 解析时间
                try:
                    from dateutil import parser
                    time_dt = parser.parse(time_str.strip())
                except Exception as e:
                    logger.error(f"[智能同步] 无法解析时间字符串: '{time_str}', 错误: {e}")
                    continue
                
                # 检查是否已存在
                existing_rate = db.query(WiseExchangeRate).filter(
                    WiseExchangeRate.source_currency == source,
                    WiseExchangeRate.target_currency == target,
                    WiseExchangeRate.time == time_dt
                ).first()
                
                if existing_rate:
                    # 更新现有记录
                    existing_rate.rate = rate
                    total_updated += 1
                    logger.debug(f"[智能同步] 更新汇率: {source}->{target} {time_dt}")
                else:
                    # 新增记录
                    try:
                        new_rate = WiseExchangeRate(
                            source_currency=source,
                            target_currency=target,
                            rate=rate,
                            time=time_dt,
                            created_at=datetime.utcnow()
                        )
                        db.add(new_rate)
                        db.commit()
                        total_inserted += 1
                        logger.debug(f"[智能同步] 新增汇率: {source}->{target} {time_dt}")
                    except Exception as e:
                        logger.error(f"[智能同步] 插入汇率失败: {source}->{target} {time_dt}, 错误: {e}")
                        db.rollback()
                        continue
            
            return {
                'success': True,
                'total_inserted': total_inserted,
                'total_updated': total_updated,
                'message': f'成功获取 {source}->{target} 数据: 新增 {total_inserted} 条，更新 {total_updated} 条'
            }
            
        except Exception as e:
            logger.error(f"[智能同步] 处理数据时发生错误: {e}")
            db.rollback()
            return {
                'success': False,
                'message': f'处理数据时发生错误: {e}'
            }
        finally:
            db.close()

# 创建路由器实例
wise_router = WiseRouter()

# 初始化Wise API服务
wise_service = WiseAPIService()


@router.get("/config")
async def get_wise_config():
    """获取Wise API配置信息"""
    try:
        config = await wise_service.get_config()
        return {
            "success": True,
            "data": config
        }
    except Exception as e:
        logger.error(f"获取Wise配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.get("/test")
async def test_wise_connection():
    """测试Wise API连接"""
    try:
        result = await wise_service.test_connection()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"测试Wise连接失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试连接失败: {str(e)}")


@router.get("/profiles")
async def get_wise_profiles():
    """获取Wise用户资料"""
    try:
        profiles = await wise_service.get_profile()
        if profiles is None:
            raise HTTPException(status_code=500, detail="获取用户资料失败")
        
        return {
            "success": True,
            "data": profiles
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Wise用户资料失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户资料失败: {str(e)}")


@router.get("/accounts/{profile_id}")
async def get_wise_accounts(profile_id: str):
    """获取指定用户的账户列表"""
    try:
        accounts = await wise_service.get_accounts(profile_id)
        if accounts is None:
            raise HTTPException(status_code=500, detail="获取账户列表失败")
        
        return {
            "success": True,
            "data": accounts
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Wise账户列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取账户列表失败: {str(e)}")


@router.get("/balance/{profile_id}/{account_id}")
async def get_wise_account_balance(profile_id: str, account_id: str):
    """获取指定账户的余额"""
    try:
        balance = await wise_service.get_account_balance(profile_id, account_id)
        if balance is None:
            raise HTTPException(status_code=500, detail="获取账户余额失败")
        
        return {
            "success": True,
            "data": balance
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Wise账户余额失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取账户余额失败: {str(e)}")


@router.get("/all-balances")
async def get_all_wise_balances():
    """获取所有账户余额"""
    try:
        balances = await wise_service.get_all_account_balances()
        return {
            "success": True,
            "data": balances,
            "count": len(balances) if balances else 0
        }
    except Exception as e:
        logger.error(f"获取Wise余额失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Wise余额失败: {str(e)}")


@router.get("/stored-balances")
async def get_stored_balances():
    """从数据库获取已存储的Wise余额数据（只取每个账户+币种最新快照）"""
    try:
        from app.models.database import WiseBalance
        from app.utils.database import SessionLocal
        from sqlalchemy import func, and_
        db = SessionLocal()
        try:
            subq = db.query(
                WiseBalance.account_id,
                WiseBalance.currency,
                func.max(WiseBalance.update_time).label('max_update_time')
            ).group_by(
                WiseBalance.account_id,
                WiseBalance.currency
            ).subquery()
            balances = db.query(WiseBalance).join(
                subq,
                and_(
                    WiseBalance.account_id == subq.c.account_id,
                    WiseBalance.currency == subq.c.currency,
                    WiseBalance.update_time == subq.c.max_update_time
                )
            ).all()
            balance_list = []
            for balance in balances:
                balance_list.append({
                    "account_id": balance.account_id,
                    "currency": balance.currency,
                    "available_balance": float(balance.available_balance),
                    "reserved_balance": float(balance.reserved_balance),
                    "cash_amount": float(balance.cash_amount),
                    "total_worth": float(balance.total_worth),
                    "type": balance.type,
                    "investment_state": balance.investment_state,
                    "creation_time": balance.creation_time.isoformat() if balance.creation_time else None,
                    "modification_time": balance.modification_time.isoformat() if balance.modification_time else None,
                    "visible": balance.visible,
                    "primary": balance.primary,
                    "update_time": balance.update_time.isoformat() if balance.update_time else None,
                    "created_at": balance.created_at.isoformat() if balance.created_at else None
                })
            return {
                "success": True,
                "data": balance_list,
                "count": len(balance_list),
                "source": "database"
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取存储的Wise余额数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取存储的Wise余额数据失败: {str(e)}")


@router.get("/transactions/{profile_id}/{account_id}")
async def get_wise_transactions(
    profile_id: str,
    account_id: str,
    limit: int = Query(50, ge=1, le=100, description="返回记录数量限制"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """获取指定账户的交易记录"""
    try:
        transactions = await wise_service.get_transactions(profile_id, account_id, limit, offset)
        if transactions is None:
            raise HTTPException(status_code=500, detail="获取交易记录失败")
        
        return {
            "success": True,
            "data": transactions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Wise交易记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取交易记录失败: {str(e)}")


@router.get("/recent-transactions")
async def get_recent_wise_transactions(
    days: int = Query(30, ge=1, le=365, description="获取最近几天的交易记录")
):
    """获取最近交易记录"""
    try:
        transactions = await wise_service.get_recent_transactions(days)
        return {
            "success": True,
            "data": transactions,
            "count": len(transactions) if transactions else 0,
            "days": days
        }
    except Exception as e:
        logger.error(f"获取Wise交易记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Wise交易记录失败: {str(e)}")


@router.get("/stored-transactions")
async def get_stored_transactions(
    limit: int = Query(100, ge=1, le=1000, description="返回记录数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    profile_id: str = Query(None, description="过滤特定profile"),
    account_id: str = Query(None, description="过滤特定账户"),
    from_date: str = Query(None, description="开始日期 (YYYY-MM-DD)"),
    to_date: str = Query(None, description="结束日期 (YYYY-MM-DD)")
):
    """从数据库获取已存储的Wise交易记录"""
    try:
        from app.models.database import WiseTransaction
        from app.utils.database import SessionLocal
        from datetime import datetime
        
        db = SessionLocal()
        try:
            query = db.query(WiseTransaction)
            
            # 添加过滤条件
            if profile_id:
                query = query.filter(WiseTransaction.profile_id == profile_id)
            if account_id:
                query = query.filter(WiseTransaction.account_id == account_id)
            
            # 添加时间范围过滤
            if from_date:
                try:
                    from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
                    query = query.filter(WiseTransaction.date >= from_datetime)
                except ValueError:
                    raise HTTPException(status_code=400, detail="开始日期格式错误，请使用YYYY-MM-DD格式")
            
            if to_date:
                try:
                    to_datetime = datetime.strptime(to_date, '%Y-%m-%d')
                    # 结束日期包含当天，所以加1天
                    to_datetime = to_datetime + timedelta(days=1)
                    query = query.filter(WiseTransaction.date < to_datetime)
                except ValueError:
                    raise HTTPException(status_code=400, detail="结束日期格式错误，请使用YYYY-MM-DD格式")
            
            # 按日期倒序排列
            query = query.order_by(WiseTransaction.date.desc())
            
            # 分页
            total_count = query.count()
            transactions = query.offset(offset).limit(limit).all()
            
            transaction_list = []
            for tx in transactions:
                transaction_list.append({
                    "profile_id": tx.profile_id,
                    "account_id": tx.account_id,
                    "transaction_id": tx.transaction_id,
                    "type": tx.type,
                    "amount": float(tx.amount),
                    "currency": tx.currency,
                    "description": tx.description,
                    "title": tx.title,
                    "date": tx.date.isoformat() if tx.date else None,
                    "status": tx.status,
                    "reference_number": tx.reference_number,
                    "created_at": tx.created_at.isoformat() if tx.created_at else None,
                    "updated_at": tx.updated_at.isoformat() if tx.updated_at else None,
                    # 新增字段
                    "primary_amount_value": float(tx.primary_amount_value) if tx.primary_amount_value is not None else None,
                    "primary_amount_currency": tx.primary_amount_currency,
                    "secondary_amount_value": float(tx.secondary_amount_value) if tx.secondary_amount_value is not None else None,
                    "secondary_amount_currency": tx.secondary_amount_currency
                })
            
            return {
                "success": True,
                "data": transaction_list,
                "count": len(transaction_list),
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "source": "database"
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取存储的Wise交易记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取存储的Wise交易记录失败: {str(e)}")


@router.get("/exchange-rates")
async def get_wise_exchange_rates(
    source: str = Query("USD", description="源货币"),
    target: str = Query("CNY", description="目标货币")
):
    """获取汇率信息"""
    try:
        rates = await wise_service.get_exchange_rates(source, target)
        if rates is None:
            raise HTTPException(status_code=500, detail="获取汇率信息失败")
        
        return {
            "success": True,
            "data": rates
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Wise汇率失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取汇率失败: {str(e)}")


@router.get("/historical-rates")
async def get_wise_historical_rates(
    source: str = Query("USD", description="源货币"),
    target: str = Query("CNY", description="目标货币"),
    from_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    to_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    interval: int = Query(24, ge=1, le=168, description="时间间隔(小时)")
):
    """获取历史汇率"""
    try:
        # 验证日期格式
        try:
            datetime.strptime(from_date, '%Y-%m-%d')
            datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")
        
        rates = await wise_service.get_historical_rates(source, target, from_date, to_date, interval)
        if rates is None:
            raise HTTPException(status_code=500, detail="获取历史汇率失败")
        
        return {
            "success": True,
            "data": rates
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Wise历史汇率失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取历史汇率失败: {str(e)}")


@router.get("/currencies")
async def get_wise_currencies():
    """获取可用货币列表"""
    try:
        currencies = await wise_service.get_available_currencies()
        if currencies is None:
            raise HTTPException(status_code=500, detail="获取货币列表失败")
        
        return {
            "success": True,
            "data": currencies
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Wise货币列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取货币列表失败: {str(e)}")


@router.get("/summary")
async def get_wise_summary():
    """获取Wise账户汇总信息"""
    try:
        # 获取所有余额
        balances = await wise_service.get_all_account_balances()
        # 过滤掉None和非dict、无account_id/currency的项
        balances = [b for b in balances if b and isinstance(b, dict) and b.get('account_id') and b.get('currency')]

        # 获取最近交易
        recent_transactions = await wise_service.get_recent_transactions(7)

        # 计算汇总信息
        total_balance_by_currency = {}
        for balance in balances:
            currency = balance['currency']
            if currency not in total_balance_by_currency:
                total_balance_by_currency[currency] = 0
            total_balance_by_currency[currency] += balance['available_balance']

        summary = {
            "total_accounts": len(set(b['account_id'] for b in balances)),
            "total_currencies": len(total_balance_by_currency),
            "balance_by_currency": total_balance_by_currency,
            "recent_transactions_count": len(recent_transactions),
            "last_updated": datetime.now().isoformat()
        }

        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        logger.error(f"获取Wise汇总信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取汇总信息失败: {str(e)}")


@router.get("/eligibility/{profile_id}")
async def get_multi_currency_eligibility(profile_id: str):
    """检查指定profile是否有资格开通多币种账户"""
    try:
        result = await wise_service.get_multi_currency_eligibility(profile_id)
        if result is None:
            raise HTTPException(status_code=500, detail="获取多币种账户资格失败")
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Wise多币种账户资格失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取多币种账户资格失败: {str(e)}")


@router.get("/balance-statement/{profile_id}/{balance_id}")
async def get_balance_statement(
    profile_id: str,
    balance_id: str,
    currency: str = Query("USD", description="货币代码"),
    interval_start: str = Query(None, description="开始时间 (ISO 8601格式)"),
    interval_end: str = Query(None, description="结束时间 (ISO 8601格式)"),
    statement_type: str = Query("COMPACT", description="对账单类型 (COMPACT/FLAT)")
):
    """获取指定账户的余额对账单"""
    try:
        result = await wise_service.get_balance_statement(
            profile_id, 
            balance_id, 
            currency, 
            interval_start, 
            interval_end, 
            statement_type
        )
        if result is None:
            raise HTTPException(status_code=500, detail="获取余额对账单失败")
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Wise余额对账单失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取余额对账单失败: {str(e)}")


@router.get("/all-balance-statements")
async def get_all_balance_statements(
    currency: str = Query("EUR", description="货币代码"),
    days: int = Query(30, ge=1, le=469, description="获取最近几天的数据")
):
    """获取所有账户的余额对账单"""
    try:
        statements = await wise_service.get_all_balance_statements(currency, days)
        return {
            "success": True,
            "data": statements,
            "count": len(statements),
            "currency": currency,
            "days": days
        }
    except Exception as e:
        logger.error(f"获取所有Wise余额对账单失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取所有余额对账单失败: {str(e)}")


@router.get("/balances/{profile_id}")
async def get_wise_balances(
    profile_id: str,
    types: str = Query("STANDARD", description="账户类型 (STANDARD, SAVINGS)")
):
    """获取指定profile的余额账户列表"""
    try:
        result = await wise_service.get_balances(profile_id, types)
        if result is None:
            raise HTTPException(status_code=500, detail="获取余额账户列表失败")
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Wise余额账户列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取余额账户列表失败: {str(e)}")


@router.get("/balance/{profile_id}/{balance_id}")
async def get_wise_balance_by_id(profile_id: str, balance_id: str):
    """获取指定余额账户的详细信息"""
    try:
        result = await wise_service.get_balance_by_id(profile_id, balance_id)
        if result is None:
            raise HTTPException(status_code=500, detail="获取余额账户详情失败")
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Wise余额账户详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取余额账户详情失败: {str(e)}")


@router.post("/create-balance")
async def create_wise_balance(
    profile_id: str,
    currency: str,
    balance_type: str = Query("STANDARD", description="账户类型 (STANDARD, SAVINGS)"),
    name: str = Query(None, description="账户名称 (SAVINGS类型必需)")
):
    """创建新的余额账户"""
    try:
        result = await wise_service.create_balance(profile_id, currency, balance_type, name)
        if result is None:
            raise HTTPException(status_code=500, detail="创建余额账户失败")
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建Wise余额账户失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建余额账户失败: {str(e)}")


@router.get("/test-aud-transactions")
async def test_aud_transactions():
    """测试AUD账户交易记录"""
    try:
        result = await wise_service.test_aud_transactions()
        if result is None:
            raise HTTPException(status_code=500, detail="测试AUD交易记录失败")
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试AUD交易记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试AUD交易记录失败: {str(e)}")


@router.get("/debug-logs")
async def get_debug_logs():
    """获取最近的Wise调试日志"""
    try:
        # 这里只是返回一个简单的状态信息
        # 实际的日志查看需要更复杂的实现
        return {
            "success": True,
            "message": "请查看后端控制台输出获取详细日志",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取调试日志失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取调试日志失败: {str(e)}")


@router.get("/profile-activities/{profile_id}")
async def get_profile_activities(
    profile_id: str,
    limit: int = Query(100, description="限制数量"),
    offset: int = Query(0, description="偏移量")
):
    """获取用户所有活动记录"""
    try:
        result = await wise_service.get_profile_activities(profile_id, limit, offset)
        if result is None:
            raise HTTPException(status_code=500, detail="获取用户活动记录失败")
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户活动记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户活动记录失败: {str(e)}")


@router.post("/sync-transactions")
async def sync_transactions(request: Request):
    """主动同步Wise所有交易记录到数据库"""
    try:
        body = await request.json()
        days = body.get("days", 90)
        result = await wise_service.sync_all_transactions_to_db(days=days)
        return result
    except Exception as e:
        logger.error(f"同步Wise交易记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步Wise交易记录失败: {str(e)}")


@router.post("/sync-balances")
async def sync_balances():
    """主动同步Wise所有余额数据到数据库"""
    try:
        result = await wise_service.sync_balances_to_db()
        return result
    except Exception as e:
        logger.error(f"同步Wise余额数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步Wise余额数据失败: {str(e)}")


@router.post("/exchange-rates/fetch-history")
async def fetch_and_store_exchange_rate_history(days: int = 365, group: str = 'day'):
    """拉取并存储持有币种对的历史汇率（全量更新）"""
    # 获取当前持有币种
    balances = await wise_service.get_all_account_balances()
    currencies = list({b['currency'] for b in balances if b and 'currency' in b})
    # 获取token
    token = wise_service.api_token
    service = ExchangeRateService(token)
    await service.fetch_and_store_history(currencies, days=days, group=group)
    return {"success": True, "msg": f"已拉取并存储{len(currencies)}币种的历史汇率"}


@router.post("/exchange-rates/fetch-history-incremental")
async def fetch_and_store_exchange_rate_history_incremental(group: str = 'day'):
    """增量拉取并存储持有币种对的历史汇率（增量更新）"""
    # 获取当前持有币种
    balances = await wise_service.get_all_account_balances()
    currencies = list({b['currency'] for b in balances if b and 'currency' in b})
    # 获取token
    token = wise_service.api_token
    service = ExchangeRateService(token)
    result = await service.fetch_and_store_history_incremental(currencies, group=group)
    return result


@router.get("/exchange-rates/history")
async def get_exchange_rate_history(
    source: str = Query(...),
    target: str = Query(...),
    from_time: str = Query(None),
    to_time: str = Query(None),
    group: str = Query('day')
):
    """查询历史汇率，支持币种对、时间区间、分组"""
    db = SessionLocal()
    q = db.query(WiseExchangeRate).filter(
        WiseExchangeRate.source_currency == source,
        WiseExchangeRate.target_currency == target
    )
    if from_time:
        q = q.filter(WiseExchangeRate.time >= from_time)
    if to_time:
        q = q.filter(WiseExchangeRate.time <= to_time)
    q = q.order_by(WiseExchangeRate.time.asc())
    data = [
        {
            "rate": r.rate,
            "time": r.time.isoformat(),
            "source": r.source_currency,
            "target": r.target_currency
        }
        for r in q.all()
    ]
    db.close()
    return {"success": True, "data": data} 


@router.post("/exchange-rates/smart-sync")
async def smart_sync_exchange_rates(
    source: str = Query(..., description="源货币"),
    target: str = Query(..., description="目标货币"),
    from_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    to_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    group: str = Query('day', description="数据分组")
):
    """
    智能同步汇率数据
    1. 检查数据库中指定时间范围的数据
    2. 如果数据不完整，从API获取所有币种对的缺失数据并保存到数据库
    3. 返回指定币种对的完整数据库数据
    """
    try:
        logger.info(f"开始智能同步汇率: {source}->{target}, 时间范围: {from_date} 到 {to_date}")
        
        # 1. 检查数据库中的现有数据
        db = SessionLocal()
        try:
            # 转换日期格式
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            # 将结束日期设置为当天的最后一刻，确保包含结束日期当天的所有数据
            to_dt = to_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # 查询数据库中指定币种对的现有数据
            existing_records = db.query(WiseExchangeRate).filter(
                WiseExchangeRate.source_currency == source,
                WiseExchangeRate.target_currency == target,
                WiseExchangeRate.time >= from_dt,
                WiseExchangeRate.time <= to_dt
            ).order_by(WiseExchangeRate.time).all()
            
            # 获取现有数据的日期集合
            existing_dates = set()
            for record in existing_records:
                existing_dates.add(record.time.date())
            
            # 计算需要的日期范围
            required_dates = set()
            current_date = from_dt.date()
            while current_date <= to_dt.date():
                required_dates.add(current_date)
                current_date += timedelta(days=1)
            
            # 找出缺失的日期
            missing_dates = required_dates - existing_dates
            
            logger.info(f"数据库现有数据: {len(existing_records)} 条")
            logger.info(f"需要的数据日期: {len(required_dates)} 天")
            logger.info(f"缺失的日期: {len(missing_dates)} 天")
            logger.info(f"查询条件: source={source}, target={target}, from_dt={from_dt}, to_dt={to_dt}")
            logger.info(f"现有数据日期: {sorted(list(existing_dates))}")
            logger.info(f"需要的数据日期: {sorted(list(required_dates))}")
            logger.info(f"缺失的日期: {sorted(list(missing_dates))}")
            
            # 2. 如果有缺失数据，从API获取特定币种对的缺失数据
            if missing_dates:
                logger.info(f"发现缺失数据，从API获取特定币种对 {source}->{target} 的缺失数据: {missing_dates}")
                
                # 初始化汇率服务
                exchange_service = ExchangeRateService(wise_service.api_token)
                
                # 计算缺失数据的时间范围
                missing_from = min(missing_dates)
                missing_to = max(missing_dates)
                days_to_fetch = (missing_to - missing_from).days + 1
                
                logger.info(f"获取缺失数据: {source}->{target}, 时间范围: {missing_from} 到 {missing_to}, 天数: {days_to_fetch}")
                
                # 只获取查询的币种对的缺失数据
                # 使用自定义方法只获取特定币种对
                sync_result = await wise_router._fetch_specific_currency_pair(
                    exchange_service, source, target, missing_from, missing_to, group
                )
                
                if not sync_result.get('success', False):
                    logger.error(f"API同步失败: {sync_result.get('message', '未知错误')}")
                    raise HTTPException(
                        status_code=500, 
                        detail=f"API同步失败: {sync_result.get('message', '未知错误')}"
                    )
                
                logger.info(f"API同步成功: 新增 {sync_result.get('total_inserted', 0)} 条，更新 {sync_result.get('total_updated', 0)} 条")
                
                # 重新查询数据库获取完整数据
                existing_records = db.query(WiseExchangeRate).filter(
                    WiseExchangeRate.source_currency == source,
                    WiseExchangeRate.target_currency == target,
                    WiseExchangeRate.time >= from_dt,
                    WiseExchangeRate.time <= to_dt
                ).order_by(WiseExchangeRate.time).all()
            else:
                logger.info("数据库数据完整，无需从API获取")
            
            # 3. 返回完整的数据
            result_data = []
            for record in existing_records:
                result_data.append({
                    "time": record.time.isoformat(),
                    "rate": record.rate,
                    "source_currency": record.source_currency,
                    "target_currency": record.target_currency
                })
            
            return {
                "success": True,
                "message": f"智能同步完成，共获取 {len(result_data)} 条汇率数据",
                "data": result_data,
                "total_records": len(result_data),
                "missing_dates_count": len(missing_dates) if 'missing_dates' in locals() else 0,
                "synced_from_api": len(missing_dates) > 0 if 'missing_dates' in locals() else False
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"智能同步汇率失败: {e}")
        raise HTTPException(status_code=500, detail=f"智能同步失败: {str(e)}") 