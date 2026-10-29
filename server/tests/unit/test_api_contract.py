import pytest

from app.db.base import Base
from app.main import app
from app import models  # Ensure all SQLAlchemy tables are registered.
from app.models import User

pytestmark = pytest.mark.unit


EXPECTED_ROUTES = {
    ('GET', '/api/v1/athletes'),
    ('GET', '/api/v1/athletes/search'),
    ('GET', '/api/v1/athletes/{athlete_id}/injuries'),
    ('POST', '/api/v1/athletes/{athlete_id}/injuries'),
    ('GET', '/api/v1/athletes/{athlete_id}/nutrition'),
    ('POST', '/api/v1/athletes/{athlete_id}/nutrition'),
    ('GET', '/api/v1/athletes/{athlete_id}/reports/summary'),
    ('POST', '/api/v1/auth/login'),
    ('POST', '/api/v1/auth/logout'),
    ('POST', '/api/v1/auth/refresh'),
    ('POST', '/api/v1/auth/register'),
    ('DELETE', '/api/v1/injuries/{injury_id}'),
    ('PATCH', '/api/v1/injuries/{injury_id}'),
    ('POST', '/api/v1/invitations'),
    ('GET', '/api/v1/invitations/incoming'),
    ('GET', '/api/v1/invitations/sent'),
    ('POST', '/api/v1/invitations/{invitation_id}/accept'),
    ('POST', '/api/v1/invitations/{invitation_id}/cancel'),
    ('POST', '/api/v1/invitations/{invitation_id}/reject'),
    ('DELETE', '/api/v1/nutrition/{nutrition_id}'),
    ('PATCH', '/api/v1/nutrition/{nutrition_id}'),
    ('GET', '/api/v1/reports/summary'),
    ('DELETE', '/api/v1/team/athletes/{athlete_id}'),
    ('DELETE', '/api/v1/team/my-trainer'),
    ('GET', '/api/v1/team/my-trainer'),
    ('GET', '/api/v1/trainings'),
    ('POST', '/api/v1/trainings'),
    ('DELETE', '/api/v1/trainings/{training_id}'),
    ('GET', '/api/v1/trainings/{training_id}'),
    ('PATCH', '/api/v1/trainings/{training_id}'),
    ('PATCH', '/api/v1/trainings/{training_id}/attendance'),
    ('GET', '/api/v1/users/me'),
    ('PATCH', '/api/v1/users/me'),
}


def test_openapi_routes_are_preserved():
    actual = {(method, path) for path, methods in app.openapi()['paths'].items() for method in methods if method.upper() in {'GET', 'POST', 'PATCH', 'DELETE'}}
    assert actual == EXPECTED_ROUTES


def test_alembic_metadata_sees_all_tables():
    assert set(Base.metadata.tables) == {'users', 'invitations', 'refresh_tokens', 'trainings', 'injuries', 'nutrition'}
    assert 'uq_users_name_normalized' in {index.name for index in User.__table__.indexes}
