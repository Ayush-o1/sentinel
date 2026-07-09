"""
SENTINEL — Authentication Router

Endpoints:
    POST /api/v1/auth/register
    POST /api/v1/auth/login
    POST /api/v1/auth/refresh
    POST /api/v1/auth/logout
    GET  /api/v1/auth/me
"""

from datetime import timedelta

from fastapi import APIRouter, Cookie, Response, status

from app.core.config import settings
from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import AuthenticationError
from app.core.limiter import limiter
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserProfileResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()

# Cookie name constant — centralized to avoid typos
REFRESH_TOKEN_COOKIE = "refresh_token"
REFRESH_TOKEN_COOKIE_PATH = "/api/v1/auth/refresh"


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    """
    Attach the refresh token as an HttpOnly Secure cookie.

    Path is scoped to the refresh endpoint only — the cookie is
    not sent with any other request, minimizing exposure.
    """
    max_age = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=raw_token,
        httponly=True,
        secure=settings.is_production,  # HTTPS only in production
        samesite="lax",
        max_age=max_age,
        path=REFRESH_TOKEN_COOKIE_PATH,
    )


def _clear_refresh_cookie(response: Response) -> None:
    """Remove the refresh token cookie."""
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE,
        path=REFRESH_TOKEN_COOKIE_PATH,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
@limiter.limit(settings.RATE_LIMIT_REGISTER)
async def register(
    request_data: RegisterRequest,
    db: DbSession,
    # NOTE: `request` is injected automatically by slowapi's limiter decorator
    # It must be the first positional param after the decorator for slowapi to work.
    # We import Request below to satisfy this requirement.
):
    from fastapi import Request as _Req  # local import to avoid circular issue
    service = AuthService(db)
    return await service.register(request_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive tokens",
)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(
    request_data: LoginRequest,
    response: Response,
    db: DbSession,
):
    service = AuthService(db)
    token_response, raw_refresh = await service.login(
        email=request_data.email,
        password=request_data.password,
    )
    _set_refresh_cookie(response, raw_refresh)
    return token_response


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using refresh token cookie",
)
async def refresh(
    response: Response,
    db: DbSession,
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_TOKEN_COOKIE),
):
    if not refresh_token:
        raise AuthenticationError("Refresh token is missing.")

    service = AuthService(db)
    token_response, new_raw_refresh = await service.refresh(refresh_token)
    _set_refresh_cookie(response, new_raw_refresh)
    return token_response


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Invalidate tokens and clear session",
)
async def logout(
    response: Response,
    db: DbSession,
    current_user: CurrentUser,
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_TOKEN_COOKIE),
):
    if refresh_token:
        service = AuthService(db)
        await service.logout(refresh_token)

    _clear_refresh_cookie(response)
    return {"message": "Successfully logged out."}


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
)
async def get_me(
    current_user: CurrentUser,
    db: DbSession,
):
    from app.repositories.user_repository import UserRepository
    user_repo = UserRepository(db)
    total_predictions = await user_repo.get_prediction_count(current_user.id)

    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        total_predictions=total_predictions,
    )
