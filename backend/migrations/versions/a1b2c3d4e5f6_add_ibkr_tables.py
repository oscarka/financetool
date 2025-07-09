"""add_ibkr_tables

Revision ID: a1b2c3d4e5f6
Revises: 9b2fcf59ac80
Create Date: 2024-12-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '9b2fcf59ac80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 创建 ibkr_accounts 表
    op.create_table('ibkr_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.String(length=50), nullable=False),
        sa.Column('account_name', sa.String(length=100), nullable=True),
        sa.Column('account_type', sa.String(length=50), nullable=True, server_default='INDIVIDUAL'),
        sa.Column('base_currency', sa.String(length=10), nullable=True, server_default='USD'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_id')
    )
    
    # 创建 ibkr_balances 表
    op.create_table('ibkr_balances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.String(length=50), nullable=False),
        sa.Column('total_cash', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('net_liquidation', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('buying_power', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('snapshot_time', sa.DateTime(), nullable=False),
        sa.Column('sync_source', sa.String(length=50), nullable=True, server_default='gcp_scheduler'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_id', 'snapshot_date', 'snapshot_time', name='uq_ibkr_balance'),
        sa.ForeignKeyConstraint(['account_id'], ['ibkr_accounts.account_id'], ondelete='CASCADE')
    )
    
    # 创建 ibkr_positions 表
    op.create_table('ibkr_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.String(length=50), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=15, scale=6), nullable=False, server_default='0'),
        sa.Column('market_value', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('average_cost', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('unrealized_pnl', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('realized_pnl', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('asset_class', sa.String(length=50), nullable=True, server_default='STK'),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('snapshot_time', sa.DateTime(), nullable=False),
        sa.Column('sync_source', sa.String(length=50), nullable=True, server_default='gcp_scheduler'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_id', 'symbol', 'snapshot_date', 'snapshot_time', name='uq_ibkr_position'),
        sa.ForeignKeyConstraint(['account_id'], ['ibkr_accounts.account_id'], ondelete='CASCADE')
    )
    
    # 创建 ibkr_sync_logs 表
    op.create_table('ibkr_sync_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.String(length=50), nullable=True),
        sa.Column('sync_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('request_data', sa.Text(), nullable=True),
        sa.Column('response_data', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('records_updated', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('records_inserted', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('source_ip', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=200), nullable=True),
        sa.Column('sync_duration_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('idx_ibkr_accounts_id', 'ibkr_accounts', ['account_id'])
    op.create_index('idx_ibkr_balances_account', 'ibkr_balances', ['account_id'])
    op.create_index('idx_ibkr_balances_date', 'ibkr_balances', ['snapshot_date'])
    op.create_index('idx_ibkr_positions_account', 'ibkr_positions', ['account_id'])
    op.create_index('idx_ibkr_positions_symbol', 'ibkr_positions', ['symbol'])
    op.create_index('idx_ibkr_positions_date', 'ibkr_positions', ['snapshot_date'])
    op.create_index('idx_ibkr_sync_logs_status', 'ibkr_sync_logs', ['status'])
    op.create_index('idx_ibkr_sync_logs_date', 'ibkr_sync_logs', ['created_at'])
    op.create_index('idx_ibkr_sync_logs_account', 'ibkr_sync_logs', ['account_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # 删除索引
    op.drop_index('idx_ibkr_sync_logs_account', table_name='ibkr_sync_logs')
    op.drop_index('idx_ibkr_sync_logs_date', table_name='ibkr_sync_logs')
    op.drop_index('idx_ibkr_sync_logs_status', table_name='ibkr_sync_logs')
    op.drop_index('idx_ibkr_positions_date', table_name='ibkr_positions')
    op.drop_index('idx_ibkr_positions_symbol', table_name='ibkr_positions')
    op.drop_index('idx_ibkr_positions_account', table_name='ibkr_positions')
    op.drop_index('idx_ibkr_balances_date', table_name='ibkr_balances')
    op.drop_index('idx_ibkr_balances_account', table_name='ibkr_balances')
    op.drop_index('idx_ibkr_accounts_id', table_name='ibkr_accounts')
    
    # 删除表（按相反顺序，考虑外键约束）
    op.drop_table('ibkr_sync_logs')
    op.drop_table('ibkr_positions')
    op.drop_table('ibkr_balances')
    op.drop_table('ibkr_accounts')