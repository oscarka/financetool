"""add asset and exchange rate snapshot tables

Revision ID: ffcccccc0003
Revises: ffcccccc0002
Create Date: 2024-07-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'ffcccccc0003'
down_revision = 'ffcccccc0002'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'asset_snapshot',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), index=True),
        sa.Column('platform', sa.String(length=50), index=True),
        sa.Column('asset_type', sa.String(length=50), index=True),
        sa.Column('asset_code', sa.String(length=50), index=True),
        sa.Column('asset_name', sa.String(length=100)),
        sa.Column('currency', sa.String(length=10), index=True),
        sa.Column('balance', sa.Numeric(20, 8), nullable=False),
        sa.Column('balance_cny', sa.Numeric(20, 8)),
        sa.Column('balance_usd', sa.Numeric(20, 8)),
        sa.Column('balance_eur', sa.Numeric(20, 8)),
        sa.Column('snapshot_time', sa.DateTime(), index=True),
        sa.Column('extra', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        'exchange_rate_snapshot',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('from_currency', sa.String(length=10), index=True),
        sa.Column('to_currency', sa.String(length=10), index=True),
        sa.Column('rate', sa.Numeric(20, 8), nullable=False),
        sa.Column('snapshot_time', sa.DateTime(), index=True),
        sa.Column('source', sa.String(length=50)),
        sa.Column('extra', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('exchange_rate_snapshot')
    op.drop_table('asset_snapshot')