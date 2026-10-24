import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher, exceptions

from .config import settings
from ..models import User

hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return hasher.verify(password_hash, password)
    except exceptions.VerificationError:
        return False


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def access_token(user: User) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings().access_token_expire_minutes)
    return jwt.encode(
        {'sub': str(user.id), 'exp': expires_at, 'type': 'access'},
        settings().jwt_secret_key,
        algorithm='HS256',
    )


def decode_access_token(token: str) -> int:
    payload = jwt.decode(token, settings().jwt_secret_key, algorithms=['HS256'])
    if payload.get('type') != 'access':
        raise ValueError('Invalid token type')
    return int(payload['sub'])
