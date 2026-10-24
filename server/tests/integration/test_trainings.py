import pytest
pytestmark = pytest.mark.integration
from .helpers import attach, auth, login, register, week

def test_training_crud_week_and_attendance(client):
    trainer = register(client, 'Тренер', 'trainer')
    athlete = register(client, 'Спортсмен', 'athlete')
    other_trainer = register(client, 'Другой тренер', 'trainer')
    token = login(client, trainer)['access_token']
    athlete_token = login(client, athlete)['access_token']
    other_token = login(client, other_trainer)['access_token']
    attach(client, token, athlete_token, athlete)
    payload = {'athlete_id': athlete, 'date': week(), 'time': '09:00', 'duration_minutes': 45, 'title': 'Бег'}
    created = client.post('/api/v1/trainings', json=payload, headers=auth(token))
    assert created.status_code == 201
    training_id = created.json()['id']
    assert created.json()['attendance'] == 'planned'
    assert client.get('/api/v1/trainings', params={'week_start': week()}, headers=auth(athlete_token)).json()[0]['id'] == training_id
    assert client.get(f'/api/v1/trainings/{training_id}', headers=auth(other_token)).status_code == 404
    assert client.patch(f'/api/v1/trainings/{training_id}', json={'title': 'Темп'}, headers=auth(token)).json()['title'] == 'Темп'
    assert client.patch(f'/api/v1/trainings/{training_id}/attendance', json={'attendance': 'missed'}, headers=auth(token)).json()['attendance'] == 'missed'
    assert client.patch(f'/api/v1/trainings/{training_id}/attendance', json={'attendance': 'attended'}, headers=auth(athlete_token)).status_code == 404
    assert client.delete(f'/api/v1/trainings/{training_id}', headers=auth(token)).status_code == 204
    assert client.get(f'/api/v1/trainings/{training_id}', headers=auth(athlete_token)).status_code == 404
