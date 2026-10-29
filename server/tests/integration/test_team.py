import pytest
from .helpers import attach, auth, invite, login, register, week
pytestmark = pytest.mark.integration

def test_full_lifecycle_and_crud(client):
    c = client
    ta = register(c, 'Орлов Алексей Анатольевич', 'trainer')
    tb = register(c, 'Орлов Борис Анатольевич', 'trainer')
    a = register(c, 'Иванова Мария Андреевна', 'athlete')
    other = register(c, 'Петров Илья Сергеевич', 'athlete')
    t = login(c, ta)['access_token']
    t2 = login(c, tb)['access_token']
    at = login(c, a)['access_token']
    ot = login(c, other)['access_token']
    attach(c, t, at, a)
    w = week()
    training = c.post('/api/v1/trainings', json={'athlete_id': a, 'date': w, 'time': '09:00', 'duration_minutes': 45, 'title': 'Бег', 'description': 'Легко'}, headers=auth(t))
    assert training.status_code == 201, training.text
    tid = training.json()['id']
    assert c.patch(f'/api/v1/trainings/{tid}', json={'title': 'Темповый бег'}, headers=auth(t)).json()['title'] == 'Темповый бег'
    assert c.patch(f'/api/v1/trainings/{tid}/attendance', json={'attendance': 'attended'}, headers=auth(t)).status_code == 200
    assert c.patch(f'/api/v1/trainings/{tid}/attendance', json={'attendance': 'missed'}, headers=auth(at)).status_code == 404
    assert c.get('/api/v1/trainings', params={'week_start': w}, headers=auth(at)).json()[0]['attendance'] == 'attended'
    assert c.get(f'/api/v1/trainings/{tid}', headers=auth(ot)).status_code == 404
    injury = c.post(f'/api/v1/athletes/{a}/injuries', json={'date': w, 'title': 'Колено', 'severity': 'mild', 'note': 'Отдых'}, headers=auth(t))
    assert injury.status_code == 201
    iid = injury.json()['id']
    assert c.patch(f'/api/v1/injuries/{iid}', json={'status': 'healed'}, headers=auth(t)).json()['status'] == 'healed'
    nutrition = c.post(f'/api/v1/athletes/{a}/nutrition', json={'date': w, 'title': 'Обед', 'note': 'Рис'}, headers=auth(t))
    assert nutrition.status_code == 201
    nid = nutrition.json()['id']
    assert c.patch(f'/api/v1/nutrition/{nid}', json={'note': 'Гречка'}, headers=auth(t)).json()['note'] == 'Гречка'
    assert c.get(f'/api/v1/athletes/{a}/injuries', headers=auth(at)).status_code == 200
    assert c.get(f'/api/v1/athletes/{a}/nutrition', headers=auth(at)).status_code == 200
    assert c.get(f'/api/v1/athletes/{a}/injuries', headers=auth(ot)).status_code == 404
    assert c.get(f'/api/v1/athletes/{a}/nutrition', headers=auth(ot)).status_code == 404
    assert c.get('/api/v1/reports/summary', params={'week_start': w}, headers=auth(t)).json()['attendance_percent'] == 100
    assert c.get(f'/api/v1/athletes/{a}/reports/summary', params={'week_start': w}, headers=auth(at)).json()['training_count'] == 1
    assert c.delete(f'/api/v1/team/athletes/{a}', headers=auth(t)).status_code == 204
    assert c.delete(f'/api/v1/team/athletes/{a}', headers=auth(t)).status_code == 404
    assert c.get('/api/v1/athletes', headers=auth(t)).json() == []
    assert c.get('/api/v1/users/me', headers=auth(at)).json()['trainer_id'] is None
    assert c.get('/api/v1/trainings', headers=auth(at)).json()[0]['id'] == tid
    assert c.get(f'/api/v1/athletes/{a}/injuries', headers=auth(at)).json()[0]['id'] == iid
    assert c.get(f'/api/v1/athletes/{a}/nutrition', headers=auth(at)).json()[0]['id'] == nid
    assert c.get(f'/api/v1/trainings/{tid}', headers=auth(t)).status_code == 404
    assert c.get(f'/api/v1/athletes/{a}/injuries', headers=auth(t)).status_code == 404
    assert c.get(f'/api/v1/athletes/{a}/nutrition', headers=auth(t)).status_code == 404
    assert c.patch(f'/api/v1/trainings/{tid}', json={'title': 'Чужое'}, headers=auth(t)).status_code == 404
    assert login(c, a)['access_token']
    attach(c, t2, at, a)
    assert c.get('/api/v1/team/my-trainer', headers=auth(at)).json()['id'] == tb
    assert c.delete(f'/api/v1/trainings/{tid}', headers=auth(t2)).status_code == 204
    assert c.delete(f'/api/v1/injuries/{iid}', headers=auth(t2)).status_code == 204
    assert c.delete(f'/api/v1/nutrition/{nid}', headers=auth(t2)).status_code == 204
    assert c.delete('/api/v1/team/my-trainer', headers=auth(at)).status_code == 204
