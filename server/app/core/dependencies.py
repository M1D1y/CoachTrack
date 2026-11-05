import jwt
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..db.session import get_db
from ..models import User
from .security import decode_access_token

bearer = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(401, 'Требуется авторизация')
    try:
        public_id = decode_access_token(credentials.credentials)
    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(401, 'Недействительный токен') from None
    user = db.scalar(select(User).where(User.public_id == public_id))
    if user is None:
        raise HTTPException(401, 'Недействительный токен')
    return user


def require_role(user: User, role: str) -> None:
    if user.role != role:
        raise HTTPException(403, 'Недостаточно прав')


def athlete_access(db: Session, user: User, athlete_id: int, write: bool = False) -> User:
    athlete = db.get(User, athlete_id)
    if not athlete or athlete.role != 'athlete':
        raise HTTPException(404, 'Спортсмен не найден')
    if user.role == 'trainer' and athlete.trainer_id == user.id:
        return athlete
    if not write and user.role == 'athlete' and user.id == athlete_id:
        return athlete
    raise HTTPException(404, 'Спортсмен не найден')


def athlete_by_public_id(db: Session, public_id: UUID) -> User:
    athlete = db.scalar(select(User).where(User.public_id == public_id, User.role == 'athlete'))
    if not athlete:
        raise HTTPException(404, 'Спортсмен не найден')
    return athlete
