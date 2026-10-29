from datetime import date, timedelta

registered_names: dict[int, str] = {}

def week():
    return (date.today() - timedelta(days=date.today().weekday())).isoformat()


def auth(token):
    return {'Authorization': f'Bearer {token}'}


def register(client, name, role):
    last_name, first_name, patronymic = name.split()
    response = client.post('/api/v1/auth/register', json={
        'last_name': last_name, 'first_name': first_name,
        'patronymic': patronymic, 'password': 'StrongPassword123!', 'role': role,
    })
    assert response.status_code == 201, response.text
    assert 'password_hash' not in response.json()
    user_id = response.json()['id']
    assert response.json()['name'] == name
    registered_names[user_id] = name
    return user_id


def login(client, user_id):
    response = client.post('/api/v1/auth/login', json={
        'name': registered_names[user_id], 'password': 'StrongPassword123!',
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
