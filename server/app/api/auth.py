from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..core.dependencies import current_user
from ..db.session import get_db
from ..models import User
from ..schemas.auth import Login, RefreshIn, Register, TokenPair
from ..schemas.user import UserOut
from ..services import auth as auth_service

router = APIRouter()


@router.post('/auth/register', response_model=UserOut, status_code=201, tags=['auth'])
def register(body: Register, db: Session = Depends(get_db)):
    return auth_service.register(db, body)


@router.post('/auth/login', response_model=TokenPair, tags=['auth'])
def login(body: Login, db: Session = Depends(get_db)):
    return auth_service.login(db, body.name, body.password)


@router.post('/auth/refresh', response_model=TokenPair, tags=['auth'])
def refresh(body: RefreshIn, db: Session = Depends(get_db)):
    return auth_service.refresh(db, body.refresh_token)


@router.post('/auth/logout', status_code=204, tags=['auth'])
def logout(body: RefreshIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    auth_service.logout(db, user, body.refresh_token)
    return Response(status_code=204)
