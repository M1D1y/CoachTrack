import os
import pytest

os.environ.setdefault('JWT_SECRET_KEY', 'test-only-random-secret-for-isolated-database')


@pytest.fixture
def strong_password():
    return 'StrongPassword123!'
