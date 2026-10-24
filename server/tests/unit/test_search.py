import pytest
from sqlalchemy.dialects import postgresql

from app.services.athletes import prepare_search, search_clause

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(('query', 'expected'), [
    (' 15 ', (15, ())),
    ('Мария', (None, ('Мария',))),
    ('Иванова', (None, ('Иванова',))),
    (' Мария   Иванова ', (None, ('Мария', 'Иванова'))),
    ('Иванова Мария', (None, ('Иванова', 'Мария'))),
    ('²', (None, ('²',))),
])
def test_prepare_search(query, expected):
    assert prepare_search(query) == expected


def test_numeric_id_uses_exact_match():
    compiled = search_clause('15').compile(dialect=postgresql.dialect())
    assert 'users.id =' in str(compiled)
    assert list(compiled.params.values()) == [15]


def test_text_search_uses_case_insensitive_terms():
    compiled = search_clause('мАрИя ИВАНОВА').compile(dialect=postgresql.dialect())
    assert str(compiled).count('ILIKE') == 2
    assert set(compiled.params.values()) == {'%мАрИя%', '%ИВАНОВА%'}


def test_like_metacharacters_are_escaped():
    compiled = search_clause(r'A%_\B').compile(dialect=postgresql.dialect())
    value = next(iter(compiled.params.values()))
    assert '\\%' in value
    assert '\\_' in value
    assert '\\\\' in value
