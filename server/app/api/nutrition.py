from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..core.dependencies import current_user
from ..db.session import get_db
from ..models import User
from ..schemas.nutrition import NutritionCreate, NutritionOut, NutritionUpdate
from ..services import nutrition as nutrition_service

router = APIRouter()


@router.get('/athletes/{athlete_id}/nutrition', response_model=list[NutritionOut], tags=['nutrition'])
def list_nutrition(athlete_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return nutrition_service.list_nutrition(db, user, athlete_id)


@router.post('/athletes/{athlete_id}/nutrition', response_model=NutritionOut, status_code=201, tags=['nutrition'])
def create_nutrition(athlete_id: int, body: NutritionCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return nutrition_service.create_nutrition(db, user, athlete_id, body)


@router.patch('/nutrition/{nutrition_id}', response_model=NutritionOut, tags=['nutrition'])
def update_nutrition(nutrition_id: int, body: NutritionUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return nutrition_service.update_nutrition(db, user, nutrition_id, body)


@router.delete('/nutrition/{nutrition_id}', status_code=204, tags=['nutrition'])
def delete_nutrition(nutrition_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    nutrition_service.delete_nutrition(db, user, nutrition_id)
    return Response(status_code=204)
