from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base

class Injury(Base):
    __tablename__ = 'injuries'
    id: Mapped[int] = mapped_column(primary_key=True)
    athlete_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    title: Mapped[str] = mapped_column(String(200))
    date: Mapped[date] = mapped_column(Date)
    note: Mapped[str] = mapped_column(Text, default='')
    severity: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    __table_args__ = (
        CheckConstraint("severity in ('mild','moderate','severe')", name='injury_severity'),
        CheckConstraint("status in ('active','healed')", name='injury_status'),
    )
