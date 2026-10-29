from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.security import access_token, digest, generate_refresh_token, hash_password, verify_password
from ..models import RefreshToken, User
from ..models.user import normalized_name_sql
from ..schemas.auth import Register, TokenPair
from ..schemas.user import UserUpdate

NAME_UNIQUE_INDEX = 'uq_users_name_normalized'
NAME_CONFLICT = 'Пользователь с таким ФИО уже зарегистрирован'


def _ensure_unique_name(db: Session, name: str, except_user_id: int | None = None) -> None:
    statement = select(User.id).where(normalized_name_sql() == normalized_name_sql(name))
    if except_user_id is not None:
        statement = statement.where(User.id != except_user_id)
    if db.scalar(statement) is not None:
        raise HTTPException(status_code=409, detail=NAME_CONFLICT)


def _commit_name_change(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        constraint = getattr(getattr(exc.orig, 'diag', None), 'constraint_name', None)
        if constraint == NAME_UNIQUE_INDEX:
            raise HTTPException(status_code=409, detail=NAME_CONFLICT) from exc
        raise


def register(db: Session, body: Register) -> User:
    name = body.full_name
    _ensure_unique_name(db, name)
    user = User(name=name, password_hash=hash_password(body.password), role=body.role)
    db.add(user)
    _commit_name_change(db)
    db.refresh(user)
    return user


def _new_refresh(db: Session, user: User) -> str:
    raw = generate_refresh_token()
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=digest(raw),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings().refresh_token_expire_days),
    ))
    return raw


def login(db: Session, name: str, password: str) -> TokenPair:
    user = db.scalar(select(User).where(normalized_name_sql() == normalized_name_sql(name)))
    if not user or not verify_password(user.password_hash, password):
        raise HTTPException(401, 'Неверное ФИО или пароль')
    refresh = _new_refresh(db, user)
    db.commit()
    return TokenPair(access_token=access_token(user), refresh_token=refresh)


def refresh(db: Session, raw: str) -> TokenPair:
    token = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == digest(raw)).with_for_update())
    if not token or token.revoked_at or token.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(401, 'Недействительный refresh token')
    user = db.get(User, token.user_id)
    token.revoked_at = datetime.now(timezone.utc)
    fresh = _new_refresh(db, user)
    db.commit()
    return TokenPair(access_token=access_token(user), refresh_token=fresh)


def logout(db: Session, user: User, raw: str) -> None:
    token = db.scalar(select(RefreshToken).where(
        RefreshToken.token_hash == digest(raw),
        RefreshToken.user_id == user.id,
    ).with_for_update())
    if token:
        token.revoked_at = datetime.now(timezone.utc)
        db.commit()


def update_profile(db: Session, user: User, body: UserUpdate) -> User:
    changes = body.model_dump(exclude_unset=True)
    if 'name' in changes:
        name = changes['name']
        if name is None:
            raise HTTPException(422, 'Укажите фамилию, имя и отчество')
        _ensure_unique_name(db, name, except_user_id=user.id)
    for key, value in changes.items():
        setattr(user, key, value)
    _commit_name_change(db)
    db.refresh(user)
    return user
