from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.services.okx_api_service import OKXAPIService
from app.services.web3_api_service import Web3APIService
from loguru import logger
from app.models.database import OKXBalance, OKXTransaction, OKXPosition, OKXMarketData, Web3Balance, Web3Token, Web3Transaction
from app.utils.database import SessionLocal
import time

router = APIRouter(prefix="/okx", tags=["OKX API"])

# 初始化OKX API服务
okx_service = OKXAPIService()
web3_service = Web3APIService()


@router.get("/summary")
async def get_okx_summary():
    """获取OKX账户汇总信息"""
    try:
        db = SessionLocal()
        try:
            # 获取余额汇总
            balances = db.query(OKXBalance).all()
            total_balance_by_currency = {}
            for balance in balances:
                currency = balance.currency
                if currency not in total_balance_by_currency:
                    total_balance_by_currency[currency] = 0
                total_balance_by_currency[currency] += float(balance.total_balance)
            
            # 获取最新持仓数据
            latest_positions = db.query(OKXPosition).order_by(OKXPosition.timestamp.desc()).limit(100).all()
            position_count = len(latest_positions)
            total_unrealized_pnl = sum(float(pos.unrealized_pnl) for pos in latest_positions)
            total_realized_pnl = sum(float(pos.realized_pnl) for pos in latest_positions)
            
            # 获取最新交易记录
            latest_transactions = db.query(OKXTransaction).order_by(OKXTransaction.timestamp.desc()).limit(100).all()
            transaction_count_24h = len([tx for tx in latest_transactions 
                                       if (datetime.now() - tx.timestamp).days <= 1])
            
            # 获取最新市场数据
            latest_market_data = db.query(OKXMarketData).order_by(OKXMarketData.timestamp.desc()).limit(10).all()
            
            return {
                "success": True,
                "data": {
                    "total_balance_by_currency": total_balance_by_currency,
                    "position_count": position_count,
                    "transaction_count_24h": transaction_count_24h,
                    "unrealized_pnl": total_unrealized_pnl,
                    "realized_pnl": total_realized_pnl,
                    "latest_market_data_count": len(latest_market_data),
                    "last_update": datetime.now().isoformat(),
                    "source": "database"
                }
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取OKX汇总信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取汇总信息失败: {str(e)}")


@router.get("/test")
async def test_okx_connection():
    """测试OKX API连接"""
    try:
        # 测试公共API（不需要认证）
        public_test = await okx_service.get_all_tickers('SPOT')
        
        # 测试私有API（需要认证）
        private_test = None
        private_error = None
        try:
            private_test = await okx_service.get_account_balance()
        except Exception as e:
            private_error = str(e)
        
        return {
            "success": True,
            "data": {
                "public_api": public_test is not None,
                "private_api": private_test is not None,
                "private_error": private_error,
                "timestamp": int(time.time() * 1000)
            }
        }
    except Exception as e:
        logger.error(f"测试OKX连接失败: {e}")
        return {
            "success": False,
            "data": {
                "public_api": False,
                "private_api": False,
                "error": str(e),
                "timestamp": int(time.time() * 1000)
            }
        }


@router.get("/config")
async def get_okx_config():
    """获取OKX API配置信息"""
    try:
        config = await okx_service.get_config()
        return {
            "success": True,
            "data": config
        }
    except Exception as e:
        logger.error(f"获取OKX配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.get("/account")
async def get_okx_account():
    """获取OKX账户资产信息"""
    try:
        result = await okx_service.get_account_balance()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"获取OKX账户信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取账户信息失败: {str(e)}")


@router.get("/positions")
async def get_okx_positions():
    """获取OKX持仓信息"""
    try:
        result = await okx_service.get_account_positions()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"获取OKX持仓信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取持仓信息失败: {str(e)}")


@router.get("/bills")
async def get_okx_bills(limit: int = Query(100, ge=1, le=1000)):
    """获取OKX账单归档流水"""
    try:
        result = await okx_service.get_bills_archive(limit=limit)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"获取OKX账单归档流水失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取账单归档流水失败: {str(e)}")


@router.get("/ticker")
async def get_okx_ticker(inst_id: str = Query(..., description="产品ID")):
    """获取OKX单个币种行情"""
    try:
        result = await okx_service.get_ticker(inst_id)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"获取OKX行情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取行情失败: {str(e)}")


@router.get("/tickers")
async def get_okx_all_tickers(inst_type: str = Query('SPOT', description="产品类型")):
    """获取OKX所有币种行情"""
    try:
        result = await okx_service.get_all_tickers(inst_type)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"获取OKX所有行情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取所有行情失败: {str(e)}")


@router.get("/instruments")
async def get_okx_instruments(inst_type: str = Query('SPOT', description="产品类型")):
    """获取OKX交易产品信息"""
    try:
        result = await okx_service.get_instruments(inst_type)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"获取OKX交易产品信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取交易产品信息失败: {str(e)}")


@router.get("/asset-balances")
async def get_okx_asset_balances():
    """获取OKX资金账户余额"""
    try:
        result = await okx_service.get_asset_balances()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"获取OKX资金账户余额失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取资金账户余额失败: {str(e)}")


@router.get("/savings-balance")
async def get_okx_savings_balance():
    """获取OKX储蓄账户余额"""
    try:
        result = await okx_service.get_savings_balance()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"获取OKX储蓄账户余额失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取储蓄账户余额失败: {str(e)}")


@router.post("/sync-balances")
async def sync_okx_balances():
    """主动同步OKX余额数据到数据库"""
    try:
        result = await okx_service.sync_balances_to_db()
        return result
    except Exception as e:
        logger.error(f"同步OKX余额数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步OKX余额数据失败: {str(e)}")


@router.post("/sync-transactions")
async def sync_okx_transactions(days: int = Query(30, ge=1, le=365)):
    """主动同步OKX交易记录到数据库"""
    try:
        logger.info(f"[入口日志] 调用sync_okx_transactions, days={days}")
        result = await okx_service.sync_transactions_to_db(days)
        logger.info(f"[入口日志] sync_transactions_to_db返回: {result}")
        return result
    except Exception as e:
        import traceback
        logger.error(f"同步OKX交易记录失败: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"同步OKX交易记录失败: {str(e)}")


@router.post("/sync-positions")
async def sync_okx_positions():
    """主动同步OKX持仓数据到数据库"""
    try:
        result = await okx_service.sync_positions_to_db()
        return result
    except Exception as e:
        logger.error(f"同步OKX持仓数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步OKX持仓数据失败: {str(e)}")


@router.post("/sync-market-data")
async def sync_okx_market_data(inst_ids: List[str] = Query(None, description="产品ID列表")):
    """主动同步OKX市场数据到数据库"""
    try:
        result = await okx_service.sync_market_data_to_db(inst_ids)
        return result
    except Exception as e:
        logger.error(f"同步OKX市场数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步OKX市场数据失败: {str(e)}")


@router.post("/sync-account-overview")
async def sync_okx_account_overview():
    """同步OKX账户总览数据到数据库"""
    try:
        # 获取账户总览数据
        overview_data = await get_okx_account_overview()
        
        if not overview_data.get("success"):
            return {"success": False, "message": "获取账户总览数据失败"}
        
        data = overview_data["data"]
        
        # 保存到数据库
        db = SessionLocal()
        try:
            from app.models.database import OKXAccountOverview
            
            # 创建新的总览记录
            overview_record = OKXAccountOverview(
                trading_total_usd=data["trading_account"]["total_equity_usd"],
                funding_total_usd=data["funding_account"]["total_balance_usd"],
                savings_total_usd=data["savings_account"]["total_balance_usd"],
                total_assets_usd=data["total_overview"]["total_assets_usd"],
                total_currencies=data["total_overview"]["total_currencies"],
                trading_currencies_count=data["trading_account"]["count"],
                funding_currencies_count=data["funding_account"]["count"],
                savings_currencies_count=data["savings_account"]["count"],
                last_update=datetime.now(),
                data_source="api"
            )
            
            db.add(overview_record)
            db.commit()
            
            return {
                "success": True,
                "message": "账户总览数据同步成功",
                "data": {
                    "total_assets_usd": data["total_overview"]["total_assets_usd"],
                    "total_currencies": data["total_overview"]["total_currencies"],
                    "trading_account": data["trading_account"]["total_equity_usd"],
                    "funding_account": data["funding_account"]["total_balance_usd"],
                    "savings_account": data["savings_account"]["total_balance_usd"],
                    "sync_time": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"保存账户总览数据失败: {e}")
            return {"success": False, "message": f"保存数据失败: {str(e)}"}
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"同步OKX账户总览失败: {str(e)}")
        return {"success": False, "message": f"同步失败: {str(e)}"}


@router.get("/stored-balances")
async def get_stored_balances():
    """从数据库获取已存储的OKX余额数据（只取最新快照，余额大于0）"""
    try:
        db = SessionLocal()
        try:
            from sqlalchemy import func, desc
            from app.models.database import OKXBalance
            subq = db.query(
                OKXBalance.account_id,
                OKXBalance.currency,
                OKXBalance.account_type,
                func.max(OKXBalance.update_time).label('max_update_time')
            ).group_by(
                OKXBalance.account_id,
                OKXBalance.currency,
                OKXBalance.account_type
            ).subquery()
            balances = db.query(OKXBalance).join(
                subq,
                (OKXBalance.account_id == subq.c.account_id) &
                (OKXBalance.currency == subq.c.currency) &
                (OKXBalance.account_type == subq.c.account_type) &
                (OKXBalance.update_time == subq.c.max_update_time)
            ).filter(OKXBalance.total_balance > 0).all()
            balance_list = []
            for balance in balances:
                balance_list.append({
                    "account_id": balance.account_id,
                    "currency": balance.currency,
                    "available_balance": float(balance.available_balance),
                    "frozen_balance": float(balance.frozen_balance),
                    "total_balance": float(balance.total_balance),
                    "account_type": balance.account_type,
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
        logger.error(f"获取存储的OKX余额数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取存储的OKX余额数据失败: {str(e)}")


@router.get("/stored-positions")
async def get_stored_positions():
    """从数据库获取已存储的OKX持仓数据"""
    try:
        db = SessionLocal()
        try:
            positions = db.query(OKXPosition).order_by(OKXPosition.timestamp.desc()).limit(100).all()
            position_list = []
            for position in positions:
                position_list.append({
                    "account_id": position.account_id,
                    "inst_type": position.inst_type,
                    "inst_id": position.inst_id,
                    "position_side": position.position_side,
                    "position_id": position.position_id,
                    "quantity": float(position.quantity),
                    "avg_price": float(position.avg_price),
                    "unrealized_pnl": float(position.unrealized_pnl),
                    "realized_pnl": float(position.realized_pnl),
                    "margin_ratio": float(position.margin_ratio) if position.margin_ratio else None,
                    "leverage": float(position.leverage) if position.leverage else None,
                    "mark_price": float(position.mark_price) if position.mark_price else None,
                    "liquidation_price": float(position.liquidation_price) if position.liquidation_price else None,
                    "currency": position.currency,
                    "timestamp": position.timestamp.isoformat() if position.timestamp else None,
                    "created_at": position.created_at.isoformat() if position.created_at else None
                })
            
            return {
                "success": True,
                "data": position_list,
                "count": len(position_list),
                "source": "database"
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取存储的OKX持仓数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取存储的OKX持仓数据失败: {str(e)}")


@router.get("/stored-transactions")
async def get_stored_transactions(
    limit: int = Query(100, ge=1, le=1000, description="返回记录数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    account_id: str = Query(None, description="过滤特定账户"),
    inst_id: str = Query(None, description="过滤特定产品"),
    from_date: str = Query(None, description="开始日期 (YYYY-MM-DD)"),
    to_date: str = Query(None, description="结束日期 (YYYY-MM-DD)")
):
    """从数据库获取已存储的OKX交易记录"""
    try:
        db = SessionLocal()
        try:
            query = db.query(OKXTransaction)
            
            if account_id:
                query = query.filter(OKXTransaction.account_id == account_id)
            if inst_id:
                query = query.filter(OKXTransaction.inst_id == inst_id)
            if from_date:
                query = query.filter(OKXTransaction.timestamp >= from_date)
            if to_date:
                query = query.filter(OKXTransaction.timestamp <= to_date + " 23:59:59")
            
            total = query.count()
            transactions = query.order_by(OKXTransaction.timestamp.desc()).offset(offset).limit(limit).all()
            
            type_desc_map = {
                '1': '划转',
                '2': '交易',
                '3': '交割',
                '4': '自动换币',
                '5': '强平',
                '6': '保证金划转',
                '7': '扣息',
                '8': '资金费',
                '9': '自动减仓',
                '10': '穿仓补偿',
                '11': '系统换币',
                '12': '策略划拨',
                '13': '对冲减仓',
                '14': '大宗交易',
                '15': '一键借币',
                '16': '借币',
                '22': '一键还债',
                '24': '价差交易',
                '26': '结构化产品',
                '27': '闪兑',
                '28': '小额兑换',
                '29': '一键还债',
                '30': '简单交易',
                '32': '移仓',
                '33': '借贷',
                '34': '结算',
                '250': '跟单人分润支出',
                '251': '跟单人分润退还',
            }
            sub_type_desc_map = {
                '1': '买入', '2': '卖出', '3': '开多', '4': '开空', '5': '平多', '6': '平空', '9': '市场借币扣息', '11': '转入', '12': '转出', '14': '尊享借币扣息',
                '16': '强制还币', '17': '强制借币还息', '100': '强减平多', '101': '强减平空', '102': '强减买入', '103': '强减卖出', '104': '强平平多', '105': '强平平空',
                '106': '强平买入', '107': '强平卖出', '108': '穿仓补偿', '110': '强平换币转入', '111': '强平换币转出', '112': '交割平多', '113': '交割平空',
                '114': '自动换币买入', '115': '自动换币卖出', '118': '系统换币转入', '119': '系统换币转出', '125': '自动减仓平多', '126': '自动减仓平空',
                '127': '自动减仓买入', '128': '自动减仓卖出', '131': '对冲买入', '132': '对冲卖出', '160': '手动追加保证金', '161': '手动减少保证金',
                '162': '自动追加保证金', '170': '到期行权（实值期权买方）', '171': '到期被行权（实值期权卖方）', '172': '到期作废（非实值期权的买方和卖方）',
                '173': '资金费支出', '174': '资金费收入', '200': '系统转入', '201': '手动转入', '202': '系统转出', '203': '手动转出',
                '204': '大宗交易买', '205': '大宗交易卖', '206': '大宗交易开多', '207': '大宗交易开空', '208': '大宗交易平多', '209': '大宗交易平空',
                '210': '一键借币的手动借币', '211': '一键借币的手动还币', '212': '一键借币的自动借币', '213': '一键借币的自动还币',
                '220': 'USDT 买期权转入', '221': 'USDT 买期权转出', '224': '一键还债买入', '225': '一键还债卖出',
                '236': '小额兑换买入', '237': '小额兑换卖出', '250': '永续分润支出', '251': '永续分润退还', '270': '价差交易买', '271': '价差交易卖',
                '272': '价差交易开多', '273': '价差交易开空', '274': '价差交易平多', '275': '价差交易平空', '280': '现货分润支出', '281': '现货分润退还',
                '284': '跟单自动转入', '285': '跟单手动转入', '286': '跟单自动转出', '287': '跟单手动转出', '290': '系统转出小额资产',
                '293': '固定借币扣息', '294': '固定借币利息退款', '295': '固定借币逾期利息', '296': '结构化下单转出', '297': '结构化下单转入',
                '298': '结构化结算转出', '299': '结构化结算转入', '306': '手动借币', '307': '自动借币', '308': '手动还币', '309': '自动还币',
                '312': '自动折抵', '318': '闪兑买入', '319': '闪兑卖出', '320': '简单交易买入', '321': '简单交易卖出',
                '324': '移仓买入', '325': '移仓卖出', '326': '移仓开多', '327': '移仓开空', '328': '移仓平多', '329': '移仓平空',
                '332': '逐仓杠杆仓位转入保证金', '333': '逐仓杠杆仓位转出保证金', '334': '逐仓杆仓位保证金平仓消耗', '355': '结算盈亏',
                '376': '质押借币超限买入', '377': '质押借币超限卖出', '381': '自动出借利息转入'
            }
            transaction_list = []
            for tx in transactions:
                type_desc = type_desc_map.get(str(tx.type), '未知')
                sub_type = getattr(tx, 'sub_type', None)
                sub_type_desc = sub_type_desc_map.get(str(sub_type), '未知') if sub_type else None
                transaction_list.append({
                    "transaction_id": tx.transaction_id,
                    "account_id": tx.account_id,
                    "inst_type": tx.inst_type,
                    "inst_id": tx.inst_id,
                    "trade_id": tx.trade_id,
                    "order_id": tx.order_id,
                    "bill_id": tx.bill_id,
                    "type": tx.type,
                    "type_desc": type_desc,
                    "sub_type": sub_type,
                    "sub_type_desc": sub_type_desc,
                    "side": tx.side,
                    "amount": float(tx.amount),
                    "currency": tx.currency,
                    "fee": float(tx.fee),
                    "fee_currency": tx.fee_currency,
                    "price": float(tx.price) if tx.price else None,
                    "quantity": float(tx.quantity) if tx.quantity else None,
                    "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
                    "created_at": tx.created_at.isoformat() if tx.created_at else None
                })
            
            return {
                "success": True,
                "data": transaction_list,
                "total": total,
                "count": len(transaction_list),
                "page": offset // limit + 1,
                "page_size": limit,
                "source": "database"
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取存储的OKX交易记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取存储的OKX交易记录失败: {str(e)}")


@router.get("/stored-market-data")
async def get_stored_market_data(
    inst_id: str = Query(None, description="产品ID"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数量限制")
):
    """从数据库获取已存储的OKX市场数据"""
    try:
        db = SessionLocal()
        try:
            query = db.query(OKXMarketData)
            
            if inst_id:
                query = query.filter(OKXMarketData.inst_id == inst_id)
            
            market_data = query.order_by(OKXMarketData.timestamp.desc()).limit(limit).all()
            
            data_list = []
            for data in market_data:
                data_list.append({
                    "inst_id": data.inst_id,
                    "inst_type": data.inst_type,
                    "last_price": float(data.last_price),
                    "bid_price": float(data.bid_price) if data.bid_price else None,
                    "ask_price": float(data.ask_price) if data.ask_price else None,
                    "high_24h": float(data.high_24h) if data.high_24h else None,
                    "low_24h": float(data.low_24h) if data.low_24h else None,
                    "volume_24h": float(data.volume_24h) if data.volume_24h else None,
                    "change_24h": float(data.change_24h) if data.change_24h else None,
                    "change_rate_24h": float(data.change_rate_24h) if data.change_rate_24h else None,
                    "timestamp": data.timestamp.isoformat() if data.timestamp else None,
                    "created_at": data.created_at.isoformat() if data.created_at else None
                })
            
            return {
                "success": True,
                "data": data_list,
                "count": len(data_list),
                "source": "database"
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取存储的OKX市场数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取存储的OKX市场数据失败: {str(e)}")


@router.get("/account-overview")
async def get_okx_account_overview():
    """获取OKX账户总览（合并交易、资金、储蓄账户）"""
    try:
        # 1. 获取交易账户数据
        trading_data = await okx_service.get_account_balance()
        
        # 2. 获取资金账户数据
        funding_data = await okx_service.get_asset_balances()
        
        # 3. 获取储蓄账户数据
        savings_data = await okx_service.get_savings_balance()
        
        # 4. 合并数据
        overview = {
            "trading_account": {
                "total_equity_usd": 0,
                "currencies": [],
                "count": 0
            },
            "funding_account": {
                "total_balance_usd": 0,
                "currencies": [],
                "count": 0
            },
            "savings_account": {
                "total_balance_usd": 0,
                "currencies": [],
                "count": 0
            },
            "total_overview": {
                "total_assets_usd": 0,
                "total_currencies": 0,
                "last_update": datetime.now().isoformat()
            }
        }
        
        # 处理交易账户数据
        if trading_data and trading_data.get("code") == "0" and trading_data.get("data"):
            for account in trading_data["data"]:
                if "details" in account:
                    for detail in account["details"]:
                        if float(detail.get("eq", 0)) > 0:
                            overview["trading_account"]["currencies"].append({
                                "currency": detail["ccy"],
                                "balance": float(detail["eq"]),
                                "available": float(detail["availBal"]),
                                "frozen": float(detail["frozenBal"]),
                                "usd_value": float(detail.get("eqUsd", 0)),
                                "account_type": "trading"
                            })
                            overview["trading_account"]["total_equity_usd"] += float(detail.get("eqUsd", 0))
                    overview["trading_account"]["count"] = len(overview["trading_account"]["currencies"])
        
        # 处理资金账户数据
        if funding_data and funding_data.get("code") == "0" and funding_data.get("data"):
            for balance in funding_data["data"]:
                if float(balance.get("bal", 0)) > 0:
                    overview["funding_account"]["currencies"].append({
                        "currency": balance["ccy"],
                        "balance": float(balance["bal"]),
                        "available": float(balance["availBal"]),
                        "frozen": float(balance["frozenBal"]),
                        "usd_value": 0,  # 需要单独计算
                        "account_type": "funding"
                    })
                    # 这里可以添加USD价值计算逻辑
            overview["funding_account"]["count"] = len(overview["funding_account"]["currencies"])
        
        # 处理储蓄账户数据
        if savings_data and savings_data.get("code") == "0" and savings_data.get("data"):
            for balance in savings_data["data"]:
                if float(balance.get("amt", 0)) > 0:
                    overview["savings_account"]["currencies"].append({
                        "currency": balance["ccy"],
                        "balance": float(balance["amt"]),
                        "available": float(balance["amt"]),
                        "frozen": 0,
                        "usd_value": 0,  # 需要单独计算
                        "account_type": "savings",
                        "earnings": float(balance.get("earnings", 0)),
                        "rate": float(balance.get("rate", 0))
                    })
                    # 简单计算USD价值（这里可以后续优化）
                    if balance["ccy"] == "USDT":
                        overview["savings_account"]["total_balance_usd"] += float(balance["amt"])
            overview["savings_account"]["count"] = len(overview["savings_account"]["currencies"])
        
        # 计算总计
        overview["total_overview"]["total_assets_usd"] = (
            overview["trading_account"]["total_equity_usd"] +
            overview["funding_account"]["total_balance_usd"] +
            overview["savings_account"]["total_balance_usd"]
        )
        
        all_currencies = set()
        for account_type in ["trading_account", "funding_account", "savings_account"]:
            for currency in overview[account_type]["currencies"]:
                all_currencies.add(currency["currency"])
        
        overview["total_overview"]["total_currencies"] = len(all_currencies)
        
        return {"success": True, "data": overview, "source": "api"}
        
    except Exception as e:
        logger.error(f"获取OKX账户总览失败: {str(e)}")
        return {"success": False, "message": f"获取账户总览失败: {str(e)}"}


# Web3 API接口
@router.get("/web3/config")
async def get_web3_config():
    """获取Web3 API配置信息"""
    try:
        config = await web3_service.get_config()
        return {
            "success": True,
            "data": config
        }
    except Exception as e:
        logger.error(f"获取Web3配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Web3配置失败: {str(e)}")


@router.get("/web3/test")
async def test_web3_connection():
    """测试Web3 API连接"""
    try:
        result = await web3_service.test_connection()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"测试Web3连接失败: {e}")
        return {
            "success": False,
            "data": {
                "public_api": False,
                "private_api": False,
                "error": str(e),
                "timestamp": int(time.time() * 1000)
            }
        }


@router.get("/web3/balance")
async def get_web3_balance():
    """获取Web3账户余额信息"""
    try:
        result = await web3_service.get_account_balance()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"获取Web3账户余额失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Web3账户余额失败: {str(e)}")


@router.get("/web3/tokens")
async def get_web3_tokens():
    """获取Web3账户代币列表"""
    try:
        result = await web3_service.get_account_tokens()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"获取Web3代币列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Web3代币列表失败: {str(e)}")


@router.get("/web3/transactions")
async def get_web3_transactions(limit: int = Query(100, ge=1, le=1000)):
    """获取Web3账户交易记录"""
    try:
        result = await web3_service.get_account_transactions(limit=limit)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"获取Web3交易记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Web3交易记录失败: {str(e)}")


@router.post("/web3/sync-balance")
async def sync_web3_balance():
    """同步Web3余额到数据库"""
    try:
        result = await web3_service.sync_balance_to_db()
        return {
            "success": result.get("success", False),
            "data": result
        }
    except Exception as e:
        logger.error(f"同步Web3余额失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步余额失败: {str(e)}")


@router.post("/web3/sync-tokens")
async def sync_web3_tokens():
    """同步Web3代币到数据库"""
    try:
        result = await web3_service.sync_tokens_to_db()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"同步Web3代币失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步代币失败: {str(e)}")


@router.post("/web3/sync-transactions")
async def sync_web3_transactions(limit: int = Query(100, ge=1, le=1000)):
    """同步Web3交易记录到数据库"""
    try:
        result = await web3_service.sync_transactions_to_db(limit=limit)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"同步Web3交易记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步交易记录失败: {str(e)}")


@router.get("/web3/stored-balance")
async def get_stored_web3_balance():
    """获取存储的Web3余额数据"""
    try:
        db = SessionLocal()
        try:
            # 获取最新的Web3余额记录
            latest_balance = db.query(Web3Balance).filter(
                Web3Balance.project_id == web3_service.project_id,
                Web3Balance.account_id == web3_service.account_id
            ).order_by(Web3Balance.update_time.desc()).first()
            
            if latest_balance:
                return {
                    "success": True,
                    "data": {
                        "total_value": float(latest_balance.total_value),
                        "currency": latest_balance.currency,
                        "update_time": latest_balance.update_time.isoformat(),
                        "source": "database"
                    }
                }
            else:
                return {
                    "success": True,
                    "data": None
                }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取存储的Web3余额失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取存储余额失败: {str(e)}")


@router.get("/web3/stored-tokens")
async def get_stored_web3_tokens():
    """获取存储的Web3代币数据"""
    try:
        db = SessionLocal()
        try:
            # 获取最新的Web3代币记录
            latest_tokens = db.query(Web3Token).filter(
                Web3Token.project_id == web3_service.project_id,
                Web3Token.account_id == web3_service.account_id
            ).order_by(Web3Token.update_time.desc()).all()
            
            if latest_tokens:
                tokens_data = []
                for token in latest_tokens:
                    tokens_data.append({
                        "token_symbol": token.token_symbol,
                        "token_name": token.token_name,
                        "token_address": token.token_address,
                        "balance": float(token.balance),
                        "value_usd": float(token.value_usd),
                        "price_usd": float(token.price_usd) if token.price_usd else None,
                        "update_time": token.update_time.isoformat()
                    })
                
                return {
                    "success": True,
                    "data": tokens_data,
                    "source": "database"
                }
            else:
                return {
                    "success": True,
                    "data": [],
                    "source": "database"
                }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取存储的Web3代币失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取存储代币失败: {str(e)}")