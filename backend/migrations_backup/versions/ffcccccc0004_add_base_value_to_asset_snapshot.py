"""add base_value to asset_snapshot table

Revision ID: ffcccccc0004
Revises: ffcccccc0003
Create Date: 2024-07-24 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'ffcccccc0004'
down_revision = 'ffcccccc0003'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('asset_snapshot', sa.Column('base_value', sa.Numeric(20, 8)))

def downgrade():
    op.drop_column('asset_snapshot', 'base_value')