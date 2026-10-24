import pytest

pytestmark = pytest.mark.integration

from .helpers import auth, login, register


def test_register_login_refresh_logout(client):
    trainer = register(client, 'Алексей Смирнов', 'trainer')
    athlete = register(client, 'Мария Иванова', 'athlete')
    assert trainer != athlete
    assert client.post('/api/v1/auth/login', json={'id': trainer, 'password': 'wrong'}).status_code == 401
    trainer_tokens = login(client, trainer)
    athlete_tokens = login(client, athlete)
    trainer_auth = auth(trainer_tokens['access_token'])
    athlete_auth = auth(athlete_tokens['access_token'])
    assert client.get('/api/v1/users/me', headers=trainer_auth).json()['role'] == 'trainer'
    assert client.get('/api/v1/users/me', headers=athlete_auth).json()['role'] == 'athlete'
    assert client.get('/api/v1/team/my-trainer', headers=athlete_auth).json() is None
    assert client.get('/api/v1/trainings', headers=athlete_auth).json() == []
    assert client.get('/api/v1/users/me').status_code == 401
    assert client.get('/api/v1/users/me', headers=auth('not-a-jwt')).status_code == 401
    assert client.patch('/api/v1/users/me', json={'name': 'Новая Мария'}, headers=athlete_auth).json()['name'] == 'Новая Мария'
    rotated = client.post('/api/v1/auth/refresh', json={'refresh_token': trainer_tokens['refresh_token']}).json()
    assert rotated['refresh_token'] != trainer_tokens['refresh_token']
    assert client.post('/api/v1/auth/refresh', json={'refresh_token': trainer_tokens['refresh_token']}).status_code == 401
    assert client.post('/api/v1/auth/logout', json={'refresh_token': rotated['refresh_token']}, headers=auth(rotated['access_token'])).status_code == 204
    assert client.post('/api/v1/auth/refresh', json={'refresh_token': rotated['refresh_token']}).status_code == 401
