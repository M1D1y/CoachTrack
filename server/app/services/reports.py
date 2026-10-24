from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.dependencies import athlete_access
from ..models import Training, User


def normalized_week(value: date | None) -> date:
    value = value or date.today()
    if value.weekday() != 0:
        raise HTTPException(422, 'week_start должен быть понедельником')
    return value


def current_or_requested_week(value: date | None) -> date:
    if value is None:
        today = date.today()
        value = today - timedelta(days=today.weekday())
    return normalized_week(value)


def attendance_percent(attended: int, missed: int) -> float:
    completed = attended + missed
    return round(attended / completed * 100, 2) if completed else 0


def week_summary(db: Session, athlete_ids: list[int], week: date, athlete_count: int | None = None) -> dict:
    counts = {'planned': 0, 'attended': 0, 'missed': 0}
    if athlete_ids:
        rows = db.execute(
            select(Training.attendance, func.count(Training.id))
            .where(
                Training.athlete_id.in_(athlete_ids),
                Training.date >= week,
                Training.date < week + timedelta(days=7),
            )
            .group_by(Training.attendance)
        ).all()
        counts.update(rows)
    return {
        'week_start': week,
        'athlete_count': athlete_count,
        'training_count': sum(counts.values()),
        'attended': counts['attended'],
        'missed': counts['missed'],
        'attendance_percent': attendance_percent(counts['attended'], counts['missed']),
    }


def user_summary(db: Session, user: User, week_start: date | None = None) -> dict:
    week = current_or_requested_week(week_start)
    if user.role == 'athlete':
        return week_summary(db, [user.id], week)
    athlete_ids = db.scalars(select(User.id).where(User.trainer_id == user.id)).all()
    return week_summary(db, athlete_ids, week, len(athlete_ids))


def athlete_summary(db: Session, user: User, athlete_id: int, week_start: date | None = None) -> dict:
    athlete_access(db, user, athlete_id)
    return week_summary(db, [athlete_id], current_or_requested_week(week_start))
