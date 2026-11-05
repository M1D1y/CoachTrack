import uuid
import pytest

from app.core.security import access_token, decode_access_token
from app.models import User
from app.schemas.user import UserOut

pytestmark = pytest.mark.unit


def test_jwt_subject_uses_public_uuid():
    user = User(id=12, public_id=uuid.uuid4(), role='athlete')
    assert decode_access_token(access_token(user)) == user.public_id


def test_user_response_has_no_internal_id():
    fields = UserOut.model_fields
    assert 'public_id' in fields
    assert 'id' not in fields
    assert 'trainer_id' not in fields


def test_old_numeric_jwt_subject_is_rejected():
    import jwt
    from datetime import datetime, timedelta, timezone
    from app.core.config import settings

    token = jwt.encode({
        'sub': '12', 'type': 'access',
        'exp': datetime.now(timezone.utc) + timedelta(minutes=1),
    }, settings().jwt_secret_key, algorithm='HS256')
    with pytest.raises(ValueError):
        decode_access_token(token)
