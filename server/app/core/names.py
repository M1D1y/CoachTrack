import re

MAX_NAME_PART_LENGTH = 60
_NAME_PART = re.compile(r'[^\W\d_]+(?:-[^\W\d_]+)*\Z', re.UNICODE)


def normalize_name(value: str) -> str:
    """Collapse whitespace without changing the spelling or capitalization."""
    return ' '.join(value.split())


def name_key(value: str) -> str:
    return normalize_name(value).lower()


def validate_name_part(value: str) -> str:
    part = value.strip()
    if not part:
        raise ValueError('Часть ФИО не может быть пустой')
    if len(part) > MAX_NAME_PART_LENGTH:
        raise ValueError(f'Часть ФИО не может быть длиннее {MAX_NAME_PART_LENGTH} символов')
    if not _NAME_PART.fullmatch(part):
        raise ValueError('Используйте буквы и, при необходимости, дефис')
    return part


def full_name(last_name: str, first_name: str, patronymic: str) -> str:
    return ' '.join(validate_name_part(part) for part in (last_name, first_name, patronymic))


def validate_full_name(value: str) -> str:
    parts = normalize_name(value).split(' ')
    if len(parts) != 3:
        raise ValueError('Укажите фамилию, имя и отчество')
    return full_name(*parts)
