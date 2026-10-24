from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.dependencies import athlete_access
from ..models import Injury, User
from ..schemas.injury import InjuryCreate, InjuryUpdate


def list_injuries(db: Session, user: User, athlete_id: int) -> list[Injury]:
    athlete_access(db, user, athlete_id)
    return db.scalars(select(Injury).where(Injury.athlete_id == athlete_id).order_by(Injury.date.desc(), Injury.id.desc())).all()


def create_injury(db: Session, user: User, athlete_id: int, body: InjuryCreate) -> Injury:
    athlete_access(db, user, athlete_id, write=True)
    item = Injury(athlete_id=athlete_id, **body.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_injury(db: Session, user: User, injury_id: int) -> Injury:
    item = db.get(Injury, injury_id)
    if not item:
        raise HTTPException(404, 'Запись не найдена')
    athlete_access(db, user, item.athlete_id, write=True)
    return item


def update_injury(db: Session, user: User, injury_id: int, body: InjuryUpdate) -> Injury:
    item = get_injury(db, user, injury_id)
    changes = body.model_dump(exclude_unset=True)
    if any(value is None for value in changes.values()):
        raise HTTPException(422, 'Поля травмы не могут быть пустыми')
    for key, value in changes.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_injury(db: Session, user: User, injury_id: int) -> None:
    item = get_injury(db, user, injury_id)
    db.delete(item)
    db.commit()
