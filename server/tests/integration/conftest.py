import os
from pathlib import Path
from urllib.parse import urlparse

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

url = os.environ.get('TEST_DATABASE_URL')
if not url or urlparse(url).scheme != 'postgresql+psycopg' or not urlparse(url).path.endswith('_test') or url == os.environ.get('DATABASE_URL'):
    pytest.skip('Set TEST_DATABASE_URL to a dedicated PostgreSQL database ending in _test', allow_module_level=True)
os.environ['DATABASE_URL'] = url

from app.core.config import settings
settings.cache_clear()
if settings().database_url != url:
    raise RuntimeError('Integration tests are not bound to TEST_DATABASE_URL')

from app.db.base import Base
from app.db import session as app_session
from app.db.session import get_db
from app import models  # Register all tables in Base.metadata.
from app.main import app

engine = create_engine(url, pool_pre_ping=True)
# Any route that bypasses the override must still use the isolated test database.
app_session.SessionLocal.configure(bind=engine)
app_session.engine = engine
Session = sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope='session', autouse=True)
def schema():
    config = Config(str(Path(__file__).resolve().parents[2] / 'alembic.ini'))
    command.upgrade(config, 'head')
    yield
    command.downgrade(config, 'base')


@pytest.fixture(autouse=True)
def clean(schema):
    names = ', '.join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
    with engine.begin() as conn:
        conn.execute(text(f'TRUNCATE {names} RESTART IDENTITY CASCADE'))


@pytest.fixture
def client():
    def db_override():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = db_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
