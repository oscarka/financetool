"""merge branches

Revision ID: dfb94dae43ef
Revises: 48eb42b82dd4, ffcccccc0004
Create Date: 2025-07-28 11:42:19.043144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dfb94dae43ef'
down_revision: Union[str, Sequence[str], None] = ('48eb42b82dd4', 'ffcccccc0004')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
