from datetime import date, timedelta


def week():
    return (date.today() - timedelta(days=date.today().weekday())).isoformat()


def auth(token):
    return {'Authorization': f'Bearer {token}'}


def register(client, name, role):
    response = client.post('/api/v1/auth/register', json={
        'name': name, 'password': 'StrongPassword123!', 'role': role,
    })
    assert response.status_code == 201, response.text
    assert 'password_hash' not in response.json()
    return response.json()['id']


def login(client, user_id):
    response = client.post('/api/v1/auth/login', json={
        'id': user_id, 'password': 'StrongPassword123!',
    })
    assert response.status_code == 200, response.text
    return response.json()


def invite(client, trainer_token, athlete_id):
    response = client.post('/api/v1/invitations', json={'athlete_id': athlete_id}, headers=auth(trainer_token))
    assert response.status_code == 201, response.text
    return response.json()['id']


def attach(client, trainer_token, athlete_token, athlete_id):
    invitation_id = invite(client, trainer_token, athlete_id)
    response = client.post(f'/api/v1/invitations/{invitation_id}/accept', headers=auth(athlete_token))
    assert response.status_code == 200, response.text
