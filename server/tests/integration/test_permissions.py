import pytest

from .helpers import attach, auth, invite, login, register, week

pytestmark = pytest.mark.integration


def test_cross_team_and_cross_athlete_access(client):
    trainer_a = register(client, 'Тренер А', 'trainer')
    trainer_b = register(client, 'Тренер Б', 'trainer')
    athlete_a = register(client, 'Спортсмен А', 'athlete')
    athlete_b = register(client, 'Спортсмен Б', 'athlete')
    token_a = login(client, trainer_a)['access_token']
    token_b = login(client, trainer_b)['access_token']
    athlete_token_a = login(client, athlete_a)['access_token']
    athlete_token_b = login(client, athlete_b)['access_token']
    attach(client, token_a, athlete_token_a, athlete_a)
    attach(client, token_b, athlete_token_b, athlete_b)
    payload = {'athlete_id': athlete_a, 'date': week(), 'time': '09:00', 'duration_minutes': 30, 'title': 'Бег'}
    training = client.post('/api/v1/trainings', json=payload, headers=auth(token_a))
    training_id = training.json()['id']
    assert client.post('/api/v1/trainings', json=payload, headers=auth(athlete_token_a)).status_code == 403
    assert client.post('/api/v1/trainings', json=payload, headers=auth(token_b)).status_code == 404
    assert client.get(f'/api/v1/trainings/{training_id}', headers=auth(token_b)).status_code == 404
    assert client.get(f'/api/v1/trainings/{training_id}', headers=auth(athlete_token_b)).status_code == 404
    assert client.patch(f'/api/v1/trainings/{training_id}/attendance', json={'attendance': 'attended'}, headers=auth(athlete_token_a)).status_code == 404
    assert client.delete(f'/api/v1/team/athletes/{athlete_a}', headers=auth(token_b)).status_code == 404
    assert client.get(f'/api/v1/athletes/{athlete_a}/nutrition', headers=auth(athlete_token_b)).status_code == 404
    assert client.get(f'/api/v1/athletes/{athlete_a}/injuries', headers=auth(token_b)).status_code == 404
    assert client.get(f'/api/v1/athletes/{athlete_a}/reports/summary', headers=auth(token_b)).status_code == 404
    assert client.delete(f'/api/v1/team/athletes/{athlete_a}', headers=auth(token_a)).status_code == 204
    assert client.get(f'/api/v1/trainings/{training_id}', headers=auth(token_a)).status_code == 404


def test_other_athlete_cannot_accept_invitation(client):
    trainer = register(client, 'Тренер', 'trainer')
    athlete = register(client, 'Спортсмен', 'athlete')
    other = register(client, 'Другой', 'athlete')
    trainer_token = login(client, trainer)['access_token']
    other_token = login(client, other)['access_token']
    invitation_id = invite(client, trainer_token, athlete)
    assert client.post(f'/api/v1/invitations/{invitation_id}/accept', headers=auth(other_token)).status_code == 404
