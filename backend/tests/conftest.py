import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.config import settings
from app.db.base import Base
from app.containers import Container

# Use a test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(name="test_engine")
async def test_engine_fixture():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(name="test_session")
async def test_session_fixture(test_engine):
    TestSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession
    )
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture(name="override_get_db")
def override_get_db_fixture(test_session):
    async def _override_get_db():
        yield test_session
    return _override_get_db

@pytest.fixture(name="client")
async def client_fixture(override_get_db):
    # Override the database dependency with the test session
    app.container.db.override(override_get_db)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.container.db.reset_override()
