"""
Web3钱包管理服务
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from loguru import logger
from sqlalchemy import func, desc

from app.utils.database import SessionLocal
from app.models.database import Web3Wallet, Web3WalletBalance
from app.services.blockchain_service import blockchain_service
from app.services.coingecko_service import coingecko_service


class Web3WalletService:
    """Web3钱包管理服务"""
    
    def __init__(self):
        self.supported_chains = ['ethereum', 'bsc', 'polygon', 'arbitrum']
    
    async def add_wallet(self, wallet_address: str, chain_type: str, wallet_name: str = None, 
                        connection_type: str = 'manual_input', user_id: int = None) -> Dict:
        """添加钱包"""
        try:
            db = SessionLocal()
            
            # 验证地址格式
            if not blockchain_service.is_valid_address(wallet_address, chain_type):
                return {"success": False, "message": f"无效的{chain_type}地址格式"}
            
            # 检查是否已存在
            existing = db.query(Web3Wallet).filter(
                Web3Wallet.wallet_address == wallet_address,
                Web3Wallet.chain_type == chain_type
            ).first()
            
            if existing:
                if existing.is_active:
                    return {"success": False, "message": "钱包已存在"}
                else:
                    # 重新激活
                    existing.is_active = True
                    existing.updated_at = datetime.now()
                    db.commit()
                    return {"success": True, "message": "钱包已重新激活", "wallet_id": existing.id}
            
            # 创建新钱包
            new_wallet = Web3Wallet(
                user_id=user_id,
                wallet_address=wallet_address,
                wallet_name=wallet_name or f"{chain_type.upper()}钱包",
                chain_type=chain_type,
                connection_type=connection_type,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(new_wallet)
            db.commit()
            
            logger.info(f"成功添加钱包: {wallet_address} ({chain_type})")
            
            # 立即同步一次资产
            sync_result = await self.sync_wallet_assets(new_wallet.id)
            
            return {
                "success": True, 
                "message": "钱包添加成功",
                "wallet_id": new_wallet.id,
                "sync_result": sync_result
            }
            
        except Exception as e:
            logger.error(f"添加钱包失败: {e}")
            db.rollback()
            return {"success": False, "message": f"添加钱包失败: {str(e)}"}
        finally:
            db.close()
    
    async def get_wallets(self, user_id: int = None) -> List[Dict]:
        """获取钱包列表"""
        try:
            db = SessionLocal()
            
            query = db.query(Web3Wallet).filter(Web3Wallet.is_active == True)
            if user_id:
                query = query.filter(Web3Wallet.user_id == user_id)
            
            wallets = query.order_by(Web3Wallet.created_at.desc()).all()
            
            wallet_list = []
            for wallet in wallets:
                wallet_list.append({
                    "id": wallet.id,
                    "wallet_address": wallet.wallet_address,
                    "wallet_name": wallet.wallet_name,
                    "chain_type": wallet.chain_type,
                    "connection_type": wallet.connection_type,
                    "last_sync_time": wallet.last_sync_time.isoformat() if wallet.last_sync_time else None,
                    "created_at": wallet.created_at.isoformat() if wallet.created_at else None
                })
            
            return wallet_list
            
        except Exception as e:
            logger.error(f"获取钱包列表失败: {e}")
            return []
        finally:
            db.close()
    
    async def sync_wallet_assets(self, wallet_id: int) -> Dict:
        """同步单个钱包资产"""
        try:
            db = SessionLocal()
            
            # 获取钱包信息
            wallet = db.query(Web3Wallet).filter(Web3Wallet.id == wallet_id).first()
            if not wallet:
                return {"success": False, "message": "钱包不存在"}
            
            sync_time = datetime.now().replace(microsecond=0)
            
            # 查询区块链资产
            assets = await blockchain_service.get_wallet_assets(wallet.chain_type, wallet.wallet_address)
            
            if not assets:
                logger.warning(f"钱包 {wallet.wallet_address} 没有找到资产")
                # 更新同步时间
                wallet.last_sync_time = sync_time
                db.commit()
                return {"success": True, "message": "同步完成，但未找到资产", "assets_count": 0}
            
            # 获取代币价格
            token_symbols = [asset['token_symbol'] for asset in assets]
            prices = await coingecko_service.get_token_prices(token_symbols)
            
            # 保存资产数据
            saved_count = 0
            for asset in assets:
                try:
                    price = prices.get(asset['token_symbol'], 0.0)
                    usdt_value = float(asset['balance']) * price if price > 0 else 0.0
                    
                    # 格式化余额显示
                    balance_formatted = self._format_balance(asset['balance'])
                    
                    new_balance = Web3WalletBalance(
                        wallet_id=wallet_id,
                        chain=asset['chain'],
                        token_symbol=asset['token_symbol'],
                        token_name=asset['token_name'],
                        token_address=asset['token_address'],
                        balance=asset['balance'],
                        balance_formatted=balance_formatted,
                        usdt_price=Decimal(str(price)) if price > 0 else None,
                        usdt_value=Decimal(str(usdt_value)) if usdt_value > 0 else None,
                        is_native_token=asset['is_native_token'],
                        sync_time=sync_time
                    )
                    
                    db.add(new_balance)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"保存资产数据失败: {e}")
            
            # 更新钱包同步时间
            wallet.last_sync_time = sync_time
            db.commit()
            
            logger.info(f"成功同步钱包 {wallet.wallet_address}，保存 {saved_count} 个资产")
            
            return {
                "success": True,
                "message": "同步完成",
                "wallet_address": wallet.wallet_address,
                "assets_count": saved_count,
                "sync_time": sync_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"同步钱包资产失败: {e}")
            db.rollback()
            return {"success": False, "message": f"同步失败: {str(e)}"}
        finally:
            db.close()
    
    async def sync_all_wallets(self, user_id: int = None) -> Dict:
        """同步所有活跃钱包"""
        try:
            db = SessionLocal()
            
            query = db.query(Web3Wallet).filter(Web3Wallet.is_active == True)
            if user_id:
                query = query.filter(Web3Wallet.user_id == user_id)
            
            wallets = query.all()
            
            if not wallets:
                return {"success": True, "message": "没有需要同步的钱包", "synced_count": 0}
            
            sync_results = []
            success_count = 0
            
            for wallet in wallets:
                result = await self.sync_wallet_assets(wallet.id)
                sync_results.append({
                    "wallet_id": wallet.id,
                    "wallet_address": wallet.wallet_address,
                    "result": result
                })
                
                if result["success"]:
                    success_count += 1
            
            return {
                "success": True,
                "message": f"同步完成，成功 {success_count}/{len(wallets)} 个钱包",
                "synced_count": success_count,
                "total_count": len(wallets),
                "details": sync_results
            }
            
        except Exception as e:
            logger.error(f"批量同步钱包失败: {e}")
            return {"success": False, "message": f"批量同步失败: {str(e)}"}
        finally:
            db.close()
    
    async def get_wallet_assets(self, wallet_id: int) -> List[Dict]:
        """获取钱包最新资产"""
        try:
            db = SessionLocal()
            
            # 获取最新同步时间
            latest_sync = db.query(func.max(Web3WalletBalance.sync_time))\
                           .filter(Web3WalletBalance.wallet_id == wallet_id)\
                           .scalar()
            
            if not latest_sync:
                return []
            
            # 获取最新资产数据
            assets = db.query(Web3WalletBalance)\
                       .filter(
                           Web3WalletBalance.wallet_id == wallet_id,
                           Web3WalletBalance.sync_time == latest_sync
                       )\
                       .order_by(desc(Web3WalletBalance.usdt_value))\
                       .all()
            
            asset_list = []
            for asset in assets:
                asset_list.append({
                    "chain": asset.chain,
                    "token_symbol": asset.token_symbol,
                    "token_name": asset.token_name,
                    "token_address": asset.token_address,
                    "balance": str(asset.balance),
                    "balance_formatted": asset.balance_formatted,
                    "usdt_price": float(asset.usdt_price) if asset.usdt_price else 0,
                    "usdt_value": float(asset.usdt_value) if asset.usdt_value else 0,
                    "is_native_token": asset.is_native_token,
                    "sync_time": asset.sync_time.isoformat()
                })
            
            return asset_list
            
        except Exception as e:
            logger.error(f"获取钱包资产失败: {e}")
            return []
        finally:
            db.close()
    
    async def get_portfolio_summary(self, user_id: int = None) -> Dict:
        """获取投资组合总览"""
        try:
            db = SessionLocal()
            
            # 获取所有活跃钱包的最新资产
            subq = db.query(
                Web3WalletBalance.wallet_id,
                func.max(Web3WalletBalance.sync_time).label('max_sync_time')
            ).group_by(Web3WalletBalance.wallet_id).subquery()
            
            query = db.query(Web3WalletBalance).join(
                subq,
                (Web3WalletBalance.wallet_id == subq.c.wallet_id) &
                (Web3WalletBalance.sync_time == subq.c.max_sync_time)
            )
            
            if user_id:
                query = query.join(Web3Wallet).filter(Web3Wallet.user_id == user_id)
            
            latest_assets = query.all()
            
            # 统计数据
            total_value = 0
            token_count = 0
            wallet_count = len(set([asset.wallet_id for asset in latest_assets]))
            
            for asset in latest_assets:
                if asset.usdt_value:
                    total_value += float(asset.usdt_value)
                token_count += 1
            
            return {
                "total_value_usdt": round(total_value, 2),
                "wallet_count": wallet_count,
                "token_count": token_count,
                "last_update": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取投资组合总览失败: {e}")
            return {
                "total_value_usdt": 0,
                "wallet_count": 0,
                "token_count": 0,
                "last_update": datetime.now().isoformat()
            }
        finally:
            db.close()
    
    def _format_balance(self, balance: Decimal) -> str:
        """格式化余额显示"""
        try:
            if balance >= 1:
                return f"{balance:.4f}"
            elif balance >= 0.0001:
                return f"{balance:.6f}"
            else:
                return f"{balance:.8f}"
        except:
            return str(balance)
    
    async def remove_wallet(self, wallet_id: int) -> Dict:
        """移除钱包（软删除）"""
        try:
            db = SessionLocal()
            
            wallet = db.query(Web3Wallet).filter(Web3Wallet.id == wallet_id).first()
            if not wallet:
                return {"success": False, "message": "钱包不存在"}
            
            wallet.is_active = False
            wallet.updated_at = datetime.now()
            db.commit()
            
            return {"success": True, "message": "钱包已移除"}
            
        except Exception as e:
            logger.error(f"移除钱包失败: {e}")
            db.rollback()
            return {"success": False, "message": f"移除钱包失败: {str(e)}"}
        finally:
            db.close()


# 全局实例
web3_wallet_service = Web3WalletService()