from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.dependencies import athlete_access, require_role
from ..models import Training, User
from ..schemas.training import AttendanceUpdate, TrainingCreate, TrainingUpdate
from .reports import normalized_week


def list_trainings(db: Session, user: User, week_start: date | None = None) -> list[Training]:
    statement = select(Training)
    if user.role == 'athlete':
        statement = statement.where(Training.athlete_id == user.id)
    else:
        statement = statement.join(User, User.id == Training.athlete_id).where(User.trainer_id == user.id)
    if week_start:
        week = normalized_week(week_start)
        statement = statement.where(Training.date >= week, Training.date < week + timedelta(days=7))
    return db.scalars(statement.order_by(Training.date, Training.time, Training.id)).all()


def get_training(db: Session, user: User, training_id: int, write: bool = False) -> Training:
    item = db.get(Training, training_id)
    if not item:
        raise HTTPException(404, 'Тренировка не найдена')
    athlete_access(db, user, item.athlete_id, write=write)
    return item


def create_training(db: Session, user: User, body: TrainingCreate) -> Training:
    require_role(user, 'trainer')
    athlete_access(db, user, body.athlete_id, write=True)
    item = Training(**body.model_dump(), attendance='planned')
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_training(db: Session, user: User, training_id: int, body: TrainingUpdate) -> Training:
    item = get_training(db, user, training_id, write=True)
    changes = body.model_dump(exclude_unset=True)
    if any(value is None for value in changes.values()):
        raise HTTPException(422, 'Поля тренировки не могут быть пустыми')
    for key, value in changes.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_training(db: Session, user: User, training_id: int) -> None:
    item = get_training(db, user, training_id, write=True)
    db.delete(item)
    db.commit()


def set_attendance(db: Session, user: User, training_id: int, body: AttendanceUpdate) -> Training:
    item = get_training(db, user, training_id, write=True)
    item.attendance = body.attendance
    db.commit()
    db.refresh(item)
    return item
