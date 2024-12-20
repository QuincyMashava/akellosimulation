"""Add workstreams and targets tables

Revision ID: 7d7d383f3617
Revises: b3524483f416
Create Date: 2024-11-30 01:00:27.875908

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d7d383f3617'
down_revision = 'b3524483f416'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('targets_report',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('target', sa.String(length=255), nullable=False),
    sa.Column('target_completion_date', sa.String(length=50), nullable=True),
    sa.Column('employee_name', sa.String(length=100), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('targets_report', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_targets_report_timestamp'), ['timestamp'], unique=False)

    op.create_table('workstreams_report',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('workstream', sa.String(length=255), nullable=False),
    sa.Column('progress', sa.String(length=50), nullable=True),
    sa.Column('quantity', sa.String(length=50), nullable=True),
    sa.Column('target_completion_date', sa.String(length=50), nullable=True),
    sa.Column('comments', sa.Text(), nullable=True),
    sa.Column('employee_name', sa.String(length=100), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('workstreams_report', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_workstreams_report_timestamp'), ['timestamp'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('workstreams_report', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_workstreams_report_timestamp'))

    op.drop_table('workstreams_report')
    with op.batch_alter_table('targets_report', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_targets_report_timestamp'))

    op.drop_table('targets_report')
    # ### end Alembic commands ###
