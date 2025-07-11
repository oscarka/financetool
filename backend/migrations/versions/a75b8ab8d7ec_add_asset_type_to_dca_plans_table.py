"""add asset_type to dca_plans table

Revision ID: a75b8ab8d7ec
Revises: 
Create Date: 2024-07-02 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a75b8ab8d7ec'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dca_plans', sa.Column('asset_type', sa.String(length=50), nullable=False, server_default='基金'))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('dca_plans', 'asset_type')
    # ### end Alembic commands ###
