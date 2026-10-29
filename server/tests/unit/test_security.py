from datetime import datetime, timedelta, timezone

import jwt
from argon2.exceptions import VerifyMismatchError
import pytest

from app.core.config import settings
from app.core.security import access_token, digest, generate_refresh_token, hash_password, hasher, verify_password
from app.models import User

pytestmark = pytest.mark.unit


def test_argon2_password_hashing(strong_password):
    encoded = hash_password(strong_password)
    assert encoded.startswith('$argon2')
    assert encoded != strong_password
    assert hasher.verify(encoded, strong_password)
    assert verify_password(encoded, strong_password)
    assert not verify_password(encoded, 'incorrect-password')
    with pytest.raises(VerifyMismatchError):
        hasher.verify(encoded, 'incorrect-password')


def test_access_jwt_contains_user_and_expiry():
    user = User(id=15, name='Иванова Мария Андреевна', role='athlete', password_hash='unused')
    token = access_token(user)
    claims = jwt.decode(token, settings().jwt_secret_key, algorithms=['HS256'])
    assert claims['sub'] == '15'
    assert claims['type'] == 'access'
    assert datetime.fromtimestamp(claims['exp'], timezone.utc) > datetime.now(timezone.utc)
    assert datetime.fromtimestamp(claims['exp'], timezone.utc) <= datetime.now(timezone.utc) + timedelta(minutes=settings().access_token_expire_minutes)


def test_refresh_digest_is_deterministic_and_not_raw():
    token = 'private-refresh-token'
    assert len(digest(token)) == 64
    assert digest(token) == digest(token)
    assert digest(token) != digest(token + 'x')
    assert token not in digest(token)


def test_refresh_token_is_random():
    first = generate_refresh_token()
    second = generate_refresh_token()
    assert first != second
    assert len(first) >= 48


def test_expired_access_token_is_rejected():
    from app.core.security import decode_access_token

    expired = jwt.encode(
        {'sub': '15', 'type': 'access', 'exp': datetime.now(timezone.utc) - timedelta(seconds=1)},
        settings().jwt_secret_key,
        algorithm='HS256',
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired)


def test_placeholder_secret_is_rejected():
    from pydantic import ValidationError
    from app.core.config import Settings

    with pytest.raises(ValidationError):
        Settings(jwt_secret_key='replace_with_a_long_random_secret_at_least_32_characters')
