"""add_okx_tables

Revision ID: c56f9f034ac1
Revises: 1c00ade64ab5
Create Date: 2025-07-17 15:38:29.608590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'c56f9f034ac1'
down_revision: Union[str, Sequence[str], None] = '1c00ade64ab5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    print('[MIGRATION] 尝试DROP索引: ix_okx_market_data_id')
    op.execute(text("DROP INDEX IF EXISTS ix_okx_market_data_id"))
    print('[MIGRATION] 创建索引: ix_okx_market_data_id')
    op.create_index(op.f('ix_okx_market_data_id'), 'okx_market_data', ['id'], unique=False)
    print('[MIGRATION] 尝试DROP索引: ix_okx_market_data_inst_id')
    op.execute(text("DROP INDEX IF EXISTS ix_okx_market_data_inst_id"))
    print('[MIGRATION] 创建索引: ix_okx_market_data_inst_id')
    op.create_index(op.f('ix_okx_market_data_inst_id'), 'okx_market_data', ['inst_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_okx_market_data_inst_id'), table_name='okx_market_data')
    op.drop_index(op.f('ix_okx_market_data_id'), table_name='okx_market_data')
    # ### end Alembic commands ###
