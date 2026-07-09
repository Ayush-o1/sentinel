"""
SENTINEL Backend — Test Configuration & Fixtures

Provides shared fixtures for all tests:
- test_db: In-memory SQLite async session (per-function — isolated state)
- client: AsyncClient with the test database injected and rate limiting disabled
- test_user: A pre-created User fixture
- ml_model: Session-scoped ML model (loaded ONCE per test session, not per test)
"""

import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
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


@pytest_asyncio.fixture(scope="session")
async def ml_model():
    """
    Load the ML model ONCE per test session, not per test function.

    Loading the joblib model takes ~1-2 seconds. Scoping this to 'session'
    avoids reloading it for every test, cutting total test suite time
    from O(n * 2s) to a fixed 2s overhead.
    """
    from app.ml.model import MLModel
    model = MLModel()
    await model.load()
    return model


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a fresh SQLite engine for each test function (clean state)."""
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
async def client(test_db: AsyncSession, ml_model) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an AsyncClient with the test database injected.

    - The real database session is overridden with the test session.
    - The ML model is reused from the session-scoped fixture (no reload per test).
    - Rate limiting is disabled to prevent 429s in fast-running tests.
    """
    app = create_application()
    app.state.limiter.enabled = False

    # Reuse the session-scoped ML model — don't reload per test
    app.state.ml_model = ml_model

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


# ---------------------------------------------------------------------------
# Shared helper — get auth headers for a test user
# ---------------------------------------------------------------------------

async def get_auth_headers(client: AsyncClient, email: str, password: str) -> dict[str, str]:
    """Register (if needed) and login to get a Bearer token."""
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test User",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password,
    })
    token = resp.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}
