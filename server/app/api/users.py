from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.dependencies import current_user
from ..db.session import get_db
from ..models import User
from ..schemas.user import UserOut, UserUpdate
from ..services.auth import update_profile

router = APIRouter()


@router.get('/users/me', response_model=UserOut, tags=['users'])
def me(user: User = Depends(current_user)):
    return user


@router.patch('/users/me', response_model=UserOut, tags=['users'])
def update_me(body: UserUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return update_profile(db, user, body)
