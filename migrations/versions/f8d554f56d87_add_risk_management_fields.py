"""Add risk management fields

Revision ID: f8d554f56d87
Revises: 10ff2958bc1e
Create Date: 2025-05-14 01:31:01.444185

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8d554f56d87'
down_revision = '10ff2958bc1e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trades', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_size', sa.Float(), nullable=True, comment='交易时的账户总资金'))
        batch_op.add_column(sa.Column('risk_percentage', sa.Float(), nullable=True, comment='风险占账户百分比'))
        batch_op.add_column(sa.Column('position_size', sa.Float(), nullable=True, comment='仓位大小'))
        batch_op.add_column(sa.Column('r_multiple', sa.Float(), nullable=True, comment='R倍数(盈亏与初始风险的比值)'))
        batch_op.add_column(sa.Column('initial_risk', sa.Float(), nullable=True, comment='初始风险金额'))
        batch_op.add_column(sa.Column('plan_vs_execution', sa.Integer(), nullable=True, comment='计划执行一致性评分(1-10)'))
        batch_op.add_column(sa.Column('trade_quality', sa.Integer(), nullable=True, comment='交易质量评分(1-10)'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trades', schema=None) as batch_op:
        batch_op.drop_column('trade_quality')
        batch_op.drop_column('plan_vs_execution')
        batch_op.drop_column('initial_risk')
        batch_op.drop_column('r_multiple')
        batch_op.drop_column('position_size')
        batch_op.drop_column('risk_percentage')
        batch_op.drop_column('account_size')

    # ### end Alembic commands ###
