from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..core.dependencies import current_user
from ..db.session import get_db
from ..models import User
from ..schemas.injury import InjuryCreate, InjuryOut, InjuryUpdate
from ..services import injuries as injury_service

router = APIRouter()


@router.get('/athletes/{athlete_id}/injuries', response_model=list[InjuryOut], tags=['injuries'])
def list_injuries(athlete_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return injury_service.list_injuries(db, user, athlete_id)


@router.post('/athletes/{athlete_id}/injuries', response_model=InjuryOut, status_code=201, tags=['injuries'])
def create_injury(athlete_id: int, body: InjuryCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return injury_service.create_injury(db, user, athlete_id, body)


@router.patch('/injuries/{injury_id}', response_model=InjuryOut, tags=['injuries'])
def update_injury(injury_id: int, body: InjuryUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return injury_service.update_injury(db, user, injury_id, body)


@router.delete('/injuries/{injury_id}', status_code=204, tags=['injuries'])
def delete_injury(injury_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    injury_service.delete_injury(db, user, injury_id)
    return Response(status_code=204)
