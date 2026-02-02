"""
Pytest configuration
"""
import pytest
from HrmsBackend.database import SessionLocal, engine
from HrmsBackend.models import Base


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
