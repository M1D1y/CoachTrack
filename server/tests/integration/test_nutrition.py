import pytest

from .helpers import attach, auth, login, register, week

pytestmark = pytest.mark.integration


def test_nutrition_crud_and_permissions(client):
    trainer = register(client, 'Смирнов Алексей Сергеевич', 'trainer')
    athlete = register(client, 'Иванова Мария Андреевна', 'athlete')
    outsider = register(client, 'Соколова Анна Сергеевна', 'athlete')
    trainer_token = login(client, trainer)['access_token']
    athlete_token = login(client, athlete)['access_token']
    outsider_token = login(client, outsider)['access_token']
    attach(client, trainer_token, athlete_token, athlete)
    created = client.post(f'/api/v1/athletes/{athlete}/nutrition', json={
        'date': week(), 'title': 'Обед', 'note': 'Рис',
    }, headers=auth(trainer_token))
    assert created.status_code == 201
    nutrition_id = created.json()['id']
    assert client.get(f'/api/v1/athletes/{athlete}/nutrition', headers=auth(athlete_token)).json()[0]['id'] == nutrition_id
    assert client.get(f'/api/v1/athletes/{athlete}/nutrition', headers=auth(outsider_token)).status_code == 404
    assert client.patch(f'/api/v1/nutrition/{nutrition_id}', json={'note': 'Гречка'}, headers=auth(athlete_token)).status_code == 404
    assert client.patch(f'/api/v1/nutrition/{nutrition_id}', json={'note': 'Гречка'}, headers=auth(trainer_token)).json()['note'] == 'Гречка'
    assert client.delete(f'/api/v1/nutrition/{nutrition_id}', headers=auth(trainer_token)).status_code == 204
    assert client.get(f'/api/v1/athletes/{athlete}/nutrition', headers=auth(athlete_token)).json() == []
