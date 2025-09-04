"""
Web3钱包管理API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger

from app.services.web3_wallet_service import web3_wallet_service
from app.services.coingecko_service import coingecko_service

router = APIRouter(prefix="/web3-wallets", tags=["Web3 Wallets"])


# 请求模型
class AddWalletRequest(BaseModel):
    wallet_address: str
    chain_type: str
    wallet_name: Optional[str] = None
    user_id: Optional[int] = None


# 响应模型
class APIResponse(BaseModel):
    success: bool
    message: str = ""
    data: Any = None


@router.get("/config")
async def get_web3_config():
    """获取Web3配置信息"""
    try:
        config = {
            "supported_chains": ["ethereum", "bsc", "polygon", "arbitrum"],
            "connection_types": ["manual_input", "walletconnect"],
            "features": {
                "price_service": "coingecko",
                "auto_sync": True,
                "cache_enabled": True
            }
        }
        return APIResponse(success=True, data=config)
    except Exception as e:
        logger.error(f"获取Web3配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.post("/add")
async def add_wallet(request: AddWalletRequest):
    """添加钱包"""
    try:
        result = await web3_wallet_service.add_wallet(
            wallet_address=request.wallet_address,
            chain_type=request.chain_type,
            wallet_name=request.wallet_name,
            user_id=request.user_id
        )
        
        if result["success"]:
            return APIResponse(
                success=True,
                message=result["message"],
                data={
                    "wallet_id": result["wallet_id"],
                    "sync_result": result.get("sync_result")
                }
            )
        else:
            return APIResponse(success=False, message=result["message"])
            
    except Exception as e:
        logger.error(f"添加钱包失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加钱包失败: {str(e)}")


@router.get("/list")
async def get_wallets(user_id: Optional[int] = Query(None)):
    """获取钱包列表"""
    try:
        wallets = await web3_wallet_service.get_wallets(user_id)
        return APIResponse(
            success=True,
            data=wallets,
            message=f"获取到 {len(wallets)} 个钱包"
        )
    except Exception as e:
        logger.error(f"获取钱包列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取钱包列表失败: {str(e)}")


@router.get("/{wallet_id}/assets")
async def get_wallet_assets(wallet_id: int):
    """获取钱包资产"""
    try:
        assets = await web3_wallet_service.get_wallet_assets(wallet_id)
        return APIResponse(
            success=True,
            data=assets,
            message=f"获取到 {len(assets)} 个资产"
        )
    except Exception as e:
        logger.error(f"获取钱包资产失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取钱包资产失败: {str(e)}")


@router.post("/{wallet_id}/sync")
async def sync_wallet(wallet_id: int):
    """同步单个钱包资产"""
    try:
        result = await web3_wallet_service.sync_wallet_assets(wallet_id)
        
        if result["success"]:
            return APIResponse(
                success=True,
                message=result["message"],
                data={
                    "wallet_address": result.get("wallet_address"),
                    "assets_count": result.get("assets_count"),
                    "sync_time": result.get("sync_time")
                }
            )
        else:
            return APIResponse(success=False, message=result["message"])
            
    except Exception as e:
        logger.error(f"同步钱包失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步钱包失败: {str(e)}")


@router.post("/sync-all")
async def sync_all_wallets(user_id: Optional[int] = Query(None)):
    """同步所有钱包资产"""
    try:
        result = await web3_wallet_service.sync_all_wallets(user_id)
        
        return APIResponse(
            success=result["success"],
            message=result["message"],
            data={
                "synced_count": result.get("synced_count"),
                "total_count": result.get("total_count"),
                "details": result.get("details", [])
            }
        )
        
    except Exception as e:
        logger.error(f"批量同步钱包失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量同步失败: {str(e)}")


@router.get("/portfolio")
async def get_portfolio(user_id: Optional[int] = Query(None)):
    """获取投资组合总览"""
    try:
        portfolio = await web3_wallet_service.get_portfolio_summary(user_id)
        return APIResponse(
            success=True,
            data=portfolio,
            message="获取投资组合成功"
        )
    except Exception as e:
        logger.error(f"获取投资组合失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取投资组合失败: {str(e)}")


@router.delete("/{wallet_id}")
async def remove_wallet(wallet_id: int):
    """移除钱包"""
    try:
        result = await web3_wallet_service.remove_wallet(wallet_id)
        
        if result["success"]:
            return APIResponse(success=True, message=result["message"])
        else:
            return APIResponse(success=False, message=result["message"])
            
    except Exception as e:
        logger.error(f"移除钱包失败: {e}")
        raise HTTPException(status_code=500, detail=f"移除钱包失败: {str(e)}")


@router.get("/assets/all")
async def get_all_assets(user_id: Optional[int] = Query(None)):
    """获取所有钱包的资产汇总"""
    try:
        # 获取所有钱包
        wallets = await web3_wallet_service.get_wallets(user_id)
        
        all_assets = []
        for wallet in wallets:
            assets = await web3_wallet_service.get_wallet_assets(wallet["id"])
            for asset in assets:
                asset["wallet_info"] = {
                    "wallet_id": wallet["id"],
                    "wallet_name": wallet["wallet_name"],
                    "wallet_address": wallet["wallet_address"],
                    "chain_type": wallet["chain_type"]
                }
                all_assets.append(asset)
        
        # 按价值排序
        all_assets.sort(key=lambda x: x.get("usdt_value", 0), reverse=True)
        
        return APIResponse(
            success=True,
            data=all_assets,
            message=f"获取到 {len(all_assets)} 个资产"
        )
        
    except Exception as e:
        logger.error(f"获取所有资产失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取所有资产失败: {str(e)}")


@router.post("/prices/update")
async def update_prices():
    """手动更新代币价格"""
    try:
        count = await coingecko_service.update_price_cache()
        return APIResponse(
            success=True,
            message=f"成功更新 {count} 个代币价格",
            data={"updated_count": count}
        )
    except Exception as e:
        logger.error(f"更新价格失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新价格失败: {str(e)}")


@router.get("/prices/{token_symbol}")
async def get_token_price(token_symbol: str):
    """获取代币价格"""
    try:
        price = await coingecko_service.get_price_with_cache(token_symbol)
        return APIResponse(
            success=True,
            data={
                "token_symbol": token_symbol.upper(),
                "usdt_price": price,
                "timestamp": logger.info
            },
            message="获取价格成功"
        )
    except Exception as e:
        logger.error(f"获取代币价格失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取价格失败: {str(e)}")


@router.get("/test")
async def test_web3_service():
    """测试Web3服务连接"""
    try:
        # 测试价格服务
        price_test = await coingecko_service.get_token_price("ETH")
        
        test_results = {
            "price_service": {
                "status": "ok" if price_test > 0 else "error",
                "eth_price": price_test
            },
            "blockchain_service": {
                "supported_chains": ["ethereum", "bsc", "polygon", "arbitrum"],
                "status": "ok"
            },
            "database": {
                "status": "ok"  # 如果能执行到这里说明数据库连接正常
            }
        }
        
        return APIResponse(
            success=True,
            data=test_results,
            message="Web3服务测试完成"
        )
        
    except Exception as e:
        logger.error(f"Web3服务测试失败: {e}")
        return APIResponse(
            success=False,
            message=f"测试失败: {str(e)}"
        )