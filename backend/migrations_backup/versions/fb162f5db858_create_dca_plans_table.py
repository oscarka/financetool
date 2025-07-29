"""create_dca_plans_table

Revision ID: fb162f5db858
Revises: ffcccccc0004
Create Date: 2025-07-28 11:20:53.481826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fb162f5db858'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'dca_plans',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('plan_name', sa.String(length=100), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=False, server_default='基金'),
        sa.Column('asset_code', sa.String(length=50), nullable=False),
        sa.Column('asset_name', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('frequency', sa.String(length=20), nullable=False),
        sa.Column('frequency_value', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date()),
        sa.Column('status', sa.String(length=20), server_default='active'),
        sa.Column('strategy', sa.Text()),
        sa.Column('execution_time', sa.String(length=10), server_default='15:00'),
        sa.Column('next_execution_date', sa.Date()),
        sa.Column('last_execution_date', sa.Date()),
        sa.Column('execution_count', sa.Integer(), server_default='0'),
        sa.Column('total_invested', sa.DECIMAL(15, 4), server_default='0'),
        sa.Column('total_shares', sa.DECIMAL(15, 8), server_default='0'),
        sa.Column('smart_dca', sa.Boolean(), server_default='false'),
        sa.Column('base_amount', sa.DECIMAL(10, 2)),
        sa.Column('max_amount', sa.DECIMAL(10, 2)),
        sa.Column('increase_rate', sa.DECIMAL(5, 4)),
        sa.Column('min_nav', sa.DECIMAL(10, 4)),
        sa.Column('max_nav', sa.DECIMAL(10, 4)),
        sa.Column('skip_holidays', sa.Boolean(), server_default='true'),
        sa.Column('enable_notification', sa.Boolean(), server_default='true'),
        sa.Column('notification_before', sa.Integer(), server_default='30'),
        sa.Column('fee_rate', sa.DECIMAL(5, 4), server_default='0'),
        sa.Column('exclude_dates', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('dca_plans')
