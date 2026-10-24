from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..core.dependencies import current_user
from ..db.session import get_db
from ..models import User
from ..schemas.user import UserOut
from ..services.team import detach_athlete, get_trainer

router = APIRouter()


@router.get('/team/my-trainer', response_model=UserOut | None, tags=['team'])
def my_trainer(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return get_trainer(db, user)


@router.delete('/team/my-trainer', status_code=204, tags=['team'])
def leave_team(user: User = Depends(current_user), db: Session = Depends(get_db)):
    detach_athlete(db, user)
    return Response(status_code=204)


@router.delete('/team/athletes/{athlete_id}', status_code=204, tags=['team'])
def remove_athlete(athlete_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    detach_athlete(db, user, athlete_id)
    return Response(status_code=204)
