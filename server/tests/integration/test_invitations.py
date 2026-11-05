from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from fastapi.testclient import TestClient
from app.main import app
import pytest
from .helpers import auth, invite, login, register
from .conftest import Session
from app.models import Invitation
pytestmark = pytest.mark.integration

def test_invitation_rejection_and_permissions(client):
    c = client
    ta = register(c, 'Орлов Алексей Анатольевич', 'trainer')
    tb = register(c, 'Орлов Борис Анатольевич', 'trainer')
    a = register(c, 'Иванова Мария Андреевна', 'athlete')
    other = register(c, 'Кузнецова Анна Павловна', 'athlete')
    t = login(c, ta)['access_token']
    t2 = login(c, tb)['access_token']
    at = login(c, a)['access_token']
    ot = login(c, other)['access_token']
    first = invite(c, t, a)
    assert c.post(f'/api/v1/invitations/{first}/accept', headers=auth(ot)).status_code == 404
    assert c.post('/api/v1/invitations', json={'athlete_public_id': a}, headers=auth(t)).status_code == 409
    assert c.post(f'/api/v1/invitations/{first}/reject', headers=auth(at)).json()['status'] == 'rejected'
    assert c.get('/api/v1/team/my-trainer', headers=auth(at)).json() is None
    second = invite(c, t, a)
    assert c.get('/api/v1/invitations/incoming', headers=auth(at)).json()[0]['id'] == second
    incoming = c.get('/api/v1/invitations/incoming', headers=auth(at)).json()[0]
    assert incoming['trainer_public_id'] == ta
    assert incoming['athlete_public_id'] == a
    assert 'trainer_id' not in incoming and 'athlete_id' not in incoming
    assert c.post(f'/api/v1/invitations/{second}/accept', headers=auth(at)).status_code == 200
    assert c.post('/api/v1/invitations', json={'athlete_public_id': a}, headers=auth(t2)).status_code == 409
    assert c.delete(f'/api/v1/team/athletes/{a}', headers=auth(t2)).status_code == 404
    assert c.get('/api/v1/athletes', params={'q': 'Иванова'}, headers=auth(t)).json()[0]['public_id'] == a
    assert c.get('/api/v1/athletes', headers=auth(t2)).json() == []
    assert c.post('/api/v1/invitations', json={'athlete_public_id': ta}, headers=auth(t)).status_code == 404

def test_cancel_invitation(client):
    trainer = register(client, 'Смирнов Алексей Сергеевич', 'trainer')
    athlete = register(client, 'Иванова Мария Андреевна', 'athlete')
    token = login(client, trainer)['access_token']
    athlete_token = login(client, athlete)['access_token']
    invitation_id = invite(client, token, athlete)
    assert client.post(f'/api/v1/invitations/{invitation_id}/cancel', headers=auth(token)).json()['status'] == 'cancelled'
    assert client.post(f'/api/v1/invitations/{invitation_id}/accept', headers=auth(athlete_token)).status_code == 409
    assert client.get('/api/v1/team/my-trainer', headers=auth(athlete_token)).json() is None

def test_concurrent_accept(client):
    c = client
    ta = register(c, 'Орлов Алексей Анатольевич', 'trainer')
    tb = register(c, 'Орлов Борис Анатольевич', 'trainer')
    a = register(c, 'Иванова Мария Андреевна', 'athlete')
    t = login(c, ta)['access_token']
    t2 = login(c, tb)['access_token']
    at = login(c, a)['access_token']
    ids = [invite(c, t, a), invite(c, t2, a)]
    barrier = Barrier(2)

    def accept_id(invitation_id):
        with TestClient(app) as independent_client:
            barrier.wait(timeout=10)
            return independent_client.post(f'/api/v1/invitations/{invitation_id}/accept', headers=auth(at)).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(accept_id, ids))
    assert sorted(results) == [200, 409]
    assert c.get('/api/v1/team/my-trainer', headers=auth(at)).json()['public_id'] in [ta, tb]

def test_sent_invitations_and_cancel(client):
    trainer = register(client, 'Смирнов Алексей Сергеевич', 'trainer')
    athlete = register(client, 'Иванова Мария Андреевна', 'athlete')
    token = login(client, trainer)['access_token']
    invitation_id = invite(client, token, athlete)
    sent = client.get('/api/v1/invitations/sent', headers=auth(token))
    assert sent.status_code == 200
    assert sent.json()[0]['id'] == invitation_id
    assert client.post(f'/api/v1/invitations/{invitation_id}/cancel', headers=auth(token)).status_code == 200


def test_clear_only_current_trainer_completed_invitation_history(client):
    trainer_a = register(client, 'Орлов Алексей Анатольевич', 'trainer')
    trainer_b = register(client, 'Орлов Борис Анатольевич', 'trainer')
    accepted_athlete = register(client, 'Иванова Мария Андреевна', 'athlete')
    rejected_athlete = register(client, 'Петрова Анна Сергеевна', 'athlete')
    cancelled_athlete = register(client, 'Сидоров Илья Иванович', 'athlete')
    pending_athlete = register(client, 'Кузнецова Елена Павловна', 'athlete')
    other_athlete = register(client, 'Морозова Ольга Андреевна', 'athlete')
    token_a = login(client, trainer_a)['access_token']
    token_b = login(client, trainer_b)['access_token']
    accepted_token = login(client, accepted_athlete)['access_token']
    rejected_token = login(client, rejected_athlete)['access_token']

    accepted = invite(client, token_a, accepted_athlete)
    rejected = invite(client, token_a, rejected_athlete)
    cancelled = invite(client, token_a, cancelled_athlete)
    pending = invite(client, token_a, pending_athlete)
    other = invite(client, token_b, other_athlete)
    assert client.post(f'/api/v1/invitations/{accepted}/accept', headers=auth(accepted_token)).status_code == 200
    assert client.post(f'/api/v1/invitations/{rejected}/reject', headers=auth(rejected_token)).status_code == 200
    assert client.post(f'/api/v1/invitations/{cancelled}/cancel', headers=auth(token_a)).status_code == 200
    assert client.post(f'/api/v1/invitations/{other}/cancel', headers=auth(token_b)).status_code == 200

    path = '/api/v1/invitations/sent/history'
    assert client.delete(path).status_code == 401
    assert client.delete(path, headers=auth(accepted_token)).status_code == 403
    assert client.delete(path, headers=auth(token_a)).status_code == 204
    assert [item['id'] for item in client.get('/api/v1/invitations/sent', headers=auth(token_a)).json()] == [pending]
    assert client.get('/api/v1/invitations/sent', headers=auth(token_b)).json()[0]['id'] == other
    assert client.get('/api/v1/team/my-trainer', headers=auth(accepted_token)).json()['public_id'] == trainer_a
    assert client.delete(path, headers=auth(token_a)).status_code == 204

    with Session() as db:
        records = {item.id: item for item in db.query(Invitation).all()}
        assert {records[key].status for key in (accepted, rejected, cancelled)} == {'accepted', 'rejected', 'cancelled'}
        assert all(records[key].hidden_from_trainer for key in (accepted, rejected, cancelled))
        assert not records[pending].hidden_from_trainer
        assert not records[other].hidden_from_trainer
