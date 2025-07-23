"""add incremental okx and wise balance

Revision ID: ffaaaaaa0000
Revises: ff5423642f10
Create Date: 2024-07-22 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'ffaaaaaa0000'
down_revision: Union[str, Sequence[str], None] = 'ff5423642f10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # OKX余额表去除唯一约束，添加联合索引
    op.drop_constraint('uq_okx_balance', 'okx_balances', type_='unique')
    op.create_index('idx_okx_balance_latest', 'okx_balances', ['account_id', 'currency', 'account_type', 'update_time'])
    # Wise余额表去除唯一约束，添加联合索引
    op.drop_constraint('uq_wise_balance', 'wise_balances', type_='unique')
    op.create_index('idx_wise_balance_latest', 'wise_balances', ['account_id', 'currency', 'update_time'])

def downgrade() -> None:
    op.drop_index('idx_okx_balance_latest', table_name='okx_balances')
    op.create_unique_constraint('uq_okx_balance', 'okx_balances', ['account_id', 'currency', 'account_type'])
    op.drop_index('idx_wise_balance_latest', table_name='wise_balances')
    op.create_unique_constraint('uq_wise_balance', 'wise_balances', ['account_id'])