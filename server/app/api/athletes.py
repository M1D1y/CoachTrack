from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.dependencies import current_user
from ..db.session import get_db
from ..models import User
from ..schemas.athlete import SearchUser
from ..schemas.user import UserOut
from ..services.athletes import list_team, search_registered

router = APIRouter()


@router.get('/athletes/search', response_model=list[SearchUser], tags=['athletes'])
def search_athletes(
    q: str = Query(min_length=1, max_length=100),
    user: User = Depends(current_user), db: Session = Depends(get_db),
):
    return search_registered(db, user, q)


@router.get('/athletes', response_model=list[UserOut], tags=['athletes'])
def athletes(q: str = Query('', max_length=100), user: User = Depends(current_user), db: Session = Depends(get_db)):
    return list_team(db, user, q)
