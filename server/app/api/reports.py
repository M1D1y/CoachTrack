from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.dependencies import current_user
from ..db.session import get_db
from ..models import User
from ..schemas.report import Summary
from ..services import reports as report_service

router = APIRouter()


@router.get('/reports/summary', response_model=Summary, tags=['reports'])
def summary(week_start: date | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return report_service.user_summary(db, user, week_start)


@router.get('/athletes/{athlete_id}/reports/summary', response_model=Summary, tags=['reports'])
def athlete_summary(
    athlete_id: int, week_start: date | None = None,
    user: User = Depends(current_user), db: Session = Depends(get_db),
):
    return report_service.athlete_summary(db, user, athlete_id, week_start)
