"""add_fund_dividend_table

Revision ID: 94e7ccaad3b2
Revises: 843fdae84b37
Create Date: 2025-07-03 17:52:50.820299

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94e7ccaad3b2'
down_revision: Union[str, Sequence[str], None] = '843fdae84b37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 创建基金分红表
    op.create_table('fund_dividend',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fund_code', sa.String(length=10), nullable=False),
        sa.Column('dividend_date', sa.Date(), nullable=False),
        sa.Column('record_date', sa.Date(), nullable=True),
        sa.Column('dividend_amount', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('total_dividend', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('announcement_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建唯一索引，防止重复分红记录
    op.create_index('idx_fund_dividend_unique', 'fund_dividend', ['fund_code', 'dividend_date'], unique=True)
    
    # 创建普通索引，提高查询性能
    op.create_index('idx_fund_dividend_fund_code', 'fund_dividend', ['fund_code'])
    op.create_index('idx_fund_dividend_date', 'fund_dividend', ['dividend_date'])


def downgrade() -> None:
    """Downgrade schema."""
    # 删除索引
    op.drop_index('idx_fund_dividend_date', table_name='fund_dividend')
    op.drop_index('idx_fund_dividend_fund_code', table_name='fund_dividend')
    op.drop_index('idx_fund_dividend_unique', table_name='fund_dividend')
    
    # 删除表
    op.drop_table('fund_dividend')
