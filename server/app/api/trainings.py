from datetime import date

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..core.dependencies import current_user
from ..db.session import get_db
from ..models import User
from ..schemas.training import AttendanceUpdate, TrainingCreate, TrainingOut, TrainingUpdate
from ..services import trainings as training_service

router = APIRouter()


@router.get('/trainings', response_model=list[TrainingOut], tags=['trainings'])
def list_trainings(week_start: date | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return training_service.list_trainings(db, user, week_start)


@router.get('/trainings/{training_id}', response_model=TrainingOut, tags=['trainings'])
def training_detail(training_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return training_service.get_training(db, user, training_id)


@router.post('/trainings', response_model=TrainingOut, status_code=201, tags=['trainings'])
def create_training(body: TrainingCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return training_service.create_training(db, user, body)


@router.patch('/trainings/{training_id}', response_model=TrainingOut, tags=['trainings'])
def update_training(training_id: int, body: TrainingUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return training_service.update_training(db, user, training_id, body)


@router.delete('/trainings/{training_id}', status_code=204, tags=['trainings'])
def delete_training(training_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    training_service.delete_training(db, user, training_id)
    return Response(status_code=204)


@router.patch('/trainings/{training_id}/attendance', response_model=TrainingOut, tags=['trainings'])
def attendance(training_id: int, body: AttendanceUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return training_service.set_attendance(db, user, training_id, body)
