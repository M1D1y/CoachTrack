from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .user import User

from ..db.base import Base
from .user import now

class Invitation(Base):
    __tablename__ = 'invitations'
    id: Mapped[int] = mapped_column(primary_key=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    athlete_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    status: Mapped[str] = mapped_column(String(20), default='pending')
    hidden_from_trainer: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text('false'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    trainer: Mapped[User] = relationship(foreign_keys=[trainer_id])
    athlete: Mapped[User] = relationship(foreign_keys=[athlete_id])

    @property
    def trainer_public_id(self):
        return self.trainer.public_id

    @property
    def athlete_public_id(self):
        return self.athlete.public_id

    @property
    def trainer_name(self):
        return self.trainer.name

    @property
    def athlete_name(self):
        return self.athlete.name
    __table_args__ = (
        CheckConstraint("status in ('pending','accepted','rejected','cancelled')", name='invitation_status'),
        Index(
            'uq_pending_invitation', 'trainer_id', 'athlete_id', unique=True,
            postgresql_where=text("status = 'pending'"),
        ),
    )
