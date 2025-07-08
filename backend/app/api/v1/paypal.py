from fastapi import APIRouter, HTTPException, Query
from loguru import logger
from app.services.paypal_api_service import PayPalAPIService
from typing import Optional
import time

router = APIRouter(prefix="/paypal", tags=["PayPal API"])

# 初始化PayPal API服务
paypal_service = PayPalAPIService()


@router.get("/config")
async def get_paypal_config():
    """获取PayPal API配置信息"""
    try:
        config = await paypal_service.get_config()
        return {"success": True, "data": config}
    except Exception as e:
        logger.error(f"获取PayPal配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取PayPal配置失败: {str(e)}")


@router.get("/test")
async def test_paypal_connection():
    """测试PayPal API连接"""
    try:
        result = await paypal_service.test_connection()
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"测试PayPal连接失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试PayPal连接失败: {str(e)}")


@router.get("/balance-accounts")
async def get_paypal_balance_accounts():
    """获取PayPal余额账户"""
    try:
        balance_accounts = await paypal_service.get_balance_accounts()
        if balance_accounts is None:
            raise HTTPException(status_code=500, detail="获取PayPal余额账户失败")
        return {"success": True, "data": balance_accounts}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取PayPal余额账户失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取PayPal余额账户失败: {str(e)}")


@router.get("/all-balances")
async def get_all_paypal_balances():
    """获取所有PayPal账户余额"""
    try:
        balances = await paypal_service.get_all_balances()
        return {"success": True, "data": balances}
    except Exception as e:
        logger.error(f"获取所有PayPal账户余额失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取所有PayPal账户余额失败: {str(e)}")


@router.get("/transactions")
async def get_paypal_transactions(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DDTHH:MM:SS-XXXX)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DDTHH:MM:SS-XXXX)"),
    page_size: int = Query(100, description="每页数量"),
    page: int = Query(1, description="页码")
):
    """获取PayPal交易记录"""
    try:
        transactions = await paypal_service.get_transactions(start_date, end_date, page_size, page)
        if transactions is None:
            raise HTTPException(status_code=500, detail="获取PayPal交易记录失败")
        return {"success": True, "data": transactions}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取PayPal交易记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取PayPal交易记录失败: {str(e)}")


@router.get("/recent-transactions")
async def get_recent_paypal_transactions(
    days: int = Query(30, description="获取最近几天的交易记录")
):
    """获取最近PayPal交易记录"""
    try:
        transactions = await paypal_service.get_recent_transactions(days)
        return {"success": True, "data": transactions}
    except Exception as e:
        logger.error(f"获取最近PayPal交易记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取最近PayPal交易记录失败: {str(e)}")


@router.get("/summary")
async def get_paypal_summary():
    """获取PayPal账户汇总信息"""
    try:
        summary = await paypal_service.get_account_summary()
        return {"success": True, "data": summary}
    except Exception as e:
        logger.error(f"获取PayPal汇总信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取PayPal汇总信息失败: {str(e)}")


@router.get("/balances-report")
async def get_paypal_balances_report():
    """获取PayPal余额报告"""
    try:
        balances = await paypal_service.get_balances_list()
        if balances is None:
            raise HTTPException(status_code=500, detail="获取PayPal余额报告失败")
        return {"success": True, "data": balances}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取PayPal余额报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取PayPal余额报告失败: {str(e)}")


@router.get("/debug")
async def get_paypal_debug_info():
    """获取PayPal调试信息"""
    try:
        # 获取配置信息
        config = await paypal_service.get_config()
        
        # 测试连接状态
        connection_test = await paypal_service.test_connection()
        
        # 获取访问令牌状态
        token_info = {
            "has_token": paypal_service.access_token is not None,
            "token_expires_at": paypal_service.token_expires_at,
            "current_time": time.time(),
            "token_valid": (
                paypal_service.access_token is not None and 
                paypal_service.token_expires_at is not None and 
                time.time() < paypal_service.token_expires_at
            )
        }
        
        return {
            "success": True,
            "data": {
                "config": config,
                "connection_test": connection_test,
                "token_info": token_info,
                "timestamp": time.time()
            }
        }
    except Exception as e:
        logger.error(f"获取PayPal调试信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取PayPal调试信息失败: {str(e)}")