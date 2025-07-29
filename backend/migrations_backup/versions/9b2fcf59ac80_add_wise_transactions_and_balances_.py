"""add_wise_transactions_and_balances_tables

Revision ID: 9b2fcf59ac80
Revises: f9adc45cf4ec
Create Date: 2025-07-06 22:27:45.713024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b2fcf59ac80'
down_revision: Union[str, Sequence[str], None] = 'f9adc45cf4ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 创建 wise_transactions 表
    op.create_table('wise_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('profile_id', sa.String(length=50), nullable=False),
        sa.Column('account_id', sa.String(length=50), nullable=False),
        sa.Column('transaction_id', sa.String(length=200), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=15, scale=4), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id', name='uq_wise_transaction')
    )
    op.create_index('idx_wise_transaction_date', 'wise_transactions', ['date'])
    op.create_index('idx_wise_transaction_profile', 'wise_transactions', ['profile_id'])
    op.create_index('idx_wise_transaction_account', 'wise_transactions', ['account_id'])

    # 创建 wise_balances 表
    op.create_table('wise_balances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.String(length=50), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('available_balance', sa.DECIMAL(precision=15, scale=4), nullable=False),
        sa.Column('reserved_balance', sa.DECIMAL(precision=15, scale=4), nullable=False),
        sa.Column('cash_amount', sa.DECIMAL(precision=15, scale=4), nullable=False),
        sa.Column('total_worth', sa.DECIMAL(precision=15, scale=4), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('investment_state', sa.String(length=50), nullable=False),
        sa.Column('creation_time', sa.DateTime(), nullable=False),
        sa.Column('modification_time', sa.DateTime(), nullable=False),
        sa.Column('visible', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('primary', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('update_time', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_id', name='uq_wise_balance')
    )
    op.create_index('idx_wise_balance_currency', 'wise_balances', ['currency'])

    # 创建 wise_exchange_rates 表
    op.create_table('wise_exchange_rates',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('source_currency', sa.String(length=8), nullable=False),
        sa.Column('target_currency', sa.String(length=8), nullable=False),
        sa.Column('rate', sa.Float(), nullable=False),
        sa.Column('time', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('wise_exchange_rates')
    op.drop_index('idx_wise_balance_currency', table_name='wise_balances')
    op.drop_table('wise_balances')
    op.drop_index('idx_wise_transaction_account', table_name='wise_transactions')
    op.drop_index('idx_wise_transaction_profile', table_name='wise_transactions')
    op.drop_index('idx_wise_transaction_date', table_name='wise_transactions')
    op.drop_table('wise_transactions')
    # ### end Alembic commands ###
