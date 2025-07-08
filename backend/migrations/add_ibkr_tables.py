"""Add IBKR tables

Revision ID: ibkr_001
Revises: 
Create Date: 2024-12-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ibkr_001'
down_revision = None  # 根据实际情况调整
branch_labels = None
depends_on = None


def upgrade():
    # 创建 ibkr_accounts 表
    op.create_table(
        'ibkr_accounts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('account_id', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('account_name', sa.String(100)),
        sa.Column('account_type', sa.String(50), default='INDIVIDUAL'),
        sa.Column('base_currency', sa.String(10), default='USD'),
        sa.Column('status', sa.String(20), default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # 创建 ibkr_balances 表
    op.create_table(
        'ibkr_balances',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('account_id', sa.String(50), nullable=False, index=True),
        sa.Column('total_cash', sa.DECIMAL(15, 2), nullable=False, default=0),
        sa.Column('net_liquidation', sa.DECIMAL(15, 2), nullable=False, default=0),
        sa.Column('buying_power', sa.DECIMAL(15, 2), nullable=False, default=0),
        sa.Column('currency', sa.String(10), nullable=False, default='USD'),
        sa.Column('snapshot_date', sa.Date(), nullable=False, index=True),
        sa.Column('snapshot_time', sa.DateTime(), nullable=False),
        sa.Column('sync_source', sa.String(50), default='gcp_scheduler'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('account_id', 'snapshot_date', 'snapshot_time', name='uq_ibkr_balance'),
        sa.ForeignKeyConstraint(['account_id'], ['ibkr_accounts.account_id'], ondelete='CASCADE')
    )
    
    # 创建 ibkr_positions 表
    op.create_table(
        'ibkr_positions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('account_id', sa.String(50), nullable=False, index=True),
        sa.Column('symbol', sa.String(20), nullable=False, index=True),
        sa.Column('quantity', sa.DECIMAL(15, 6), nullable=False, default=0),
        sa.Column('market_value', sa.DECIMAL(15, 2), nullable=False, default=0),
        sa.Column('average_cost', sa.DECIMAL(15, 2), nullable=False, default=0),
        sa.Column('unrealized_pnl', sa.DECIMAL(15, 2), default=0),
        sa.Column('realized_pnl', sa.DECIMAL(15, 2), default=0),
        sa.Column('currency', sa.String(10), nullable=False, default='USD'),
        sa.Column('asset_class', sa.String(50), default='STK'),
        sa.Column('snapshot_date', sa.Date(), nullable=False, index=True),
        sa.Column('snapshot_time', sa.DateTime(), nullable=False),
        sa.Column('sync_source', sa.String(50), default='gcp_scheduler'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('account_id', 'symbol', 'snapshot_date', 'snapshot_time', name='uq_ibkr_position'),
        sa.ForeignKeyConstraint(['account_id'], ['ibkr_accounts.account_id'], ondelete='CASCADE')
    )
    
    # 创建 ibkr_sync_logs 表
    op.create_table(
        'ibkr_sync_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('account_id', sa.String(50), index=True),
        sa.Column('sync_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, index=True),
        sa.Column('request_data', sa.Text()),
        sa.Column('response_data', sa.Text()),
        sa.Column('error_message', sa.Text()),
        sa.Column('records_processed', sa.Integer(), default=0),
        sa.Column('records_updated', sa.Integer(), default=0),
        sa.Column('records_inserted', sa.Integer(), default=0),
        sa.Column('source_ip', sa.String(50)),
        sa.Column('user_agent', sa.String(200)),
        sa.Column('sync_duration_ms', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), index=True)
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


def downgrade():
    # 删除索引
    op.drop_index('idx_ibkr_sync_logs_account', 'ibkr_sync_logs')
    op.drop_index('idx_ibkr_sync_logs_date', 'ibkr_sync_logs')
    op.drop_index('idx_ibkr_sync_logs_status', 'ibkr_sync_logs')
    op.drop_index('idx_ibkr_positions_date', 'ibkr_positions')
    op.drop_index('idx_ibkr_positions_symbol', 'ibkr_positions')
    op.drop_index('idx_ibkr_positions_account', 'ibkr_positions')
    op.drop_index('idx_ibkr_balances_date', 'ibkr_balances')
    op.drop_index('idx_ibkr_balances_account', 'ibkr_balances')
    op.drop_index('idx_ibkr_accounts_id', 'ibkr_accounts')
    
    # 删除表（按相反顺序，考虑外键约束）
    op.drop_table('ibkr_sync_logs')
    op.drop_table('ibkr_positions')
    op.drop_table('ibkr_balances')
    op.drop_table('ibkr_accounts')