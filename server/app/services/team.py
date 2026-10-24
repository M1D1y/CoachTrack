from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.dependencies import require_role
from ..models import User


def detach_athlete(db: Session, user: User, athlete_id: int | None = None) -> None:
    if athlete_id is None:
        require_role(user, 'athlete')
        athlete_id = user.id
    else:
        require_role(user, 'trainer')
    athlete = db.scalar(
        select(User).where(User.id == athlete_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if (
        not athlete
        or athlete.role != 'athlete'
        or (user.role == 'trainer' and athlete.trainer_id != user.id)
    ):
        raise HTTPException(404, 'Спортсмен не найден в команде')
    athlete.trainer_id = None
    db.commit()


def get_trainer(db: Session, athlete: User) -> User | None:
    require_role(athlete, 'athlete')
    return db.get(User, athlete.trainer_id) if athlete.trainer_id else None
