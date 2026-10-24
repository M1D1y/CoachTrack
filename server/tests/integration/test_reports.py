import pytest

from .helpers import attach, auth, login, register, week

pytestmark = pytest.mark.integration


def test_aggregates_from_postgresql(client):
    trainer = register(client, 'Тренер', 'trainer')
    athlete = register(client, 'Спортсмен', 'athlete')
    other = register(client, 'Без тренера', 'athlete')
    trainer_token = login(client, trainer)['access_token']
    athlete_token = login(client, athlete)['access_token']
    other_token = login(client, other)['access_token']
    attach(client, trainer_token, athlete_token, athlete)
    for status in ('attended', 'missed', 'planned'):
        created = client.post('/api/v1/trainings', json={
            'athlete_id': athlete, 'date': week(), 'time': '09:00',
            'duration_minutes': 30, 'title': status,
        }, headers=auth(trainer_token))
        assert created.status_code == 201
        client.patch(f"/api/v1/trainings/{created.json()['id']}/attendance", json={'attendance': status}, headers=auth(trainer_token))
    trainer_result = client.get('/api/v1/reports/summary', params={'week_start': week()}, headers=auth(trainer_token)).json()
    assert trainer_result['athlete_count'] == 1
    assert trainer_result['training_count'] == 3
    assert trainer_result['attended'] == 1
    assert trainer_result['missed'] == 1
    assert trainer_result['attendance_percent'] == 50
    athlete_result = client.get(f'/api/v1/athletes/{athlete}/reports/summary', params={'week_start': week()}, headers=auth(athlete_token)).json()
    assert athlete_result['training_count'] == 3
    assert athlete_result['attendance_percent'] == 50
    assert client.get('/api/v1/reports/summary', params={'week_start': week()}, headers=auth(other_token)).json()['training_count'] == 0
    assert client.get(f'/api/v1/athletes/{athlete}/reports/summary', headers=auth(other_token)).status_code == 404
