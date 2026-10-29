from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import jwt
import pytest

from app.core.config import settings
from app.core.security import hash_password
from app.models import User
from app.services import auth as auth_service
from .conftest import Session

pytestmark = pytest.mark.integration

from .helpers import auth, login, register


def test_register_login_refresh_logout(client):
    trainer = register(client, 'Смирнов Алексей Сергеевич', 'trainer')
    athlete = register(client, 'Иванова Мария Андреевна', 'athlete')
    assert trainer != athlete
    assert client.post('/api/v1/auth/login', json={
        'name': 'Смирнов Алексей Сергеевич', 'password': 'wrong',
    }).status_code == 401
    assert client.post('/api/v1/auth/login', json={
        'name': 'Несуществующий Иван Иванович', 'password': 'StrongPassword123!',
    }).status_code == 401
    trainer_tokens = login(client, trainer)
    athlete_tokens = login(client, athlete)
    claims = jwt.decode(trainer_tokens['access_token'], settings().jwt_secret_key, algorithms=['HS256'])
    assert claims['sub'] == str(trainer)
    trainer_auth = auth(trainer_tokens['access_token'])
    athlete_auth = auth(athlete_tokens['access_token'])
    assert client.get('/api/v1/users/me', headers=trainer_auth).json()['role'] == 'trainer'
    assert client.get('/api/v1/users/me', headers=athlete_auth).json()['role'] == 'athlete'
    assert client.get('/api/v1/team/my-trainer', headers=athlete_auth).json() is None
    assert client.get('/api/v1/trainings', headers=athlete_auth).json() == []
    assert client.get('/api/v1/users/me').status_code == 401
    assert client.get('/api/v1/users/me', headers=auth('not-a-jwt')).status_code == 401
    assert client.patch('/api/v1/users/me', json={
        'name': '  Иванова   Мария Владимировна ',
    }, headers=athlete_auth).json()['name'] == 'Иванова Мария Владимировна'
    assert client.post('/api/v1/auth/login', json={
        'name': 'Иванова Мария Владимировна', 'password': 'StrongPassword123!',
    }).status_code == 200
    assert client.post('/api/v1/auth/login', json={
        'name': 'Иванова Мария Андреевна', 'password': 'StrongPassword123!',
    }).status_code == 401
    rotated = client.post('/api/v1/auth/refresh', json={'refresh_token': trainer_tokens['refresh_token']}).json()
    assert rotated['refresh_token'] != trainer_tokens['refresh_token']
    assert client.post('/api/v1/auth/refresh', json={'refresh_token': trainer_tokens['refresh_token']}).status_code == 401
    assert client.post('/api/v1/auth/logout', json={'refresh_token': rotated['refresh_token']}, headers=auth(rotated['access_token'])).status_code == 204
    assert client.post('/api/v1/auth/refresh', json={'refresh_token': rotated['refresh_token']}).status_code == 401


def test_login_normalizes_fio_and_duplicate_registration_is_rejected(client):
    user_id = register(client, 'Соколова Мария Андреевна', 'athlete')
    response = client.post('/api/v1/auth/login', json={
        'name': '  сОкОлОвА    МАРИЯ   андреевна ', 'password': 'StrongPassword123!',
    })
    assert response.status_code == 200
    token = response.json()['access_token']
    assert client.get('/api/v1/users/me', headers=auth(token)).json()['id'] == user_id

    duplicate = client.post('/api/v1/auth/register', json={
        'last_name': 'соколова', 'first_name': 'МАРИЯ', 'patronymic': 'андреевна',
        'password': 'StrongPassword123!', 'role': 'trainer',
    })
    assert duplicate.status_code == 409
    assert duplicate.json()['detail'] == 'Пользователь с таким ФИО уже зарегистрирован'
    assert client.post('/api/v1/auth/register', json={
        'last_name': 'Соколова', 'first_name': 'Мария',
        'password': 'StrongPassword123!', 'role': 'athlete',
    }).status_code == 422


def test_profile_name_must_be_complete_and_unique(client):
    first = register(client, 'Соколова Мария Андреевна', 'athlete')
    second = register(client, 'Иванова Анна Павловна', 'athlete')
    token = login(client, second)['access_token']
    headers = auth(token)
    assert client.patch('/api/v1/users/me', json={'name': 'Иванова Анна'}, headers=headers).status_code == 422
    duplicate = client.patch('/api/v1/users/me', json={
        'name': '  СОКОЛОВА   мария Андреевна ',
    }, headers=headers)
    assert duplicate.status_code == 409
    assert client.get('/api/v1/users/me', headers=headers).json()['id'] == second
    assert first != second


def test_existing_two_part_name_can_login_until_profile_update(client):
    with Session() as db:
        user = User(name='Старый Пользователь', role='athlete', password_hash=hash_password('StrongPassword123!'))
        db.add(user)
        db.commit()
        user_id = user.id

    response = client.post('/api/v1/auth/login', json={
        'name': '  старый   пользователь ', 'password': 'StrongPassword123!',
    })
    assert response.status_code == 200
    headers = auth(response.json()['access_token'])
    assert client.get('/api/v1/users/me', headers=headers).json()['id'] == user_id
    updated = client.patch('/api/v1/users/me', json={
        'name': 'Старый Пользователь Иванович',
    }, headers=headers)
    assert updated.status_code == 200
    assert client.post('/api/v1/auth/login', json={
        'name': 'Старый Пользователь', 'password': 'StrongPassword123!',
    }).status_code == 401


def test_concurrent_registration_returns_conflict(client, monkeypatch):
    barrier = Barrier(2)
    original_hash = auth_service.hash_password

    def synchronized_hash(password: str) -> str:
        # Both requests pass the precheck before either inserts a user.
        barrier.wait(timeout=10)
        return original_hash(password)

    monkeypatch.setattr(auth_service, 'hash_password', synchronized_hash)
    body = {
        'last_name': 'Ёлкина', 'first_name': 'Анна-Мария',
        'patronymic': 'Павловна', 'password': 'StrongPassword123!', 'role': 'athlete',
    }

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: client.post('/api/v1/auth/register', json=body), range(2)))
    assert sorted(response.status_code for response in responses) == [201, 409]
    assert next(response for response in responses if response.status_code == 409).json()['detail'] == (
        'Пользователь с таким ФИО уже зарегистрирован'
    )
