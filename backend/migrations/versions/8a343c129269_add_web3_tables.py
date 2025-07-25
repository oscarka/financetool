"""add_web3_tables

Revision ID: 8a343c129269
Revises: 033880ebf93b
Create Date: 2025-07-18 15:00:31.250119

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '8a343c129269'
down_revision: Union[str, Sequence[str], None] = '033880ebf93b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('web3_balances',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.String(length=100), nullable=False),
    sa.Column('account_id', sa.String(length=100), nullable=False),
    sa.Column('total_value', sa.DECIMAL(precision=20, scale=8), nullable=False),
    sa.Column('currency', sa.String(length=10), nullable=False),
    sa.Column('update_time', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_id', 'account_id', 'update_time', name='uq_web3_balance')
    )
    op.execute(text("DROP INDEX IF EXISTS ix_web3_balances_account_id"))
    op.create_index(op.f('ix_web3_balances_account_id'), 'web3_balances', ['account_id'], unique=False)
    op.execute(text("DROP INDEX IF EXISTS ix_web3_balances_id"))
    op.create_index(op.f('ix_web3_balances_id'), 'web3_balances', ['id'], unique=False)
    op.execute(text("DROP INDEX IF EXISTS ix_web3_balances_project_id"))
    op.create_index(op.f('ix_web3_balances_project_id'), 'web3_balances', ['project_id'], unique=False)
    op.execute(text("DROP INDEX IF EXISTS ix_web3_balances_update_time"))
    op.create_index(op.f('ix_web3_balances_update_time'), 'web3_balances', ['update_time'], unique=False)
    op.create_table('web3_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.String(length=100), nullable=False),
    sa.Column('account_id', sa.String(length=100), nullable=False),
    sa.Column('token_symbol', sa.String(length=20), nullable=False),
    sa.Column('token_name', sa.String(length=100), nullable=False),
    sa.Column('token_address', sa.String(length=100), nullable=True),
    sa.Column('balance', sa.DECIMAL(precision=20, scale=8), nullable=False),
    sa.Column('value_usd', sa.DECIMAL(precision=20, scale=8), nullable=False),
    sa.Column('price_usd', sa.DECIMAL(precision=20, scale=8), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_id', 'account_id', 'token_symbol', 'update_time', name='uq_web3_token')
    )
    op.execute(text("DROP INDEX IF EXISTS ix_web3_tokens_account_id"))
    op.create_index(op.f('ix_web3_tokens_account_id'), 'web3_tokens', ['account_id'], unique=False)
    op.execute(text("DROP INDEX IF EXISTS ix_web3_tokens_id"))
    op.create_index(op.f('ix_web3_tokens_id'), 'web3_tokens', ['id'], unique=False)
    op.execute(text("DROP INDEX IF EXISTS ix_web3_tokens_project_id"))
    op.create_index(op.f('ix_web3_tokens_project_id'), 'web3_tokens', ['project_id'], unique=False)
    op.execute(text("DROP INDEX IF EXISTS ix_web3_tokens_token_symbol"))
    op.create_index(op.f('ix_web3_tokens_token_symbol'), 'web3_tokens', ['token_symbol'], unique=False)
    op.execute(text("DROP INDEX IF EXISTS ix_web3_tokens_update_time"))
    op.create_index(op.f('ix_web3_tokens_update_time'), 'web3_tokens', ['update_time'], unique=False)
    op.create_table('web3_transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.String(length=100), nullable=False),
    sa.Column('account_id', sa.String(length=100), nullable=False),
    sa.Column('transaction_hash', sa.String(length=100), nullable=False),
    sa.Column('block_number', sa.Integer(), nullable=True),
    sa.Column('from_address', sa.String(length=100), nullable=True),
    sa.Column('to_address', sa.String(length=100), nullable=True),
    sa.Column('token_symbol', sa.String(length=20), nullable=True),
    sa.Column('amount', sa.DECIMAL(precision=20, scale=8), nullable=False),
    sa.Column('value_usd', sa.DECIMAL(precision=20, scale=8), nullable=True),
    sa.Column('gas_used', sa.DECIMAL(precision=20, scale=8), nullable=True),
    sa.Column('gas_price', sa.DECIMAL(precision=20, scale=8), nullable=True),
    sa.Column('transaction_type', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('transaction_hash', name='uq_web3_transaction')
    )
    op.execute(text("DROP INDEX IF EXISTS ix_web3_transactions_account_id"))
    op.create_index(op.f('ix_web3_transactions_account_id'), 'web3_transactions', ['account_id'], unique=False)
    op.execute(text("DROP INDEX IF EXISTS ix_web3_transactions_id"))
    op.create_index(op.f('ix_web3_transactions_id'), 'web3_transactions', ['id'], unique=False)
    op.execute(text("DROP INDEX IF EXISTS ix_web3_transactions_project_id"))
    op.create_index(op.f('ix_web3_transactions_project_id'), 'web3_transactions', ['project_id'], unique=False)
    op.execute(text("DROP INDEX IF EXISTS ix_web3_transactions_timestamp"))
    op.create_index(op.f('ix_web3_transactions_timestamp'), 'web3_transactions', ['timestamp'], unique=False)
    op.execute(text("DROP INDEX IF EXISTS ix_web3_transactions_token_symbol"))
    op.create_index(op.f('ix_web3_transactions_token_symbol'), 'web3_transactions', ['token_symbol'], unique=False)
    op.execute(text("DROP INDEX IF EXISTS ix_web3_transactions_transaction_hash"))
    op.create_index(op.f('ix_web3_transactions_transaction_hash'), 'web3_transactions', ['transaction_hash'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_web3_transactions_transaction_hash'), table_name='web3_transactions')
    op.drop_index(op.f('ix_web3_transactions_token_symbol'), table_name='web3_transactions')
    op.drop_index(op.f('ix_web3_transactions_timestamp'), table_name='web3_transactions')
    op.drop_index(op.f('ix_web3_transactions_project_id'), table_name='web3_transactions')
    op.drop_index(op.f('ix_web3_transactions_id'), table_name='web3_transactions')
    op.drop_index(op.f('ix_web3_transactions_account_id'), table_name='web3_transactions')
    op.drop_table('web3_transactions')
    op.drop_index(op.f('ix_web3_tokens_update_time'), table_name='web3_tokens')
    op.drop_index(op.f('ix_web3_tokens_token_symbol'), table_name='web3_tokens')
    op.drop_index(op.f('ix_web3_tokens_project_id'), table_name='web3_tokens')
    op.drop_index(op.f('ix_web3_tokens_id'), table_name='web3_tokens')
    op.drop_index(op.f('ix_web3_tokens_account_id'), table_name='web3_tokens')
    op.drop_table('web3_tokens')
    op.drop_index(op.f('ix_web3_balances_update_time'), table_name='web3_balances')
    op.drop_index(op.f('ix_web3_balances_project_id'), table_name='web3_balances')
    op.drop_index(op.f('ix_web3_balances_id'), table_name='web3_balances')
    op.drop_index(op.f('ix_web3_balances_account_id'), table_name='web3_balances')
    op.drop_table('web3_balances')
    # ### end Alembic commands ###
