"""
expand okx_transactions to store all OKX bills-archive fields
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ffbbbbbb9999'
down_revision = 'ffcccccc0004'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('okx_transactions') as batch_op:
        batch_op.add_column(sa.Column('bal', sa.String(32)))
        batch_op.add_column(sa.Column('bal_chg', sa.String(32)))
        batch_op.add_column(sa.Column('ccy', sa.String(10)))
        batch_op.add_column(sa.Column('cl_ord_id', sa.String(64)))
        batch_op.add_column(sa.Column('exec_type', sa.String(16)))
        batch_op.add_column(sa.Column('fill_fwd_px', sa.String(32)))
        batch_op.add_column(sa.Column('fill_idx_px', sa.String(32)))
        batch_op.add_column(sa.Column('fill_mark_px', sa.String(32)))
        batch_op.add_column(sa.Column('fill_mark_vol', sa.String(32)))
        batch_op.add_column(sa.Column('fill_px_usd', sa.String(32)))
        batch_op.add_column(sa.Column('fill_px_vol', sa.String(32)))
        batch_op.add_column(sa.Column('fill_time', sa.String(32)))
        batch_op.add_column(sa.Column('from_addr', sa.String(64)))
        batch_op.add_column(sa.Column('interest', sa.String(32)))
        batch_op.add_column(sa.Column('mgn_mode', sa.String(16)))
        batch_op.add_column(sa.Column('notes', sa.Text))
        batch_op.add_column(sa.Column('pnl', sa.String(32)))
        batch_op.add_column(sa.Column('pos_bal', sa.String(32)))
        batch_op.add_column(sa.Column('pos_bal_chg', sa.String(32)))
        batch_op.add_column(sa.Column('sub_type', sa.String(16)))
        batch_op.add_column(sa.Column('tag', sa.String(32)))
        batch_op.add_column(sa.Column('to_addr', sa.String(64)))
        # 兼容未来账单字段

def downgrade():
    with op.batch_alter_table('okx_transactions') as batch_op:
        # 检查字段是否存在再删除，避免KeyError
        columns_to_drop = [
            'bal', 'bal_chg', 'ccy', 'cl_ord_id', 'exec_type', 'fill_fwd_px',
            'fill_idx_px', 'fill_mark_px', 'fill_mark_vol', 'fill_px_usd',
            'fill_px_vol', 'fill_time', 'from_addr', 'interest', 'mgn_mode',
            'notes', 'pnl', 'pos_bal', 'pos_bal_chg', 'sub_type', 'tag', 'to_addr'
        ]
        
        for column_name in columns_to_drop:
            if column_name in batch_op.columns:
                batch_op.drop_column(column_name) 
