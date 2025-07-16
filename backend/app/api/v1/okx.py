from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.services.okx_api_service import OKXAPIService
from loguru import logger
from app.models.database import OKXBalance, OKXTransaction, OKXPosition, OKXMarketData
from app.utils.database import SessionLocal

router = APIRouter(prefix="/okx", tags=["OKX API"])

# 初始化OKX API服务
okx_service = OKXAPIService()


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


@router.get("/test")
async def test_okx_connection():
    """测试OKX API连接"""
    try:
        result = await okx_service.test_connection()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"测试OKX连接失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试连接失败: {str(e)}")


@router.get("/account")
async def get_okx_account():
    """获取OKX账户资产信息"""
    try:
        result = await okx_service.get_account_balance()
        if result is None:
            raise HTTPException(status_code=500, detail="获取账户资产失败")
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取OKX账户资产失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取账户资产失败: {str(e)}")


@router.get("/asset-balances")
async def get_okx_asset_balances(ccy: str = Query(None, description="币种代码")):
    """获取OKX资金账户余额"""
    try:
        result = await okx_service.get_asset_balances(ccy)
        if result is None:
            raise HTTPException(status_code=500, detail="获取资金账户余额失败")
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取OKX资金账户余额失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取资金账户余额失败: {str(e)}")


@router.get("/savings-balance")
async def get_okx_savings_balance(ccy: str = Query(None, description="币种代码")):
    """获取OKX储蓄账户余额"""
    try:
        result = await okx_service.get_savings_balance(ccy)
        if result is None:
            raise HTTPException(status_code=500, detail="获取储蓄账户余额失败")
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取OKX储蓄账户余额失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取储蓄账户余额失败: {str(e)}")


@router.get("/stored-balances")
async def get_stored_balances():
    """从数据库获取已存储的OKX余额数据"""
    try:
        db = SessionLocal()
        try:
            balances = db.query(OKXBalance).all()
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


@router.get("/positions")
async def get_okx_positions(inst_type: str = Query(None, description="产品类型")):
    """获取OKX持仓信息"""
    try:
        result = await okx_service.get_positions(inst_type)
        if result is None:
            raise HTTPException(status_code=500, detail="获取持仓信息失败")
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取OKX持仓信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取持仓信息失败: {str(e)}")


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


@router.get("/bills")
async def get_okx_bills(
    inst_type: str = Query(None, description="产品类型"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数量限制")
):
    """获取OKX账单流水"""
    try:
        result = await okx_service.get_bills(inst_type, limit)
        if result is None:
            raise HTTPException(status_code=500, detail="获取账单流水失败")
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取OKX账单流水失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取账单流水失败: {str(e)}")


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
            
            transaction_list = []
            for tx in transactions:
                transaction_list.append({
                    "transaction_id": tx.transaction_id,
                    "account_id": tx.account_id,
                    "inst_type": tx.inst_type,
                    "inst_id": tx.inst_id,
                    "trade_id": tx.trade_id,
                    "order_id": tx.order_id,
                    "bill_id": tx.bill_id,
                    "type": tx.type,
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


@router.get("/ticker")
async def get_okx_ticker(inst_id: str = Query(..., description="产品ID")):
    """获取OKX单个币种行情"""
    try:
        result = await okx_service.get_ticker(inst_id)
        if result is None:
            raise HTTPException(status_code=500, detail="获取行情数据失败")
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取OKX行情数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取行情数据失败: {str(e)}")


@router.get("/tickers")
async def get_okx_tickers(inst_type: str = Query("SPOT", description="产品类型")):
    """获取OKX所有币种行情"""
    try:
        result = await okx_service.get_all_tickers(inst_type)
        if result is None:
            raise HTTPException(status_code=500, detail="获取所有行情数据失败")
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取OKX所有行情数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取所有行情数据失败: {str(e)}")


@router.get("/instruments")
async def get_okx_instruments(inst_type: str = Query("SPOT", description="产品类型")):
    """获取OKX交易产品基础信息"""
    try:
        result = await okx_service.get_instruments(inst_type)
        if result is None:
            raise HTTPException(status_code=500, detail="获取交易产品信息失败")
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取OKX交易产品信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取交易产品信息失败: {str(e)}")


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


@router.get("/summary")
async def get_okx_summary():
    """获取OKX账户汇总信息"""
    try:
        result = await okx_service.get_summary()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"获取OKX汇总信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取汇总信息失败: {str(e)}")


@router.post("/sync-balances")
async def sync_balances():
    """主动同步OKX余额数据到数据库"""
    try:
        result = await okx_service.sync_balances_to_db()
        return result
    except Exception as e:
        logger.error(f"同步OKX余额数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步OKX余额数据失败: {str(e)}")


@router.post("/sync-transactions")
async def sync_transactions(days: int = Query(30, ge=1, le=365, description="同步天数")):
    """主动同步OKX交易记录到数据库"""
    try:
        result = await okx_service.sync_transactions_to_db(days)
        return result
    except Exception as e:
        logger.error(f"同步OKX交易记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步OKX交易记录失败: {str(e)}")


@router.post("/sync-positions")
async def sync_positions():
    """主动同步OKX持仓数据到数据库"""
    try:
        result = await okx_service.sync_positions_to_db()
        return result
    except Exception as e:
        logger.error(f"同步OKX持仓数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步OKX持仓数据失败: {str(e)}")


@router.post("/sync-market-data")
async def sync_market_data(inst_ids: List[str] = Query(None, description="产品ID列表")):
    """主动同步OKX市场数据到数据库"""
    try:
        result = await okx_service.sync_market_data_to_db(inst_ids)
        return result
    except Exception as e:
        logger.error(f"同步OKX市场数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步OKX市场数据失败: {str(e)}")