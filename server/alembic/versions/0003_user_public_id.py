"""Add stable random public identifiers without changing internal foreign keys.

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('public_id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False))
    op.create_unique_constraint('uq_users_public_id', 'users', ['public_id'])


def downgrade():
    op.drop_constraint('uq_users_public_id', 'users', type_='unique')
    op.drop_column('users', 'public_id')
