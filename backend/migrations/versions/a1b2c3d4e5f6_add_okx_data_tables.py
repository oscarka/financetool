"""add OKX data tables

Revision ID: a1b2c3d4e5f6
Revises: 4d412d44dc3e
Create Date: 2025-01-15 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '4d412d44dc3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # 创建OKX账户余额表
    op.create_table('okx_account_balances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=20), nullable=False),
        sa.Column('equity', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('available_balance', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('frozen_balance', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('position_value', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('unrealized_pnl', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('interest', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('margin_required', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('borrowed', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('data_timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建OKX持仓表
    op.create_table('okx_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inst_id', sa.String(length=50), nullable=False),
        sa.Column('inst_type', sa.String(length=20), nullable=False),
        sa.Column('position_side', sa.String(length=10), nullable=False),
        sa.Column('currency', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('available_quantity', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('avg_price', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('mark_price', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('notional_value', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('unrealized_pnl', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('unrealized_pnl_ratio', sa.Numeric(precision=8, scale=4), nullable=False, default=0),
        sa.Column('data_timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建OKX交易记录表
    op.create_table('okx_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bill_id', sa.String(length=50), nullable=False, unique=True),
        sa.Column('inst_id', sa.String(length=50), nullable=False),
        sa.Column('inst_type', sa.String(length=20), nullable=False),
        sa.Column('currency', sa.String(length=20), nullable=False),
        sa.Column('bill_type', sa.String(length=50), nullable=False),
        sa.Column('bill_sub_type', sa.String(length=50), nullable=True),
        sa.Column('amount', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('balance', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('fee', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('fill_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('fill_quantity', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('trade_id', sa.String(length=50), nullable=True),
        sa.Column('order_id', sa.String(length=50), nullable=True),
        sa.Column('bill_time', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建OKX行情数据表
    op.create_table('okx_market_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inst_id', sa.String(length=50), nullable=False),
        sa.Column('inst_type', sa.String(length=20), nullable=False),
        sa.Column('last_price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('best_bid', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('best_ask', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('open_24h', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('high_24h', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('low_24h', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('volume_24h', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('volume_currency_24h', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('change_24h', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('data_timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建OKX同步日志表
    op.create_table('okx_sync_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sync_type', sa.String(length=50), nullable=False),
        sa.Column('sync_status', sa.String(length=20), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=False, default=0),
        sa.Column('records_success', sa.Integer(), nullable=False, default=0),
        sa.Column('records_failed', sa.Integer(), nullable=False, default=0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('sync_params', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    # 账户余额表索引
    op.create_index('idx_okx_balance_currency', 'okx_account_balances', ['currency'])
    op.create_index('idx_okx_balance_currency_time', 'okx_account_balances', ['currency', 'data_timestamp'])
    op.create_constraint('uq_okx_balance', 'okx_account_balances', ['currency', 'data_timestamp'], type_='unique')
    
    # 持仓表索引
    op.create_index('idx_okx_position_inst', 'okx_positions', ['inst_id'])
    op.create_index('idx_okx_position_inst_time', 'okx_positions', ['inst_id', 'data_timestamp'])
    op.create_constraint('uq_okx_position', 'okx_positions', ['inst_id', 'position_side', 'data_timestamp'], type_='unique')
    
    # 交易记录表索引
    op.create_index('idx_okx_transaction_bill_id', 'okx_transactions', ['bill_id'])
    op.create_index('idx_okx_transaction_inst', 'okx_transactions', ['inst_id'])
    op.create_index('idx_okx_transaction_time', 'okx_transactions', ['bill_time'])
    op.create_index('idx_okx_transaction_currency', 'okx_transactions', ['currency'])
    op.create_index('idx_okx_transaction_type', 'okx_transactions', ['bill_type'])
    op.create_constraint('uq_okx_transaction', 'okx_transactions', ['bill_id'], type_='unique')
    
    # 行情数据表索引
    op.create_index('idx_okx_market_inst', 'okx_market_data', ['inst_id'])
    op.create_index('idx_okx_market_inst_time', 'okx_market_data', ['inst_id', 'data_timestamp'])
    op.create_constraint('uq_okx_market_data', 'okx_market_data', ['inst_id', 'data_timestamp'], type_='unique')
    
    # 同步日志表索引
    op.create_index('idx_okx_sync_log_type', 'okx_sync_logs', ['sync_type'])
    op.create_index('idx_okx_sync_log_type_time', 'okx_sync_logs', ['sync_type', 'start_time'])


def downgrade() -> None:
    """Downgrade schema."""
    
    # 删除索引和约束
    # 同步日志表
    op.drop_index('idx_okx_sync_log_type_time', table_name='okx_sync_logs')
    op.drop_index('idx_okx_sync_log_type', table_name='okx_sync_logs')
    
    # 行情数据表
    op.drop_constraint('uq_okx_market_data', 'okx_market_data', type_='unique')
    op.drop_index('idx_okx_market_inst_time', table_name='okx_market_data')
    op.drop_index('idx_okx_market_inst', table_name='okx_market_data')
    
    # 交易记录表
    op.drop_constraint('uq_okx_transaction', 'okx_transactions', type_='unique')
    op.drop_index('idx_okx_transaction_type', table_name='okx_transactions')
    op.drop_index('idx_okx_transaction_currency', table_name='okx_transactions')
    op.drop_index('idx_okx_transaction_time', table_name='okx_transactions')
    op.drop_index('idx_okx_transaction_inst', table_name='okx_transactions')
    op.drop_index('idx_okx_transaction_bill_id', table_name='okx_transactions')
    
    # 持仓表
    op.drop_constraint('uq_okx_position', 'okx_positions', type_='unique')
    op.drop_index('idx_okx_position_inst_time', table_name='okx_positions')
    op.drop_index('idx_okx_position_inst', table_name='okx_positions')
    
    # 账户余额表
    op.drop_constraint('uq_okx_balance', 'okx_account_balances', type_='unique')
    op.drop_index('idx_okx_balance_currency_time', table_name='okx_account_balances')
    op.drop_index('idx_okx_balance_currency', table_name='okx_account_balances')
    
    # 删除表
    op.drop_table('okx_sync_logs')
    op.drop_table('okx_market_data')
    op.drop_table('okx_transactions')
    op.drop_table('okx_positions')
    op.drop_table('okx_account_balances')