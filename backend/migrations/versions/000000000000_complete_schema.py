"""complete_schema

Revision ID: 000000000000
Revises: 
Create Date: 2025-07-28 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '000000000000'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 获取数据库连接
    connection = op.get_bind()
    
    # 检查表是否存在的辅助函数
    def table_exists(table_name):
        from sqlalchemy import text
        result = connection.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = '{table_name}'
            )
        """))
        return result.scalar()
    
    # 创建所有表结构（只创建不存在的表）
    # 1. user_operations 表
    if not table_exists('user_operations'):
        op.create_table('user_operations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('operation_date', sa.DateTime(), nullable=False),
            sa.Column('platform', sa.String(length=50), nullable=False),
            sa.Column('asset_type', sa.String(length=50), nullable=False),
            sa.Column('operation_type', sa.String(length=20), nullable=False),
            sa.Column('asset_code', sa.String(length=50), nullable=False),
            sa.Column('asset_name', sa.String(length=100), nullable=False),
            sa.Column('amount', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('currency', sa.String(length=10), nullable=False),
            sa.Column('quantity', sa.DECIMAL(precision=15, scale=8), nullable=True),
            sa.Column('price', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('nav', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('fee', sa.DECIMAL(precision=10, scale=4), nullable=True),
            sa.Column('strategy', sa.Text(), nullable=True),
            sa.Column('emotion_score', sa.Integer(), nullable=True),
            sa.Column('tags', sa.Text(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=True),
            sa.Column('dca_plan_id', sa.Integer(), nullable=True),
            sa.Column('dca_execution_type', sa.String(length=20), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    
    # 2. asset_positions 表
    if not table_exists('asset_positions'):
        op.create_table('asset_positions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('platform', sa.String(length=50), nullable=False),
            sa.Column('asset_type', sa.String(length=50), nullable=False),
            sa.Column('asset_code', sa.String(length=50), nullable=False),
            sa.Column('asset_name', sa.String(length=100), nullable=False),
            sa.Column('currency', sa.String(length=10), nullable=False),
            sa.Column('quantity', sa.DECIMAL(precision=15, scale=8), nullable=False),
            sa.Column('avg_cost', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('current_price', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('current_value', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('total_invested', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('total_profit', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('profit_rate', sa.DECIMAL(precision=8, scale=4), nullable=False),
            sa.Column('last_updated', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('platform', 'asset_code', 'currency', name='uq_position')
        )
    
    # 3. fund_info 表
    if not table_exists('fund_info'):
        op.create_table('fund_info',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('fund_code', sa.String(length=20), nullable=False),
            sa.Column('fund_name', sa.String(length=100), nullable=False),
            sa.Column('fund_type', sa.String(length=50), nullable=True),
            sa.Column('management_fee', sa.DECIMAL(precision=5, scale=4), nullable=True),
            sa.Column('purchase_fee', sa.DECIMAL(precision=5, scale=4), nullable=True),
            sa.Column('redemption_fee', sa.DECIMAL(precision=5, scale=4), nullable=True),
            sa.Column('min_purchase', sa.DECIMAL(precision=10, scale=2), nullable=True),
            sa.Column('risk_level', sa.String(length=20), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('fund_code')
        )
    
    # 4. fund_nav 表
    if not table_exists('fund_nav'):
        op.create_table('fund_nav',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('fund_code', sa.String(length=20), nullable=False),
            sa.Column('nav_date', sa.Date(), nullable=False),
            sa.Column('nav', sa.DECIMAL(precision=10, scale=4), nullable=False),
            sa.Column('accumulated_nav', sa.DECIMAL(precision=10, scale=4), nullable=True),
            sa.Column('growth_rate', sa.DECIMAL(precision=8, scale=4), nullable=True),
            sa.Column('source', sa.String(length=50), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('fund_code', 'nav_date', name='uq_fund_nav')
        )
    
    # 5. fund_dividend 表
    if not table_exists('fund_dividend'):
        op.create_table('fund_dividend',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('fund_code', sa.String(length=10), nullable=False),
            sa.Column('dividend_date', sa.Date(), nullable=False),
            sa.Column('dividend_amount', sa.DECIMAL(precision=10, scale=4), nullable=False),
            sa.Column('dividend_type', sa.String(length=20), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('fund_code', 'dividend_date', name='uq_fund_dividend')
        )
    
    # 6. dca_plans 表
    if not table_exists('dca_plans'):
        op.create_table('dca_plans',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('platform', sa.String(length=50), nullable=False),
            sa.Column('asset_code', sa.String(length=50), nullable=False),
            sa.Column('asset_name', sa.String(length=100), nullable=False),
            sa.Column('currency', sa.String(length=10), nullable=False),
            sa.Column('amount', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('frequency', sa.String(length=20), nullable=False),
            sa.Column('next_execution', sa.DateTime(), nullable=True),
            sa.Column('smart_dca', sa.Boolean(), nullable=True),
            sa.Column('skip_holidays', sa.Boolean(), nullable=True),
            sa.Column('enable_notification', sa.Boolean(), nullable=True),
            sa.Column('exclude_dates', sa.Text(), nullable=True),
            sa.Column('fee_rate', sa.DECIMAL(precision=5, scale=4), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    
    # 7. exchange_rates 表
    if not table_exists('exchange_rates'):
        op.create_table('exchange_rates',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('from_currency', sa.String(length=10), nullable=False),
            sa.Column('to_currency', sa.String(length=10), nullable=False),
            sa.Column('rate', sa.DECIMAL(precision=15, scale=6), nullable=False),
            sa.Column('rate_date', sa.Date(), nullable=False),
            sa.Column('source', sa.String(length=50), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('from_currency', 'to_currency', 'rate_date', name='uq_exchange_rate')
        )
    
    # 8. system_config 表
    if not table_exists('system_config'):
        op.create_table('system_config',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('config_key', sa.String(length=100), nullable=False),
            sa.Column('config_value', sa.Text(), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('config_key')
        )
    
    # 9. wise_transactions 表
    if not table_exists('wise_transactions'):
        op.create_table('wise_transactions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('transaction_id', sa.String(length=100), nullable=False),
            sa.Column('account_id', sa.String(length=100), nullable=False),
            sa.Column('type', sa.String(length=50), nullable=False),
            sa.Column('status', sa.String(length=50), nullable=False),
            sa.Column('amount', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('currency', sa.String(length=10), nullable=False),
            sa.Column('primary_amount', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('secondary_amount', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('fee', sa.DECIMAL(precision=10, scale=4), nullable=True),
            sa.Column('exchange_rate', sa.DECIMAL(precision=15, scale=6), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('reference', sa.String(length=200), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('transaction_id')
        )
    
    # 10. wise_balances 表
    if not table_exists('wise_balances'):
        op.create_table('wise_balances',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('account_id', sa.String(length=100), nullable=False),
            sa.Column('currency', sa.String(length=10), nullable=False),
            sa.Column('balance', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('reserved', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('available', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('last_updated', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('account_id', 'currency', name='uq_wise_balance')
        )
    
    # 11. wise_exchange_rates 表
    if not table_exists('wise_exchange_rates'):
        op.create_table('wise_exchange_rates',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('from_currency', sa.String(length=10), nullable=False),
            sa.Column('to_currency', sa.String(length=10), nullable=False),
            sa.Column('rate', sa.DECIMAL(precision=15, scale=6), nullable=False),
            sa.Column('rate_date', sa.Date(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('from_currency', 'to_currency', 'rate_date', name='uq_wise_exchange_rate')
        )
    
    # 12. ibkr_accounts 表
    if not table_exists('ibkr_accounts'):
        op.create_table('ibkr_accounts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('account_id', sa.String(length=50), nullable=False),
            sa.Column('account_name', sa.String(length=100), nullable=True),
            sa.Column('account_type', sa.String(length=50), nullable=True),
            sa.Column('currency', sa.String(length=10), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('account_id')
        )
    
    # 13. ibkr_balances 表
    if not table_exists('ibkr_balances'):
        op.create_table('ibkr_balances',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('account_id', sa.String(length=50), nullable=False),
            sa.Column('currency', sa.String(length=10), nullable=False),
            sa.Column('balance', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('available', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('last_updated', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('account_id', 'currency', name='uq_ibkr_balance')
        )
    
    # 14. ibkr_positions 表
    if not table_exists('ibkr_positions'):
        op.create_table('ibkr_positions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('account_id', sa.String(length=50), nullable=False),
            sa.Column('symbol', sa.String(length=50), nullable=False),
            sa.Column('currency', sa.String(length=10), nullable=False),
            sa.Column('quantity', sa.DECIMAL(precision=15, scale=8), nullable=False),
            sa.Column('avg_cost', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('market_value', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('unrealized_pnl', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('last_updated', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('account_id', 'symbol', 'currency', name='uq_ibkr_position')
        )
    
    # 15. ibkr_sync_logs 表
    if not table_exists('ibkr_sync_logs'):
        op.create_table('ibkr_sync_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('sync_type', sa.String(length=50), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('records_processed', sa.Integer(), nullable=True),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('started_at', sa.DateTime(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    
    # 16. okx_balances 表
    if not table_exists('okx_balances'):
        op.create_table('okx_balances',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('account_id', sa.String(length=100), nullable=False),
            sa.Column('currency', sa.String(length=10), nullable=False),
            sa.Column('balance', sa.DECIMAL(precision=15, scale=8), nullable=False),
            sa.Column('available', sa.DECIMAL(precision=15, scale=8), nullable=True),
            sa.Column('frozen', sa.DECIMAL(precision=15, scale=8), nullable=True),
            sa.Column('last_updated', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('account_id', 'currency', name='uq_okx_balance')
        )
    
    # 17. okx_transactions 表
    if not table_exists('okx_transactions'):
        op.create_table('okx_transactions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('transaction_id', sa.String(length=100), nullable=False),
            sa.Column('account_id', sa.String(length=100), nullable=False),
            sa.Column('inst_type', sa.String(length=20), nullable=False),
            sa.Column('inst_id', sa.String(length=50), nullable=False),
            sa.Column('trade_id', sa.String(length=100), nullable=True),
            sa.Column('order_id', sa.String(length=100), nullable=True),
            sa.Column('bill_id', sa.String(length=100), nullable=True),
            sa.Column('type', sa.String(length=20), nullable=False),
            sa.Column('side', sa.String(length=10), nullable=True),
            sa.Column('amount', sa.DECIMAL(precision=15, scale=8), nullable=False),
            sa.Column('currency', sa.String(length=10), nullable=False),
            sa.Column('fee', sa.DECIMAL(precision=15, scale=8), nullable=True),
            sa.Column('fee_currency', sa.String(length=10), nullable=True),
            sa.Column('price', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('quantity', sa.DECIMAL(precision=15, scale=8), nullable=True),
            sa.Column('timestamp', sa.DateTime(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            # 新增的25个字段
            sa.Column('bal', sa.DECIMAL(precision=15, scale=8), nullable=True),
            sa.Column('bal_chg', sa.DECIMAL(precision=15, scale=8), nullable=True),
            sa.Column('ccy', sa.String(length=10), nullable=True),
            sa.Column('cl_ord_id', sa.String(length=100), nullable=True),
            sa.Column('exec_type', sa.String(length=20), nullable=True),
            sa.Column('fill_fwd_px', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('fill_idx_px', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('fill_mark_px', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('fill_mark_vol', sa.DECIMAL(precision=15, scale=8), nullable=True),
            sa.Column('fill_px_usd', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('fill_px_vol', sa.DECIMAL(precision=15, scale=8), nullable=True),
            sa.Column('fill_time', sa.DateTime(), nullable=True),
            sa.Column('from_addr', sa.String(length=200), nullable=True),
            sa.Column('interest', sa.DECIMAL(precision=15, scale=8), nullable=True),
            sa.Column('mgn_mode', sa.String(length=20), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('pnl', sa.DECIMAL(precision=15, scale=8), nullable=True),
            sa.Column('pos_bal', sa.DECIMAL(precision=15, scale=8), nullable=True),
            sa.Column('pos_bal_chg', sa.DECIMAL(precision=15, scale=8), nullable=True),
            sa.Column('sub_type', sa.String(length=20), nullable=True),
            sa.Column('tag', sa.String(length=50), nullable=True),
            sa.Column('to_addr', sa.String(length=200), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('transaction_id')
        )
    
    # 18. okx_positions 表
    if not table_exists('okx_positions'):
        op.create_table('okx_positions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('account_id', sa.String(length=100), nullable=False),
            sa.Column('inst_id', sa.String(length=50), nullable=False),
            sa.Column('inst_type', sa.String(length=20), nullable=False),
            sa.Column('currency', sa.String(length=10), nullable=False),
            sa.Column('position', sa.DECIMAL(precision=15, scale=8), nullable=False),
            sa.Column('avg_price', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('market_value', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('unrealized_pnl', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('last_updated', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('account_id', 'inst_id', 'currency', name='uq_okx_position')
        )
    
    # 19. okx_market_data 表
    if not table_exists('okx_market_data'):
        op.create_table('okx_market_data',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('inst_id', sa.String(length=50), nullable=False),
            sa.Column('inst_type', sa.String(length=20), nullable=False),
            sa.Column('price', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('volume_24h', sa.DECIMAL(precision=20, scale=8), nullable=True),
            sa.Column('change_24h', sa.DECIMAL(precision=10, scale=4), nullable=True),
            sa.Column('timestamp', sa.DateTime(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('inst_id', 'timestamp', name='uq_okx_market_data')
        )
    
    # 20. okx_account_overview 表
    if not table_exists('okx_account_overview'):
        op.create_table('okx_account_overview',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('account_id', sa.String(length=100), nullable=False),
            sa.Column('total_equity', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('total_margin', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('available_balance', sa.DECIMAL(precision=15, scale=4), nullable=False),
            sa.Column('unrealized_pnl', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('currency', sa.String(length=10), nullable=False),
            sa.Column('last_updated', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('account_id', 'currency', name='uq_okx_account_overview')
        )
    
    # 21. web3_balances 表
    if not table_exists('web3_balances'):
        op.create_table('web3_balances',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('wallet_address', sa.String(length=200), nullable=False),
            sa.Column('network', sa.String(length=50), nullable=False),
            sa.Column('currency', sa.String(length=10), nullable=False),
            sa.Column('balance', sa.DECIMAL(precision=30, scale=18), nullable=False),
            sa.Column('usd_value', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('last_updated', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('wallet_address', 'network', 'currency', name='uq_web3_balance')
        )
    
    # 22. web3_tokens 表
    if not table_exists('web3_tokens'):
        op.create_table('web3_tokens',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('wallet_address', sa.String(length=200), nullable=False),
            sa.Column('network', sa.String(length=50), nullable=False),
            sa.Column('token_address', sa.String(length=200), nullable=False),
            sa.Column('token_symbol', sa.String(length=20), nullable=False),
            sa.Column('token_name', sa.String(length=100), nullable=True),
            sa.Column('decimals', sa.Integer(), nullable=True),
            sa.Column('balance', sa.DECIMAL(precision=30, scale=18), nullable=False),
            sa.Column('usd_value', sa.DECIMAL(precision=15, scale=4), nullable=True),
            sa.Column('last_updated', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('wallet_address', 'network', 'token_address', name='uq_web3_token')
        )
    
    # 23. web3_transactions 表
    if not table_exists('web3_transactions'):
        op.create_table('web3_transactions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('tx_hash', sa.String(length=200), nullable=False),
            sa.Column('wallet_address', sa.String(length=200), nullable=False),
            sa.Column('network', sa.String(length=50), nullable=False),
            sa.Column('type', sa.String(length=20), nullable=False),
            sa.Column('from_address', sa.String(length=200), nullable=True),
            sa.Column('to_address', sa.String(length=200), nullable=True),
            sa.Column('amount', sa.DECIMAL(precision=30, scale=18), nullable=True),
            sa.Column('currency', sa.String(length=10), nullable=True),
            sa.Column('gas_fee', sa.DECIMAL(precision=30, scale=18), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('timestamp', sa.DateTime(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('tx_hash', 'network', name='uq_web3_transaction')
        )
    
    # 24. asset_snapshot 表
    if not table_exists('asset_snapshot'):
        op.create_table('asset_snapshot',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('platform', sa.String(length=50), nullable=True),
            sa.Column('asset_type', sa.String(length=50), nullable=True),
            sa.Column('asset_code', sa.String(length=50), nullable=True),
            sa.Column('asset_name', sa.String(length=100), nullable=True),
            sa.Column('currency', sa.String(length=10), nullable=True),
            sa.Column('balance', sa.DECIMAL(precision=20, scale=8), nullable=False),
            sa.Column('balance_cny', sa.DECIMAL(precision=20, scale=8), nullable=True),
            sa.Column('balance_usd', sa.DECIMAL(precision=20, scale=8), nullable=True),
            sa.Column('balance_eur', sa.DECIMAL(precision=20, scale=8), nullable=True),
            sa.Column('base_value', sa.DECIMAL(precision=20, scale=8), nullable=True),
            sa.Column('snapshot_time', sa.DateTime(), nullable=True),
            sa.Column('extra', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    
    # 25. exchange_rate_snapshot 表
    if not table_exists('exchange_rate_snapshot'):
        op.create_table('exchange_rate_snapshot',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('from_currency', sa.String(length=10), nullable=True),
            sa.Column('to_currency', sa.String(length=10), nullable=True),
            sa.Column('rate', sa.DECIMAL(precision=20, scale=8), nullable=False),
            sa.Column('snapshot_time', sa.DateTime(), nullable=True),
            sa.Column('source', sa.String(length=50), nullable=True),
            sa.Column('extra', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    
    # 创建索引（只创建不存在的索引）
    def index_exists(index_name):
        from sqlalchemy import text
        result = connection.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = '{index_name}'
            )
        """))
        return result.scalar()
    
    # 用户操作表索引
    if not index_exists('idx_operations_date'):
        op.create_index('idx_operations_date', 'user_operations', ['operation_date'], unique=False)
    if not index_exists('idx_operations_platform'):
        op.create_index('idx_operations_platform', 'user_operations', ['platform'], unique=False)
    if not index_exists('idx_operations_asset'):
        op.create_index('idx_operations_asset', 'user_operations', ['asset_code'], unique=False)
    if not index_exists('ix_user_operations_id'):
        op.create_index('ix_user_operations_id', 'user_operations', ['id'], unique=False)
    if not index_exists('ix_user_operations_operation_date'):
        op.create_index('ix_user_operations_operation_date', 'user_operations', ['operation_date'], unique=False)
    if not index_exists('ix_user_operations_platform'):
        op.create_index('ix_user_operations_platform', 'user_operations', ['platform'], unique=False)
    if not index_exists('ix_user_operations_asset_code'):
        op.create_index('ix_user_operations_asset_code', 'user_operations', ['asset_code'], unique=False)
    
    # 资产持仓表索引
    if not index_exists('idx_positions_platform'):
        op.create_index('idx_positions_platform', 'asset_positions', ['platform'], unique=False)
    if not index_exists('idx_positions_asset'):
        op.create_index('idx_positions_asset', 'asset_positions', ['asset_code'], unique=False)
    if not index_exists('ix_asset_positions_id'):
        op.create_index('ix_asset_positions_id', 'asset_positions', ['id'], unique=False)
    if not index_exists('ix_asset_positions_platform'):
        op.create_index('ix_asset_positions_platform', 'asset_positions', ['platform'], unique=False)
    if not index_exists('ix_asset_positions_asset_code'):
        op.create_index('ix_asset_positions_asset_code', 'asset_positions', ['asset_code'], unique=False)
    
    # 基金信息表索引
    if not index_exists('ix_fund_info_id'):
        op.create_index('ix_fund_info_id', 'fund_info', ['id'], unique=False)
    if not index_exists('ix_fund_info_fund_code'):
        op.create_index('ix_fund_info_fund_code', 'fund_info', ['fund_code'], unique=False)
    
    # 基金净值表索引
    if not index_exists('idx_fund_nav_date'):
        op.create_index('idx_fund_nav_date', 'fund_nav', ['nav_date'], unique=False)
    if not index_exists('idx_fund_nav_code'):
        op.create_index('idx_fund_nav_code', 'fund_nav', ['fund_code'], unique=False)
    if not index_exists('ix_fund_nav_id'):
        op.create_index('ix_fund_nav_id', 'fund_nav', ['id'], unique=False)
    if not index_exists('ix_fund_nav_fund_code'):
        op.create_index('ix_fund_nav_fund_code', 'fund_nav', ['fund_code'], unique=False)
    if not index_exists('ix_fund_nav_nav_date'):
        op.create_index('ix_fund_nav_nav_date', 'fund_nav', ['nav_date'], unique=False)
    
    # 基金分红表索引
    if not index_exists('idx_fund_dividend_code'):
        op.create_index('idx_fund_dividend_code', 'fund_dividend', ['fund_code'], unique=False)
    if not index_exists('idx_fund_dividend_date'):
        op.create_index('idx_fund_dividend_date', 'fund_dividend', ['dividend_date'], unique=False)
    if not index_exists('ix_fund_dividend_id'):
        op.create_index('ix_fund_dividend_id', 'fund_dividend', ['id'], unique=False)
    if not index_exists('ix_fund_dividend_fund_code'):
        op.create_index('ix_fund_dividend_fund_code', 'fund_dividend', ['fund_code'], unique=False)
    if not index_exists('ix_fund_dividend_dividend_date'):
        op.create_index('ix_fund_dividend_dividend_date', 'fund_dividend', ['dividend_date'], unique=False)
    
    # DCA计划表索引
    if not index_exists('ix_dca_plans_id'):
        op.create_index('ix_dca_plans_id', 'dca_plans', ['id'], unique=False)
    
    # 汇率表索引
    if not index_exists('idx_exchange_rates_date'):
        op.create_index('idx_exchange_rates_date', 'exchange_rates', ['rate_date'], unique=False)
    if not index_exists('idx_exchange_rates_currency'):
        op.create_index('idx_exchange_rates_currency', 'exchange_rates', ['from_currency', 'to_currency'], unique=False)
    if not index_exists('ix_exchange_rates_id'):
        op.create_index('ix_exchange_rates_id', 'exchange_rates', ['id'], unique=False)
    if not index_exists('ix_exchange_rates_from_currency'):
        op.create_index('ix_exchange_rates_from_currency', 'exchange_rates', ['from_currency'], unique=False)
    if not index_exists('ix_exchange_rates_rate_date'):
        op.create_index('ix_exchange_rates_rate_date', 'exchange_rates', ['rate_date'], unique=False)
    if not index_exists('ix_exchange_rates_to_currency'):
        op.create_index('ix_exchange_rates_to_currency', 'exchange_rates', ['to_currency'], unique=False)
    
    # 系统配置表索引
    if not index_exists('ix_system_config_id'):
        op.create_index('ix_system_config_id', 'system_config', ['id'], unique=False)
    if not index_exists('ix_system_config_config_key'):
        op.create_index('ix_system_config_config_key', 'system_config', ['config_key'], unique=False)
    
    # Wise交易表索引
    if not index_exists('idx_wise_transaction_date'):
        op.create_index('idx_wise_transaction_date', 'wise_transactions', ['created_at'], unique=False)
    if not index_exists('idx_wise_transaction_account'):
        op.create_index('idx_wise_transaction_account', 'wise_transactions', ['account_id'], unique=False)
    if not index_exists('ix_wise_transactions_id'):
        op.create_index('ix_wise_transactions_id', 'wise_transactions', ['id'], unique=False)
    if not index_exists('ix_wise_transactions_account_id'):
        op.create_index('ix_wise_transactions_account_id', 'wise_transactions', ['account_id'], unique=False)
    if not index_exists('ix_wise_transactions_transaction_id'):
        op.create_index('ix_wise_transactions_transaction_id', 'wise_transactions', ['transaction_id'], unique=False)
    if not index_exists('ix_wise_transactions_created_at'):
        op.create_index('ix_wise_transactions_created_at', 'wise_transactions', ['created_at'], unique=False)
    
    # Wise余额表索引
    if not index_exists('idx_wise_balance_currency'):
        op.create_index('idx_wise_balance_currency', 'wise_balances', ['currency'], unique=False)
    if not index_exists('ix_wise_balances_id'):
        op.create_index('ix_wise_balances_id', 'wise_balances', ['id'], unique=False)
    if not index_exists('ix_wise_balances_account_id'):
        op.create_index('ix_wise_balances_account_id', 'wise_balances', ['account_id'], unique=False)
    
    # Wise汇率表索引
    if not index_exists('ix_wise_exchange_rates_id'):
        op.create_index('ix_wise_exchange_rates_id', 'wise_exchange_rates', ['id'], unique=False)
    
    # IBKR账户表索引
    if not index_exists('idx_ibkr_accounts_id'):
        op.create_index('idx_ibkr_accounts_id', 'ibkr_accounts', ['account_id'], unique=False)
    if not index_exists('ix_ibkr_accounts_id'):
        op.create_index('ix_ibkr_accounts_id', 'ibkr_accounts', ['id'], unique=False)
    if not index_exists('ix_ibkr_accounts_account_id'):
        op.create_index('ix_ibkr_accounts_account_id', 'ibkr_accounts', ['account_id'], unique=False)
    
    # IBKR余额表索引
    if not index_exists('idx_ibkr_balances_account'):
        op.create_index('idx_ibkr_balances_account', 'ibkr_balances', ['account_id'], unique=False)
    if not index_exists('ix_ibkr_balances_id'):
        op.create_index('ix_ibkr_balances_id', 'ibkr_balances', ['id'], unique=False)
    if not index_exists('ix_ibkr_balances_account_id'):
        op.create_index('ix_ibkr_balances_account_id', 'ibkr_balances', ['account_id'], unique=False)
    
    # IBKR持仓表索引
    if not index_exists('idx_ibkr_positions_account'):
        op.create_index('idx_ibkr_positions_account', 'ibkr_positions', ['account_id'], unique=False)
    if not index_exists('idx_ibkr_positions_symbol'):
        op.create_index('idx_ibkr_positions_symbol', 'ibkr_positions', ['symbol'], unique=False)
    if not index_exists('ix_ibkr_positions_id'):
        op.create_index('ix_ibkr_positions_id', 'ibkr_positions', ['id'], unique=False)
    if not index_exists('ix_ibkr_positions_account_id'):
        op.create_index('ix_ibkr_positions_account_id', 'ibkr_positions', ['account_id'], unique=False)
    if not index_exists('ix_ibkr_positions_symbol'):
        op.create_index('ix_ibkr_positions_symbol', 'ibkr_positions', ['symbol'], unique=False)
    
    # IBKR同步日志表索引
    if not index_exists('idx_ibkr_sync_logs_status'):
        op.create_index('idx_ibkr_sync_logs_status', 'ibkr_sync_logs', ['status'], unique=False)
    if not index_exists('idx_ibkr_sync_logs_date'):
        op.create_index('idx_ibkr_sync_logs_date', 'ibkr_sync_logs', ['created_at'], unique=False)
    if not index_exists('ix_ibkr_sync_logs_id'):
        op.create_index('ix_ibkr_sync_logs_id', 'ibkr_sync_logs', ['id'], unique=False)
    if not index_exists('ix_ibkr_sync_logs_status'):
        op.create_index('ix_ibkr_sync_logs_status', 'ibkr_sync_logs', ['status'], unique=False)
    if not index_exists('ix_ibkr_sync_logs_created_at'):
        op.create_index('ix_ibkr_sync_logs_created_at', 'ibkr_sync_logs', ['created_at'], unique=False)
    
    # OKX余额表索引
    if not index_exists('idx_okx_balance_currency'):
        op.create_index('idx_okx_balance_currency', 'okx_balances', ['currency'], unique=False)
    if not index_exists('ix_okx_balances_id'):
        op.create_index('ix_okx_balances_id', 'okx_balances', ['id'], unique=False)
    if not index_exists('ix_okx_balances_account_id'):
        op.create_index('ix_okx_balances_account_id', 'okx_balances', ['account_id'], unique=False)
    if not index_exists('ix_okx_balances_currency'):
        op.create_index('ix_okx_balances_currency', 'okx_balances', ['currency'], unique=False)
    
    # OKX交易表索引
    if not index_exists('idx_okx_transaction_timestamp'):
        op.create_index('idx_okx_transaction_timestamp', 'okx_transactions', ['timestamp'], unique=False)
    if not index_exists('idx_okx_transaction_inst_id'):
        op.create_index('idx_okx_transaction_inst_id', 'okx_transactions', ['inst_id'], unique=False)
    if not index_exists('idx_okx_transaction_type'):
        op.create_index('idx_okx_transaction_type', 'okx_transactions', ['type'], unique=False)

def downgrade():
    # 删除索引（按创建顺序的反序）
    op.drop_index('ix_exchange_rate_snapshot_snapshot_time', table_name='exchange_rate_snapshot')
    op.drop_index('ix_exchange_rate_snapshot_to_currency', table_name='exchange_rate_snapshot')
    op.drop_index('ix_exchange_rate_snapshot_from_currency', table_name='exchange_rate_snapshot')
    op.drop_index('ix_exchange_rate_snapshot_id', table_name='exchange_rate_snapshot')
    
    op.drop_index('ix_asset_snapshot_snapshot_time', table_name='asset_snapshot')
    op.drop_index('ix_asset_snapshot_currency', table_name='asset_snapshot')
    op.drop_index('ix_asset_snapshot_asset_code', table_name='asset_snapshot')
    op.drop_index('ix_asset_snapshot_asset_type', table_name='asset_snapshot')
    op.drop_index('ix_asset_snapshot_platform', table_name='asset_snapshot')
    op.drop_index('ix_asset_snapshot_user_id', table_name='asset_snapshot')
    op.drop_index('ix_asset_snapshot_id', table_name='asset_snapshot')
    
    op.drop_index('ix_web3_transactions_timestamp', table_name='web3_transactions')
    op.drop_index('ix_web3_transactions_token_symbol', table_name='web3_transactions')
    op.drop_index('ix_web3_transactions_transaction_hash', table_name='web3_transactions')
    op.drop_index('ix_web3_transactions_account_id', table_name='web3_transactions')
    op.drop_index('ix_web3_transactions_project_id', table_name='web3_transactions')
    op.drop_index('ix_web3_transactions_id', table_name='web3_transactions')
    
    op.drop_index('ix_web3_tokens_update_time', table_name='web3_tokens')
    op.drop_index('ix_web3_tokens_token_symbol', table_name='web3_tokens')
    op.drop_index('ix_web3_tokens_account_id', table_name='web3_tokens')
    op.drop_index('ix_web3_tokens_project_id', table_name='web3_tokens')
    op.drop_index('ix_web3_tokens_id', table_name='web3_tokens')
    
    op.drop_index('ix_web3_balances_update_time', table_name='web3_balances')
    op.drop_index('ix_web3_balances_account_id', table_name='web3_balances')
    op.drop_index('ix_web3_balances_project_id', table_name='web3_balances')
    op.drop_index('ix_web3_balances_id', table_name='web3_balances')
    
    op.drop_index('ix_okx_account_overview_last_update', table_name='okx_account_overview')
    op.drop_index('ix_okx_account_overview_id', table_name='okx_account_overview')
    
    op.drop_index('ix_okx_market_data_timestamp', table_name='okx_market_data')
    op.drop_index('ix_okx_market_data_inst_type', table_name='okx_market_data')
    op.drop_index('ix_okx_market_data_inst_id', table_name='okx_market_data')
    op.drop_index('ix_okx_market_data_id', table_name='okx_market_data')
    
    op.drop_index('ix_okx_positions_timestamp', table_name='okx_positions')
    op.drop_index('ix_okx_positions_inst_id', table_name='okx_positions')
    op.drop_index('ix_okx_positions_account_id', table_name='okx_positions')
    op.drop_index('ix_okx_positions_id', table_name='okx_positions')
    op.drop_index('idx_okx_position_timestamp', table_name='okx_positions')
    op.drop_index('idx_okx_position_inst_id', table_name='okx_positions')
    
    op.drop_index('ix_okx_transactions_type', table_name='okx_transactions')
    op.drop_index('ix_okx_transactions_timestamp', table_name='okx_transactions')
    op.drop_index('ix_okx_transactions_inst_id', table_name='okx_transactions')
    op.drop_index('ix_okx_transactions_account_id', table_name='okx_transactions')
    op.drop_index('ix_okx_transactions_transaction_id', table_name='okx_transactions')
    op.drop_index('ix_okx_transactions_id', table_name='okx_transactions')
    op.drop_index('idx_okx_transaction_type', table_name='okx_transactions')
    op.drop_index('idx_okx_transaction_inst_id', table_name='okx_transactions')
    op.drop_index('idx_okx_transaction_timestamp', table_name='okx_transactions')
    
    op.drop_index('ix_okx_balances_account_type', table_name='okx_balances')
    op.drop_index('ix_okx_balances_currency', table_name='okx_balances')
    op.drop_index('ix_okx_balances_account_id', table_name='okx_balances')
    op.drop_index('ix_okx_balances_id', table_name='okx_balances')
    op.drop_index('idx_okx_balance_account_type', table_name='okx_balances')
    op.drop_index('idx_okx_balance_currency', table_name='okx_balances')
    
    op.drop_index('ix_ibkr_sync_logs_account_id', table_name='ibkr_sync_logs')
    op.drop_index('ix_ibkr_sync_logs_created_at', table_name='ibkr_sync_logs')
    op.drop_index('ix_ibkr_sync_logs_status', table_name='ibkr_sync_logs')
    op.drop_index('ix_ibkr_sync_logs_id', table_name='ibkr_sync_logs')
    op.drop_index('idx_ibkr_sync_logs_account', table_name='ibkr_sync_logs')
    op.drop_index('idx_ibkr_sync_logs_date', table_name='ibkr_sync_logs')
    op.drop_index('idx_ibkr_sync_logs_status', table_name='ibkr_sync_logs')
    
    op.drop_index('ix_ibkr_positions_snapshot_date', table_name='ibkr_positions')
    op.drop_index('ix_ibkr_positions_symbol', table_name='ibkr_positions')
    op.drop_index('ix_ibkr_positions_account_id', table_name='ibkr_positions')
    op.drop_index('ix_ibkr_positions_id', table_name='ibkr_positions')
    op.drop_index('idx_ibkr_positions_date', table_name='ibkr_positions')
    op.drop_index('idx_ibkr_positions_symbol', table_name='ibkr_positions')
    op.drop_index('idx_ibkr_positions_account', table_name='ibkr_positions')
    
    op.drop_index('ix_ibkr_balances_snapshot_date', table_name='ibkr_balances')
    op.drop_index('ix_ibkr_balances_account_id', table_name='ibkr_balances')
    op.drop_index('ix_ibkr_balances_id', table_name='ibkr_balances')
    op.drop_index('idx_ibkr_balances_date', table_name='ibkr_balances')
    op.drop_index('idx_ibkr_balances_account', table_name='ibkr_balances')
    
    op.drop_index('ix_ibkr_accounts_account_id', table_name='ibkr_accounts')
    op.drop_index('ix_ibkr_accounts_id', table_name='ibkr_accounts')
    op.drop_index('idx_ibkr_accounts_id', table_name='ibkr_accounts')
    
    op.drop_index('ix_wise_exchange_rates_id', table_name='wise_exchange_rates')
    
    op.drop_index('ix_wise_balances_account_id', table_name='wise_balances')
    op.drop_index('ix_wise_balances_id', table_name='wise_balances')
    op.drop_index('idx_wise_balance_currency', table_name='wise_balances')
    
    op.drop_index('ix_wise_transactions_date', table_name='wise_transactions')
    op.drop_index('ix_wise_transactions_transaction_id', table_name='wise_transactions')
    op.drop_index('ix_wise_transactions_account_id', table_name='wise_transactions')
    op.drop_index('ix_wise_transactions_profile_id', table_name='wise_transactions')
    op.drop_index('ix_wise_transactions_id', table_name='wise_transactions')
    op.drop_index('idx_wise_transaction_account', table_name='wise_transactions')
    op.drop_index('idx_wise_transaction_profile', table_name='wise_transactions')
    op.drop_index('idx_wise_transaction_date', table_name='wise_transactions')
    
    op.drop_index('ix_system_config_config_key', table_name='system_config')
    op.drop_index('ix_system_config_id', table_name='system_config')
    
    op.drop_index('ix_exchange_rates_to_currency', table_name='exchange_rates')
    op.drop_index('ix_exchange_rates_rate_date', table_name='exchange_rates')
    op.drop_index('ix_exchange_rates_from_currency', table_name='exchange_rates')
    op.drop_index('ix_exchange_rates_id', table_name='exchange_rates')
    op.drop_index('idx_exchange_rates_currency', table_name='exchange_rates')
    op.drop_index('idx_exchange_rates_date', table_name='exchange_rates')
    
    op.drop_index('ix_dca_plans_id', table_name='dca_plans')
    
    op.drop_index('ix_fund_dividend_dividend_date', table_name='fund_dividend')
    op.drop_index('ix_fund_dividend_fund_code', table_name='fund_dividend')
    op.drop_index('ix_fund_dividend_id', table_name='fund_dividend')
    op.drop_index('idx_fund_dividend_date', table_name='fund_dividend')
    op.drop_index('idx_fund_dividend_code', table_name='fund_dividend')
    
    op.drop_index('ix_fund_nav_nav_date', table_name='fund_nav')
    op.drop_index('ix_fund_nav_fund_code', table_name='fund_nav')
    op.drop_index('ix_fund_nav_id', table_name='fund_nav')
    op.drop_index('idx_fund_nav_code', table_name='fund_nav')
    op.drop_index('idx_fund_nav_date', table_name='fund_nav')
    
    op.drop_index('ix_fund_info_fund_code', table_name='fund_info')
    op.drop_index('ix_fund_info_id', table_name='fund_info')
    
    op.drop_index('ix_asset_positions_asset_code', table_name='asset_positions')
    op.drop_index('ix_asset_positions_platform', table_name='asset_positions')
    op.drop_index('ix_asset_positions_id', table_name='asset_positions')
    op.drop_index('idx_positions_asset', table_name='asset_positions')
    op.drop_index('idx_positions_platform', table_name='asset_positions')
    
    op.drop_index('ix_user_operations_asset_code', table_name='user_operations')
    op.drop_index('ix_user_operations_platform', table_name='user_operations')
    op.drop_index('ix_user_operations_operation_date', table_name='user_operations')
    op.drop_index('ix_user_operations_id', table_name='user_operations')
    op.drop_index('idx_operations_asset', table_name='user_operations')
    op.drop_index('idx_operations_platform', table_name='user_operations')
    op.drop_index('idx_operations_date', table_name='user_operations')
    
    # 删除所有表（按创建顺序的反序）
    op.drop_table('exchange_rate_snapshot')
    op.drop_table('asset_snapshot')
    op.drop_table('web3_transactions')
    op.drop_table('web3_tokens')
    op.drop_table('web3_balances')
    op.drop_table('okx_account_overview')
    op.drop_table('okx_market_data')
    op.drop_table('okx_positions')
    op.drop_table('okx_transactions')
    op.drop_table('okx_balances')
    op.drop_table('ibkr_sync_logs')
    op.drop_table('ibkr_positions')
    op.drop_table('ibkr_balances')
    op.drop_table('ibkr_accounts')
    op.drop_table('wise_exchange_rates')
    op.drop_table('wise_balances')
    op.drop_table('wise_transactions')
    op.drop_table('system_config')
    op.drop_table('exchange_rates')
    op.drop_table('dca_plans')
    op.drop_table('fund_dividend')
    op.drop_table('fund_nav')
    op.drop_table('fund_info')
    op.drop_table('asset_positions')
    op.drop_table('user_operations') 