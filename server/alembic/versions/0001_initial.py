"""Initial CoachTrack schema.

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('age', sa.Integer()),
        sa.Column('sport', sa.String(100)),
        sa.Column('trainer_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role in ('trainer','athlete')", name='user_role'),
        sa.CheckConstraint("role = 'athlete' OR trainer_id IS NULL", name='trainer_no_trainer'),
    )
    op.create_index('ix_users_trainer_id', 'users', ['trainer_id'])
    op.create_table('invitations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('trainer_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('athlete_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('responded_at', sa.DateTime(timezone=True)),
        sa.CheckConstraint("status in ('pending','accepted','rejected','cancelled')", name='invitation_status'),
    )
    op.create_index('ix_invitations_trainer_id', 'invitations', ['trainer_id'])
    op.create_index('ix_invitations_athlete_id', 'invitations', ['athlete_id'])
    op.create_index('uq_pending_invitation', 'invitations', ['trainer_id', 'athlete_id'], unique=True, postgresql_where=sa.text("status = 'pending'"))
    op.create_table('trainings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('athlete_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('time', sa.Time(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('attendance', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('duration_minutes > 0', name='training_duration'),
        sa.CheckConstraint("attendance in ('planned','attended','missed')", name='training_attendance'),
    )
    op.create_index('ix_trainings_athlete_id', 'trainings', ['athlete_id'])
    op.create_index('ix_trainings_date', 'trainings', ['date'])
    op.create_table('injuries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('athlete_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('note', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.CheckConstraint("severity in ('mild','moderate','severe')", name='injury_severity'),
        sa.CheckConstraint("status in ('active','healed')", name='injury_status'),
    )
    op.create_index('ix_injuries_athlete_id', 'injuries', ['athlete_id'])
    op.create_table('nutrition',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('athlete_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('note', sa.Text(), nullable=False),
    )
    op.create_index('ix_nutrition_athlete_id', 'nutrition', ['athlete_id'])
    op.create_table('refresh_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])

def downgrade():
    op.drop_table('refresh_tokens')
    op.drop_table('nutrition')
    op.drop_table('injuries')
    op.drop_table('trainings')
    op.drop_table('invitations')
    op.drop_table('users')
