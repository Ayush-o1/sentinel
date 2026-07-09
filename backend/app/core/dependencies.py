"""
SENTINEL — FastAPI Dependency Injection

This module provides reusable FastAPI dependencies injected via Depends().

Dependencies defined here:
    - get_db: Async database session per request
    - get_current_user: Validates JWT and returns the authenticated user
    - get_current_active_user: Ensures user account is not disabled
    - require_admin: Restricts endpoints to admin role only

Usage in route handlers:
    @router.get("/protected")
    async def protected_route(user: User = Depends(get_current_active_user)):
        ...
"""

from collections.abc import AsyncGenerator
from typing import Annotated

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError as JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import AsyncSessionFactory
from app.models.user import User

logger = structlog.get_logger(__name__)

# OAuth2 Bearer scheme — automatically parses "Authorization: Bearer <token>"
bearer_scheme = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Database Session Dependency
# ---------------------------------------------------------------------------

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async database session for the lifetime of a single request.

    The session is automatically committed or rolled back based on whether
    the request completed successfully. Always closed after the response.

    Yields:
        An open AsyncSession bound to the current request.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Type alias for cleaner route signatures
DbSession = Annotated[AsyncSession, Depends(get_db)]


# ---------------------------------------------------------------------------
# Authentication Dependencies
# ---------------------------------------------------------------------------

async def get_current_user(
    db: DbSession,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    """
    Extract and validate the JWT from the Authorization header.

    Raises:
        HTTPException 401: If the token is missing, malformed, expired, or
                           refers to a non-existent user.

    Returns:
        The User ORM object for the authenticated user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        logger.warning("sentinel.auth.invalid_token")
        raise credentials_exception from None

    # Import here to avoid circular dependency with user model
    from app.repositories.user_repository import UserRepository
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if user is None:
        logger.warning("sentinel.auth.user_not_found", user_id=user_id)
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Ensure the authenticated user's account is active.

    Raises:
        HTTPException 403: If the account has been deactivated.

    Returns:
        The active User object.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support.",
        )
    return current_user


async def require_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Restrict access to admin role only.

    Raises:
        HTTPException 403: If the user is not an admin.

    Returns:
        The admin User object.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin access required.",
        )
    return current_user


# Type aliases — makes route signatures clean and readable
CurrentUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(require_admin)]
