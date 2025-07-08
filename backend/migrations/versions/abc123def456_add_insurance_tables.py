"""add_insurance_tables

Revision ID: abc123def456
Revises: f9adc45cf4ec
Create Date: 2025-01-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abc123def456'
down_revision: Union[str, Sequence[str], None] = 'f9adc45cf4ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # 创建保险产品信息表
    op.create_table('insurance_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_code', sa.String(length=50), nullable=False),
        sa.Column('product_name', sa.String(length=200), nullable=False),
        sa.Column('insurance_company', sa.String(length=100), nullable=False),
        sa.Column('product_type', sa.String(length=50), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('min_premium', sa.DECIMAL(precision=15, scale=4), nullable=True),
        sa.Column('max_premium', sa.DECIMAL(precision=15, scale=4), nullable=True),
        sa.Column('payment_frequency', sa.String(length=20), nullable=True),
        sa.Column('initial_charge_rate', sa.DECIMAL(precision=5, scale=4), nullable=True),
        sa.Column('management_fee_rate', sa.DECIMAL(precision=5, scale=4), nullable=True),
        sa.Column('surrender_charge_rate', sa.DECIMAL(precision=5, scale=4), nullable=True),
        sa.Column('guaranteed_rate', sa.DECIMAL(precision=5, scale=4), nullable=True),
        sa.Column('current_rate', sa.DECIMAL(precision=5, scale=4), nullable=True),
        sa.Column('rate_type', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_insurance_product_code', 'insurance_products', ['product_code'], unique=True)
    op.create_index('idx_insurance_product_company', 'insurance_products', ['insurance_company'])
    op.create_index('idx_insurance_product_type', 'insurance_products', ['product_type'])
    
    # 创建保险保单表
    op.create_table('insurance_policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('policy_number', sa.String(length=100), nullable=False),
        sa.Column('product_code', sa.String(length=50), nullable=False),
        sa.Column('product_name', sa.String(length=200), nullable=False),
        sa.Column('insurance_company', sa.String(length=100), nullable=False),
        sa.Column('policy_holder', sa.String(length=100), nullable=False),
        sa.Column('insured_person', sa.String(length=100), nullable=False),
        sa.Column('beneficiary', sa.String(length=200), nullable=True),
        sa.Column('policy_start_date', sa.Date(), nullable=False),
        sa.Column('policy_end_date', sa.Date(), nullable=True),
        sa.Column('payment_start_date', sa.Date(), nullable=False),
        sa.Column('payment_end_date', sa.Date(), nullable=True),
        sa.Column('sum_insured', sa.DECIMAL(precision=15, scale=4), nullable=False),
        sa.Column('annual_premium', sa.DECIMAL(precision=15, scale=4), nullable=False),
        sa.Column('payment_frequency', sa.String(length=20), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('current_cash_value', sa.DECIMAL(precision=15, scale=4), nullable=False, server_default='0'),
        sa.Column('guaranteed_cash_value', sa.DECIMAL(precision=15, scale=4), nullable=False, server_default='0'),
        sa.Column('account_value', sa.DECIMAL(precision=15, scale=4), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_insurance_policy_number', 'insurance_policies', ['policy_number'], unique=True)
    op.create_index('idx_insurance_policy_product_code', 'insurance_policies', ['product_code'])
    op.create_index('idx_insurance_policy_company', 'insurance_policies', ['insurance_company'])
    op.create_index('idx_insurance_policy_status', 'insurance_policies', ['status'])
    op.create_index('idx_insurance_policy_start_date', 'insurance_policies', ['policy_start_date'])
    
    # 创建保险操作记录表
    op.create_table('insurance_operations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('policy_number', sa.String(length=100), nullable=False),
        sa.Column('operation_date', sa.DateTime(), nullable=False),
        sa.Column('operation_type', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=15, scale=4), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('exchange_rate', sa.DECIMAL(precision=15, scale=6), nullable=True),
        sa.Column('amount_cny', sa.DECIMAL(precision=15, scale=4), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('cash_value_before', sa.DECIMAL(precision=15, scale=4), nullable=True),
        sa.Column('cash_value_after', sa.DECIMAL(precision=15, scale=4), nullable=True),
        sa.Column('account_value_before', sa.DECIMAL(precision=15, scale=4), nullable=True),
        sa.Column('account_value_after', sa.DECIMAL(precision=15, scale=4), nullable=True),
        sa.Column('initial_charge', sa.DECIMAL(precision=15, scale=4), nullable=False, server_default='0'),
        sa.Column('management_fee', sa.DECIMAL(precision=15, scale=4), nullable=False, server_default='0'),
        sa.Column('insurance_cost', sa.DECIMAL(precision=15, scale=4), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='confirmed'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_insurance_operation_policy_id', 'insurance_operations', ['policy_id'])
    op.create_index('idx_insurance_operation_policy_number', 'insurance_operations', ['policy_number'])
    op.create_index('idx_insurance_operation_date', 'insurance_operations', ['operation_date'])
    op.create_index('idx_insurance_operation_type', 'insurance_operations', ['operation_type'])
    
    # 创建保险收益记录表
    op.create_table('insurance_returns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('policy_number', sa.String(length=100), nullable=False),
        sa.Column('return_date', sa.Date(), nullable=False),
        sa.Column('return_type', sa.String(length=50), nullable=False),
        sa.Column('return_amount', sa.DECIMAL(precision=15, scale=4), nullable=False),
        sa.Column('return_rate', sa.DECIMAL(precision=8, scale=6), nullable=True),
        sa.Column('base_amount', sa.DECIMAL(precision=15, scale=4), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('distribution_method', sa.String(length=50), nullable=True),
        sa.Column('cash_value_change', sa.DECIMAL(precision=15, scale=4), nullable=False, server_default='0'),
        sa.Column('account_value_change', sa.DECIMAL(precision=15, scale=4), nullable=False, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='manual'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_insurance_return_policy_id', 'insurance_returns', ['policy_id'])
    op.create_index('idx_insurance_return_policy_number', 'insurance_returns', ['policy_number'])
    op.create_index('idx_insurance_return_date', 'insurance_returns', ['return_date'])
    op.create_index('idx_insurance_return_type', 'insurance_returns', ['return_type'])
    
    # 创建保险分红历史表
    op.create_table('insurance_dividend_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_code', sa.String(length=50), nullable=False),
        sa.Column('policy_year', sa.Integer(), nullable=False),
        sa.Column('dividend_year', sa.Integer(), nullable=False),
        sa.Column('dividend_rate', sa.DECIMAL(precision=8, scale=6), nullable=True),
        sa.Column('dividend_amount_per_1000', sa.DECIMAL(precision=10, scale=4), nullable=True),
        sa.Column('bonus_rate', sa.DECIMAL(precision=8, scale=6), nullable=True),
        sa.Column('announcement_date', sa.Date(), nullable=True),
        sa.Column('distribution_date', sa.Date(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='company_announcement'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_insurance_dividend_product', 'insurance_dividend_history', ['product_code'])
    op.create_index('idx_insurance_dividend_year', 'insurance_dividend_history', ['dividend_year'])
    op.create_index('idx_insurance_dividend_unique', 'insurance_dividend_history', 
                   ['product_code', 'policy_year', 'dividend_year'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    
    # 删除保险分红历史表
    op.drop_index('idx_insurance_dividend_unique', table_name='insurance_dividend_history')
    op.drop_index('idx_insurance_dividend_year', table_name='insurance_dividend_history')
    op.drop_index('idx_insurance_dividend_product', table_name='insurance_dividend_history')
    op.drop_table('insurance_dividend_history')
    
    # 删除保险收益记录表
    op.drop_index('idx_insurance_return_type', table_name='insurance_returns')
    op.drop_index('idx_insurance_return_date', table_name='insurance_returns')
    op.drop_index('idx_insurance_return_policy_number', table_name='insurance_returns')
    op.drop_index('idx_insurance_return_policy_id', table_name='insurance_returns')
    op.drop_table('insurance_returns')
    
    # 删除保险操作记录表
    op.drop_index('idx_insurance_operation_type', table_name='insurance_operations')
    op.drop_index('idx_insurance_operation_date', table_name='insurance_operations')
    op.drop_index('idx_insurance_operation_policy_number', table_name='insurance_operations')
    op.drop_index('idx_insurance_operation_policy_id', table_name='insurance_operations')
    op.drop_table('insurance_operations')
    
    # 删除保险保单表
    op.drop_index('idx_insurance_policy_start_date', table_name='insurance_policies')
    op.drop_index('idx_insurance_policy_status', table_name='insurance_policies')
    op.drop_index('idx_insurance_policy_company', table_name='insurance_policies')
    op.drop_index('idx_insurance_policy_product_code', table_name='insurance_policies')
    op.drop_index('idx_insurance_policy_number', table_name='insurance_policies')
    op.drop_table('insurance_policies')
    
    # 删除保险产品信息表
    op.drop_index('idx_insurance_product_type', table_name='insurance_products')
    op.drop_index('idx_insurance_product_company', table_name='insurance_products')
    op.drop_index('idx_insurance_product_code', table_name='insurance_products')
    op.drop_table('insurance_products')