"""
SENTINEL — Async Database Session Management

Creates the async SQLAlchemy engine and session factory.
All database I/O in the application uses async sessions from this module.

Architecture:
    - One engine per process (connection pool shared across requests)
    - One session per request (managed by the get_db dependency)
    - Sessions are NEVER created outside of dependency injection
"""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# pool_pre_ping=True: Verify connections are alive before use.
#                     Handles stale connections after PostgreSQL restarts.
# pool_size: Number of persistent connections to keep open.
# max_overflow: Additional connections allowed beyond pool_size under load.
# echo: Log all SQL statements in development for debugging.
# ---------------------------------------------------------------------------
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.is_development,  # SQL logging in dev only
)

# ---------------------------------------------------------------------------
# Session Factory
# ---------------------------------------------------------------------------
# expire_on_commit=False: Keep ORM objects usable after commit.
#                          Without this, accessing attributes after commit
#                          triggers a lazy load — which fails in async context.
# ---------------------------------------------------------------------------
AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
