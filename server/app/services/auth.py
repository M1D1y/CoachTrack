from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.security import access_token, digest, generate_refresh_token, hash_password, verify_password
from ..models import RefreshToken, User
from ..schemas.auth import TokenPair
from ..schemas.user import UserUpdate


def register(db: Session, name: str, password: str, role: str) -> User:
    name = name.strip()
    if not name:
        raise HTTPException(422, 'Имя не может быть пустым')
    user = User(name=name, password_hash=hash_password(password), role=role)
    db.add(user)
    db.commit()
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


def login(db: Session, user_id: int, password: str) -> TokenPair:
    user = db.get(User, user_id)
    if not user or not verify_password(user.password_hash, password):
        raise HTTPException(401, 'Неверный ID или пароль')
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
        if name is None or not name.strip():
            raise HTTPException(422, 'Имя не может быть пустым')
        changes['name'] = name.strip()
    for key, value in changes.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
