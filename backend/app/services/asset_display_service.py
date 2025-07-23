import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from decimal import Decimal

from app.models.exchange_rate_models import (
    AccountBalanceSnapshot, ExchangeRateTimeline, AssetDisplayConfig,
    AssetTypeConfig, UserAssetPreference
)
from app.models.database import AssetPosition, WiseBalance, IBKRBalance, OKXBalance
from app.core.database import get_db

logger = logging.getLogger(__name__)


class AssetDisplayService:
    """资产展示服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def get_multi_currency_overview(self, user_id: int, currencies: List[str], 
                                   base_currency: Optional[str] = None, 
                                   time_point: Optional[datetime] = None) -> Dict:
        """
        获取多币种资产概览
        
        Args:
            user_id: 用户ID
            currencies: 要展示的币种列表 ['CNY', 'USD', 'JPY']
            base_currency: 基准货币（用于统一衡量）
            time_point: 时间点（None表示当前时间）
            
        Returns:
            多币种资产概览数据
        """
        try:
            # 1. 获取用户当前资产余额
            balances = self.get_user_balances(user_id, time_point)
            
            # 2. 计算各币种总资产
            currency_totals = {}
            for currency in currencies:
                total = self.calculate_total_in_currency(balances, currency, time_point)
                currency_totals[currency] = total
            
            # 3. 如果指定了基准货币，计算统一衡量
            unified_totals = None
            if base_currency:
                unified_totals = {}
                for currency in currencies:
                    if currency == base_currency:
                        unified_totals[currency] = currency_totals[currency]
                    else:
                        # 通过基准货币转换
                        rate = self.get_exchange_rate(currency, base_currency, time_point)
                        if rate:
                            unified_totals[currency] = currency_totals[currency] * rate
                        else:
                            unified_totals[currency] = 0
            
            return {
                'currency_totals': currency_totals,
                'unified_totals': unified_totals,
                'time_point': time_point or datetime.now(),
                'base_currency': base_currency,
                'currencies': currencies,
                'user_id': user_id
            }
            
        except Exception as e:
            self.logger.error(f"获取多币种资产概览失败: {e}")
            return {
                'error': str(e),
                'currency_totals': {},
                'unified_totals': None,
                'time_point': time_point or datetime.now(),
                'base_currency': base_currency,
                'currencies': currencies,
                'user_id': user_id
            }
    
    def get_user_balances(self, user_id: int, time_point: Optional[datetime] = None) -> List[Dict]:
        """
        获取用户资产余额
        
        Args:
            user_id: 用户ID
            time_point: 时间点（None表示当前时间）
            
        Returns:
            资产余额列表
        """
        balances = []
        
        if time_point:
            # 获取指定时间点的快照数据
            snapshots = self.db.query(AccountBalanceSnapshot).filter(
                AccountBalanceSnapshot.user_id == user_id,
                AccountBalanceSnapshot.snapshot_time <= time_point
            ).all()
            
            # 获取每个资产类型的最新快照
            asset_latest = {}
            for snapshot in snapshots:
                key = snapshot.asset_type
                if key not in asset_latest or snapshot.snapshot_time > asset_latest[key].snapshot_time:
                    asset_latest[key] = snapshot
            
            for asset_type, snapshot in asset_latest.items():
                balances.append({
                    'asset_type': asset_type,
                    'balance': snapshot.balance,
                    'snapshot_time': snapshot.snapshot_time
                })
        else:
            # 获取当前实时数据
            balances.extend(self.get_current_balances(user_id))
        
        return balances
    
    def get_current_balances(self, user_id: int) -> List[Dict]:
        """获取当前实时资产余额"""
        balances = []
        
        # 从各个平台获取余额数据
        # 1. 基金持仓
        fund_positions = self.db.query(AssetPosition).filter(
            AssetPosition.platform.in_(['蚂蚁财富', '天天基金', '招商银行'])
        ).all()
        
        for pos in fund_positions:
            balances.append({
                'asset_type': pos.currency,
                'balance': pos.current_value,
                'platform': pos.platform,
                'asset_name': pos.asset_name
            })
        
        # 2. Wise余额
        wise_balances = self.db.query(WiseBalance).filter(
            WiseBalance.visible == True
        ).all()
        
        for balance in wise_balances:
            balances.append({
                'asset_type': balance.currency,
                'balance': balance.available_balance,
                'platform': 'Wise',
                'account_id': balance.account_id
            })
        
        # 3. IBKR余额
        ibkr_balances = self.db.query(IBKRBalance).filter(
            IBKRBalance.snapshot_date == datetime.now().date()
        ).all()
        
        for balance in ibkr_balances:
            balances.append({
                'asset_type': balance.currency,
                'balance': balance.net_liquidation,
                'platform': 'IBKR',
                'account_id': balance.account_id
            })
        
        # 4. OKX余额
        okx_balances = self.db.query(OKXBalance).filter(
            OKXBalance.update_time >= datetime.now() - timedelta(hours=1)
        ).all()
        
        for balance in okx_balances:
            balances.append({
                'asset_type': balance.currency,
                'balance': balance.total_balance,
                'platform': 'OKX',
                'account_id': balance.account_id
            })
        
        return balances
    
    def calculate_total_in_currency(self, balances: List[Dict], target_currency: str, 
                                   time_point: Optional[datetime] = None) -> Decimal:
        """
        计算指定币种的总资产
        
        Args:
            balances: 资产余额列表
            target_currency: 目标币种
            time_point: 时间点
            
        Returns:
            总资产金额
        """
        total = Decimal('0')
        
        for balance in balances:
            asset_currency = balance['asset_type']
            amount = Decimal(str(balance['balance']))
            
            if asset_currency == target_currency:
                total += amount
            else:
                # 通过汇率转换
                rate = self.get_exchange_rate(asset_currency, target_currency, time_point)
                if rate:
                    total += amount * rate
                else:
                    self.logger.warning(f"无法获取汇率: {asset_currency}/{target_currency}")
        
        return total
    
    def get_exchange_rate(self, from_currency: str, to_currency: str, 
                         time_point: Optional[datetime] = None) -> Optional[Decimal]:
        """
        获取汇率
        
        Args:
            from_currency: 源币种
            to_currency: 目标币种
            time_point: 时间点（None表示最新汇率）
            
        Returns:
            汇率值
        """
        try:
            query = self.db.query(ExchangeRateTimeline).filter(
                ExchangeRateTimeline.from_currency == from_currency,
                ExchangeRateTimeline.to_currency == to_currency
            )
            
            if time_point:
                query = query.filter(ExchangeRateTimeline.effective_time <= time_point)
            
            rate_record = query.order_by(desc(ExchangeRateTimeline.effective_time)).first()
            
            if rate_record:
                return Decimal(str(rate_record.rate))
            else:
                # 尝试反向汇率
                reverse_query = self.db.query(ExchangeRateTimeline).filter(
                    ExchangeRateTimeline.from_currency == to_currency,
                    ExchangeRateTimeline.to_currency == from_currency
                )
                
                if time_point:
                    reverse_query = reverse_query.filter(ExchangeRateTimeline.effective_time <= time_point)
                
                reverse_rate = reverse_query.order_by(desc(ExchangeRateTimeline.effective_time)).first()
                
                if reverse_rate:
                    return Decimal('1') / Decimal(str(reverse_rate.rate))
                
                return None
                
        except Exception as e:
            self.logger.error(f"获取汇率失败: {from_currency}/{to_currency}, 错误: {e}")
            return None
    
    def get_asset_trend(self, user_id: int, currency: str, days: int = 30) -> List[Dict]:
        """
        获取资产趋势数据
        
        Args:
            user_id: 用户ID
            currency: 币种
            days: 天数
            
        Returns:
            趋势数据列表
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 获取时间范围内的快照数据
            snapshots = self.db.query(AccountBalanceSnapshot).filter(
                AccountBalanceSnapshot.user_id == user_id,
                AccountBalanceSnapshot.snapshot_time >= start_date,
                AccountBalanceSnapshot.snapshot_time <= end_date
            ).order_by(AccountBalanceSnapshot.snapshot_time).all()
            
            trend_data = []
            
            # 按日期分组计算
            daily_totals = {}
            for snapshot in snapshots:
                date_key = snapshot.snapshot_time.date()
                if date_key not in daily_totals:
                    daily_totals[date_key] = []
                daily_totals[date_key].append(snapshot)
            
            # 计算每日总资产
            for date_key, day_snapshots in daily_totals.items():
                total = self.calculate_total_in_currency(
                    [{'asset_type': s.asset_type, 'balance': s.balance} for s in day_snapshots],
                    currency,
                    datetime.combine(date_key, datetime.max.time())
                )
                
                trend_data.append({
                    'date': date_key.isoformat(),
                    'total': float(total),
                    'currency': currency
                })
            
            return trend_data
            
        except Exception as e:
            self.logger.error(f"获取资产趋势失败: {e}")
            return []
    
    def get_user_preferences(self, user_id: int) -> Dict:
        """获取用户资产偏好设置"""
        try:
            preferences = self.db.query(UserAssetPreference).filter(
                UserAssetPreference.user_id == user_id,
                UserAssetPreference.effective_to.is_(None)  # 当前有效的偏好
            ).all()
            
            return {
                pref.asset_type: pref.preferred_currency 
                for pref in preferences
            }
            
        except Exception as e:
            self.logger.error(f"获取用户偏好失败: {e}")
            return {}
    
    def save_user_preference(self, user_id: int, asset_type: str, preferred_currency: str):
        """保存用户资产偏好"""
        try:
            # 结束之前的偏好设置
            existing_prefs = self.db.query(UserAssetPreference).filter(
                UserAssetPreference.user_id == user_id,
                UserAssetPreference.asset_type == asset_type,
                UserAssetPreference.effective_to.is_(None)
            ).all()
            
            for pref in existing_prefs:
                pref.effective_to = datetime.now()
            
            # 创建新的偏好设置
            new_pref = UserAssetPreference(
                user_id=user_id,
                asset_type=asset_type,
                preferred_currency=preferred_currency,
                effective_from=datetime.now()
            )
            
            self.db.add(new_pref)
            self.db.commit()
            
            self.logger.info(f"用户偏好已保存: {user_id}, {asset_type} -> {preferred_currency}")
            
        except Exception as e:
            self.logger.error(f"保存用户偏好失败: {e}")
            self.db.rollback()
            raise
    
    def get_display_configs(self, user_id: Optional[int] = None) -> List[Dict]:
        """获取展示配置"""
        try:
            query = self.db.query(AssetDisplayConfig)
            
            if user_id:
                # 获取用户特定配置和全局配置
                query = query.filter(
                    (AssetDisplayConfig.user_id == user_id) | 
                    (AssetDisplayConfig.user_id.is_(None))
                )
            else:
                # 只获取全局配置
                query = query.filter(AssetDisplayConfig.user_id.is_(None))
            
            configs = query.all()
            
            return [
                {
                    'id': config.id,
                    'display_name': config.display_name,
                    'currencies': config.currencies,
                    'base_currency': config.base_currency,
                    'layout_type': config.layout_type,
                    'is_default': config.is_default,
                    'user_id': config.user_id
                }
                for config in configs
            ]
            
        except Exception as e:
            self.logger.error(f"获取展示配置失败: {e}")
            return []
    
    def save_display_config(self, config_data: Dict) -> Dict:
        """保存展示配置"""
        try:
            config = AssetDisplayConfig(**config_data)
            self.db.add(config)
            self.db.commit()
            
            return {
                'id': config.id,
                'display_name': config.display_name,
                'currencies': config.currencies,
                'base_currency': config.base_currency,
                'layout_type': config.layout_type,
                'is_default': config.is_default,
                'user_id': config.user_id
            }
            
        except Exception as e:
            self.logger.error(f"保存展示配置失败: {e}")
            self.db.rollback()
            raise


# 便捷函数
def get_asset_overview(user_id: int, currencies: List[str] = None, 
                      base_currency: str = None, time_point: datetime = None) -> Dict:
    """获取资产概览的便捷函数"""
    if currencies is None:
        currencies = ['CNY', 'USD', 'JPY']
    
    db = next(get_db())
    try:
        service = AssetDisplayService(db)
        return service.get_multi_currency_overview(user_id, currencies, base_currency, time_point)
    finally:
        db.close()


def get_asset_trend(user_id: int, currency: str = 'CNY', days: int = 30) -> List[Dict]:
    """获取资产趋势的便捷函数"""
    db = next(get_db())
    try:
        service = AssetDisplayService(db)
        return service.get_asset_trend(user_id, currency, days)
    finally:
        db.close()