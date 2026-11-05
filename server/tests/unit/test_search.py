import pytest
from sqlalchemy.dialects import postgresql

from app.services.athletes import prepare_search, search_clause

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(('query', 'expected'), [
    (' 15 ', (None, ())),
    ('Мария', (None, ('Мария',))),
    ('Иванова', (None, ('Иванова',))),
    (' Мария   Иванова ', (None, ('Мария', 'Иванова'))),
    ('Иванова Мария', (None, ('Иванова', 'Мария'))),
    ('  Соколова  Мария   Андреевна  ', (None, ('Соколова', 'Мария', 'Андреевна'))),
    ('²', (None, ('²',))),
])
def test_prepare_search(query, expected):
    assert prepare_search(query) == expected


def test_numeric_id_is_not_searchable():
    compiled = search_clause('15').compile(dialect=postgresql.dialect())
    assert 'false' in str(compiled).lower()


def test_text_search_uses_case_insensitive_terms():
    compiled = search_clause('мАрИя ИВАНОВА').compile(dialect=postgresql.dialect())
    assert str(compiled).count('LIKE') == 2
    assert {'%мария%', '%иванова%'} <= set(compiled.params.values())


def test_patronymic_search_is_case_insensitive():
    compiled = search_clause('Андреевна').compile(dialect=postgresql.dialect())
    assert 'LIKE' in str(compiled)
    assert '%андреевна%' in compiled.params.values()


def test_like_metacharacters_are_escaped():
    compiled = search_clause(r'A%_\B').compile(dialect=postgresql.dialect())
    value = next(value for value in compiled.params.values() if '%' in value and 'a' in value)
    assert '\\%' in value
    assert '\\_' in value
    assert '\\\\' in value
