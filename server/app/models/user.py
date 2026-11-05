from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Uuid, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

def now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), default=uuid4, server_default=text('gen_random_uuid()'), nullable=False)
    name: Mapped[str] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    age: Mapped[int | None] = mapped_column(Integer)
    sport: Mapped[str | None] = mapped_column(String(100))
    trainer_id: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    trainer: Mapped['User | None'] = relationship(remote_side='User.id', foreign_keys=[trainer_id])
    __table_args__ = (
        UniqueConstraint('public_id', name='uq_users_public_id'),
        CheckConstraint("role in ('trainer','athlete')", name='user_role'),
        CheckConstraint("role = 'athlete' OR trainer_id IS NULL", name='trainer_no_trainer'),
    )


def normalized_name_sql(value=None):
    source = User.name if value is None else value
    collapsed = func.btrim(func.regexp_replace(source, '[[:space:]]+', ' ', 'g'))
    return func.translate(
        func.lower(collapsed),
        'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ',
        'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
    )


Index('uq_users_name_normalized', normalized_name_sql(), unique=True)
