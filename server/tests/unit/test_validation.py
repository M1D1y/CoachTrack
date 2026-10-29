import pytest
from pydantic import ValidationError

from app.schemas.auth import Register
from app.schemas.injury import InjuryCreate
from app.schemas.training import AttendanceUpdate, TrainingCreate

pytestmark = pytest.mark.unit


@pytest.mark.parametrize('field', ['last_name', 'first_name', 'patronymic'])
@pytest.mark.parametrize('value', ['', '   ', 'Мария1', 'Мария Иванова', 'А' * 61])
def test_registration_rejects_invalid_name_part(field, value):
    data = {'last_name': 'Соколова', 'first_name': 'Мария', 'patronymic': 'Андреевна'}
    data[field] = value
    with pytest.raises(ValidationError):
        Register(**data, password='StrongPassword123!', role='athlete')


def test_registration_rejects_short_password():
    with pytest.raises(ValidationError):
        Register(last_name='Соколова', first_name='Мария', patronymic='Андреевна', password='short', role='athlete')


def test_registration_rejects_unknown_role():
    with pytest.raises(ValidationError):
        Register(last_name='Соколова', first_name='Мария', patronymic='Андреевна', password='StrongPassword123!', role='admin')


def test_training_rejects_negative_duration():
    with pytest.raises(ValidationError):
        TrainingCreate(athlete_id=1, date='2026-10-19', time='09:00', duration_minutes=-5, title='Бег')


def test_attendance_rejects_unknown_status():
    with pytest.raises(ValidationError):
        AttendanceUpdate(attendance='cancelled')


def test_injury_rejects_unknown_severity():
    with pytest.raises(ValidationError):
        InjuryCreate(title='Колено', date='2026-10-19', severity='critical')
