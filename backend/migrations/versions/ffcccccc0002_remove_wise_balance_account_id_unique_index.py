"""remove unique index ix_wise_balances_account_id from wise_balances

Revision ID: ffcccccc0002
Revises: ffaaaaaa0000
Create Date: 2024-07-23 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'ffcccccc0002'
down_revision: Union[str, Sequence[str], None] = 'ffaaaaaa0000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    with op.batch_alter_table('wise_balances') as batch_op:
        batch_op.drop_index('ix_wise_balances_account_id')

def downgrade() -> None:
    with op.batch_alter_table('wise_balances') as batch_op:
        batch_op.create_index('ix_wise_balances_account_id', ['account_id'], unique=True)