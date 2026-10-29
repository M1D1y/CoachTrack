import pytest

from app.core.names import full_name, name_key, normalize_name, validate_full_name, validate_name_part
from app.schemas.auth import Login, Register
from app.schemas.user import UserUpdate

pytestmark = pytest.mark.unit


def test_full_name_trims_parts_and_keeps_spelling():
    body = Register(
        last_name='  Соколова  ', first_name=' Мария ', patronymic=' Андреевна ',
        password='StrongPassword123!', role='athlete',
    )
    assert body.full_name == 'Соколова Мария Андреевна'
    assert full_name('Соколова', 'Мария', 'Андреевна') == body.full_name


def test_normalized_login_ignores_case_and_extra_spaces():
    assert name_key('  сОкОлОвА   МАРИЯ  андреевна ') == name_key('Соколова Мария Андреевна')
    assert Login(name='  Соколова   Мария Андреевна ', password='x').name == 'Соколова Мария Андреевна'
    assert normalize_name('  Иванов   Иван  ') == 'Иванов Иван'


@pytest.mark.parametrize('value', [' ', 'Мария Иванова', 'Имя1', 'Имя_', 'А' * 61])
def test_invalid_part_is_rejected(value):
    with pytest.raises(ValueError):
        validate_name_part(value)


def test_hyphen_and_yo_are_allowed():
    assert validate_full_name('Ёлкина Анна-Мария Петровна') == 'Ёлкина Анна-Мария Петровна'
    assert validate_name_part('  Семёнов-Петров  ') == 'Семёнов-Петров'


def test_profile_name_requires_three_parts():
    with pytest.raises(ValueError):
        validate_full_name('Соколова Мария')
    assert UserUpdate(name='  Соколова   Мария Андреевна ').name == 'Соколова Мария Андреевна'


def test_legacy_login_name_can_have_two_parts():
    assert Login(name='Старый Пользователь', password='x').name == 'Старый Пользователь'
