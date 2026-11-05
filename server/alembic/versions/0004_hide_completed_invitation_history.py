"""Allow trainers to hide completed invitations without deleting history.

Revision ID: 0004
Revises: 0003
"""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'invitations',
        sa.Column('hidden_from_trainer', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    )


def downgrade():
    op.drop_column('invitations', 'hidden_from_trainer')
