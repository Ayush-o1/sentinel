"""
SENTINEL Backend — Test Configuration & Fixtures

Provides shared fixtures for all tests:
- test_db: In-memory SQLite async session
- client: TestClient with auth bypassed
- test_user: A pre-created User fixture
"""

import asyncio
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.dependencies import get_db
from app.core.security import hash_password
from app.main import create_application
from app.models.base import Base
from app.models.user import User

# Use an in-memory SQLite database for tests
# aiosqlite driver supports async SQLAlchemy with SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Use a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a fresh SQLite engine for each test function."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session."""
    TestSessionFactory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with TestSessionFactory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an AsyncClient with the test database injected.

    The real database session is overridden with the test session
    via FastAPI's dependency override mechanism.
    """
    app = create_application()

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def test_user(test_db: AsyncSession) -> User:
    """Create and return a test user."""
    user = User(
        id=uuid.uuid4(),
        email="test@sentinel.dev",
        full_name="Test User",
        hashed_password=hash_password("TestPass1!"),
        role="user",
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user
