"""remove account_id unique constraint/index from wise_balances

Revision ID: ffbbbbbb0001
Revises: ffaaaaaa0000
Create Date: 2024-07-23 13:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'ffbbbbbb0001'
down_revision: Union[str, Sequence[str], None] = 'ffaaaaaa0000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 去除account_id唯一约束/唯一索引
    with op.batch_alter_table('wise_balances') as batch_op:
        # 先尝试删除唯一约束
        try:
            batch_op.drop_constraint('uq_wise_balance', type_='unique')
        except Exception:
            pass
        # 再尝试删除唯一索引
        try:
            batch_op.drop_index('ix_wise_balances_account_id')
        except Exception:
            pass

def downgrade() -> None:
    # 恢复唯一约束
    with op.batch_alter_table('wise_balances') as batch_op:
        batch_op.create_unique_constraint('uq_wise_balance', ['account_id'])