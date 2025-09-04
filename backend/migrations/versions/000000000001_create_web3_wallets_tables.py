"""create web3 wallets tables

Revision ID: web3_wallets_001
Revises: 000000000000_complete_schema
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'web3_wallets_001'
down_revision = '000000000000_complete_schema'
branch_labels = None
depends_on = None


def upgrade():
    # 1. 创建web3_wallets表
    op.create_table('web3_wallets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('wallet_address', sa.String(length=42), nullable=False),
        sa.Column('wallet_name', sa.String(length=50), nullable=True),
        sa.Column('chain_type', sa.String(length=20), nullable=False),
        sa.Column('connection_type', sa.String(length=20), nullable=False),
        sa.Column('last_sync_time', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wallet_address', 'chain_type', name='uq_wallet_chain')
    )
    
    # 创建索引
    op.create_index('idx_web3_wallets_user', 'web3_wallets', ['user_id'])
    op.create_index('idx_web3_wallets_address', 'web3_wallets', ['wallet_address'])
    op.create_index('idx_web3_wallets_type', 'web3_wallets', ['connection_type', 'chain_type'])
    
    # 2. 创建web3_wallet_balances表
    op.create_table('web3_wallet_balances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wallet_id', sa.Integer(), nullable=False),
        sa.Column('chain', sa.String(length=20), nullable=False),
        sa.Column('token_symbol', sa.String(length=10), nullable=False),
        sa.Column('token_name', sa.String(length=100), nullable=True),
        sa.Column('token_address', sa.String(length=100), nullable=True),
        sa.Column('balance', sa.DECIMAL(precision=30, scale=18), nullable=False),
        sa.Column('balance_formatted', sa.String(length=50), nullable=True),
        sa.Column('usdt_price', sa.DECIMAL(precision=15, scale=8), nullable=True),
        sa.Column('usdt_value', sa.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('is_native_token', sa.Boolean(), nullable=True, default=False),
        sa.Column('sync_time', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['wallet_id'], ['web3_wallets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('idx_balances_wallet_time', 'web3_wallet_balances', ['wallet_id', 'sync_time'])
    op.create_index('idx_balances_symbol', 'web3_wallet_balances', ['token_symbol'])
    op.create_index('idx_balances_sync_time', 'web3_wallet_balances', ['sync_time'])
    
    # 3. 创建web3_token_prices表
    op.create_table('web3_token_prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token_symbol', sa.String(length=10), nullable=False),
        sa.Column('token_address', sa.String(length=100), nullable=True),
        sa.Column('chain', sa.String(length=20), nullable=False),
        sa.Column('usdt_price', sa.DECIMAL(precision=15, scale=8), nullable=False),
        sa.Column('coingecko_id', sa.String(length=100), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_symbol', 'chain', 'token_address', name='uq_token_price')
    )
    
    # 创建索引
    op.create_index('idx_prices_symbol', 'web3_token_prices', ['token_symbol'])
    op.create_index('idx_prices_updated', 'web3_token_prices', ['last_updated'])


def downgrade():
    # 删除表
    op.drop_table('web3_token_prices')
    op.drop_table('web3_wallet_balances')
    op.drop_table('web3_wallets')