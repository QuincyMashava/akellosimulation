"""empty message

Revision ID: ea5fb6d569db
Revises: 
Create Date: 2024-11-25 02:56:58.062722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea5fb6d569db'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('firstname', sa.String(length=120), nullable=False),
    sa.Column('lastname', sa.String(length=120), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('department', sa.String(length=120), nullable=False),
    sa.Column('role', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_department'), ['department'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_firstname'), ['firstname'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_lastname'), ['lastname'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_role'), ['role'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_role'))
        batch_op.drop_index(batch_op.f('ix_user_lastname'))
        batch_op.drop_index(batch_op.f('ix_user_firstname'))
        batch_op.drop_index(batch_op.f('ix_user_email'))
        batch_op.drop_index(batch_op.f('ix_user_department'))

    op.drop_table('user')
    # ### end Alembic commands ###
