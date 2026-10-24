from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.dependencies import athlete_access
from ..models import Nutrition, User
from ..schemas.nutrition import NutritionCreate, NutritionUpdate


def list_nutrition(db: Session, user: User, athlete_id: int) -> list[Nutrition]:
    athlete_access(db, user, athlete_id)
    statement = (
        select(Nutrition).where(Nutrition.athlete_id == athlete_id)
        .order_by(Nutrition.date.desc(), Nutrition.id.desc())
    )
    return db.scalars(statement).all()


def create_nutrition(db: Session, user: User, athlete_id: int, body: NutritionCreate) -> Nutrition:
    athlete_access(db, user, athlete_id, write=True)
    item = Nutrition(athlete_id=athlete_id, **body.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_nutrition(db: Session, user: User, nutrition_id: int) -> Nutrition:
    item = db.get(Nutrition, nutrition_id)
    if not item:
        raise HTTPException(404, 'Запись не найдена')
    athlete_access(db, user, item.athlete_id, write=True)
    return item


def update_nutrition(db: Session, user: User, nutrition_id: int, body: NutritionUpdate) -> Nutrition:
    item = get_nutrition(db, user, nutrition_id)
    changes = body.model_dump(exclude_unset=True)
    if any(value is None for value in changes.values()):
        raise HTTPException(422, 'Поля питания не могут быть пустыми')
    for key, value in changes.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_nutrition(db: Session, user: User, nutrition_id: int) -> None:
    item = get_nutrition(db, user, nutrition_id)
    db.delete(item)
    db.commit()
