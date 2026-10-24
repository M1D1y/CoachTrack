import pytest
from .helpers import auth, login, register, attach
pytestmark = pytest.mark.integration

def test_search_by_id_and_name(client):
    trainer = register(client, 'Алексей Смирнов', 'trainer')
    athlete = register(client, 'Мария Иванова', 'athlete')
    token = login(client, trainer)['access_token']
    for query in [str(athlete), 'мария', 'иванова', 'Мария Иванова']:
        result = client.get('/api/v1/athletes/search', params={'q': query}, headers=auth(token)).json()
        assert result[0]['id'] == athlete
        assert set(result[0]) == {'id', 'name', 'sport', 'relationship_status'}
    assert client.get('/api/v1/athletes/search', params={'q': 'Несуществующий'}, headers=auth(token)).json() == []
    assert client.get('/api/v1/athletes/search', params={'q': ' '}, headers=auth(token)).status_code == 422

def test_team_list_is_scoped_to_trainer(client):
    trainer_a = register(client, 'Тренер А', 'trainer')
    trainer_b = register(client, 'Тренер Б', 'trainer')
    athlete = register(client, 'Мария Иванова', 'athlete')
    token_a = login(client, trainer_a)['access_token']
    token_b = login(client, trainer_b)['access_token']
    athlete_token = login(client, athlete)['access_token']
    assert client.get('/api/v1/athletes', headers=auth(token_a)).json() == []
    attach(client, token_a, athlete_token, athlete)
    assert client.get('/api/v1/athletes', params={'q': 'Иванова'}, headers=auth(token_a)).json()[0]['id'] == athlete
    assert client.get('/api/v1/athletes', headers=auth(token_b)).json() == []
    result = client.get('/api/v1/athletes/search', params={'q': str(athlete)}, headers=auth(token_b)).json()[0]
    assert result['relationship_status'] == 'unavailable'
    assert 'password_hash' not in result
