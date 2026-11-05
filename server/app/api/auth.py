from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.dependencies import current_user
from ..db.session import get_db
from ..models import User
from ..schemas.auth import AccessOut, Login, Register
from ..schemas.user import UserOut
from ..services import auth as auth_service

router = APIRouter()
COOKIE_NAME = 'coachtrack_refresh'
COOKIE_PATH = '/api/v1/auth'


def check_origin(request: Request) -> None:
    allowed = {item.strip() for item in settings().cors_origins.split(',')}
    allowed.add('http://localhost:8000')
    if request.headers.get('origin') not in allowed:
        raise HTTPException(403, 'Недопустимый источник запроса')


def set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        COOKIE_NAME, token, httponly=True, secure=settings().refresh_cookie_secure, samesite='strict',
        path=COOKIE_PATH, max_age=settings().refresh_token_expire_days * 86400,
    )


@router.post('/auth/register', response_model=UserOut, status_code=201, tags=['auth'])
def register(body: Register, db: Session = Depends(get_db)):
    return auth_service.register(db, body)


@router.post('/auth/login', response_model=AccessOut, tags=['auth'])
def login(body: Login, response: Response, db: Session = Depends(get_db), _: None = Depends(check_origin)):
    tokens = auth_service.login(db, body.name, body.password)
    set_refresh_cookie(response, tokens.refresh_token)
    return AccessOut(access_token=tokens.access_token)


@router.post('/auth/refresh', response_model=AccessOut, tags=['auth'])
def refresh(response: Response, raw: str | None = Cookie(None, alias=COOKIE_NAME),
            db: Session = Depends(get_db), _: None = Depends(check_origin)):
    if not raw:
        raise HTTPException(401, 'Нет действующей сессии')
    tokens = auth_service.refresh(db, raw)
    set_refresh_cookie(response, tokens.refresh_token)
    return AccessOut(access_token=tokens.access_token)


@router.post('/auth/logout', status_code=204, tags=['auth'])
def logout(response: Response, user: User = Depends(current_user),
           raw: str | None = Cookie(None, alias=COOKIE_NAME),
           db: Session = Depends(get_db), _: None = Depends(check_origin)):
    if raw:
        auth_service.logout(db, user, raw)
    response.delete_cookie(COOKIE_NAME, path=COOKIE_PATH, samesite='strict')
    response.status_code = 204
