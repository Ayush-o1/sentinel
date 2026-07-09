"""
SENTINEL Backend — Application Entry Point

This module is the FastAPI application factory.
It wires together all routers, middleware, exception handlers,
and application lifespan events (startup/shutdown).

Architecture note:
    The `create_application` factory pattern is used instead of a
    module-level app instance. This makes the app testable (each test
    can create a fresh app instance) and avoids circular import issues.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.limiter import limiter
from app.db.session import engine

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Load ML model, create DB tables (dev only), configure NLTK
    - Shutdown: Dispose DB engine connections cleanly
    """
    # ---- STARTUP ----
    logger.info("sentinel.startup", version=settings.APP_VERSION, env=settings.APP_ENV)

    # Removed Base.metadata.create_all even for development.
    # Relying exclusively on Alembic migrations prevents schema drift
    # and avoids conflicts ('relation already exists') when transitioning to production.

    # Load the ML model into application state (once, at startup)
    from app.ml.model import MLModel
    app.state.ml_model = MLModel()
    await app.state.ml_model.load()
    logger.info(
        "sentinel.startup.model_loaded",
        version=app.state.ml_model.version,
    )

    yield  # Application is running

    # ---- SHUTDOWN ----
    logger.info("sentinel.shutdown")
    await engine.dispose()
    logger.info("sentinel.shutdown.db_disposed")


def create_application() -> FastAPI:
    """
    FastAPI application factory.

    Returns a fully configured FastAPI application instance.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-Powered Spam Detection & Threat Intelligence Platform",
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.APP_ENV != "production" else None,
        redoc_url="/redoc" if settings.APP_ENV != "production" else None,
        openapi_url="/openapi.json" if settings.APP_ENV != "production" else None,
        lifespan=lifespan,
    )

    # ---- Rate Limiter ----
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # ---- CORS ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,  # Required for HttpOnly cookie refresh tokens
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )

    # ---- Trusted Host (production hardening) ----
    if settings.APP_ENV == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )

    # ---- Exception Handlers ----
    register_exception_handlers(app)

    # ---- Routers ----
    app.include_router(api_router, prefix="/api/v1")

    # ---- Health Check (unauthenticated) ----
    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def health_check() -> dict:
        return {"status": "ok", "version": settings.APP_VERSION}

    return app


# Module-level app instance for Uvicorn
app = create_application()
