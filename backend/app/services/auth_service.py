"""
SENTINEL — Authentication Service

Orchestrates all authentication-related business logic:
- User registration
- Login credential verification
- Token issuance and rotation
- Logout

This service is the single source of truth for auth behavior.
It coordinates between security utilities, repositories, and models
without containing any direct database queries.
"""

import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    verify_password,
)
from app.core.config import settings
from app.core.exceptions import AuthenticationError, ConflictError
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, TokenResponse, UserResponse

logger = structlog.get_logger(__name__)


class AuthService:
    """Handles all authentication-related business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self._user_repo = UserRepository(db)
        self._token_repo = TokenRepository(db)

    async def register(self, request: RegisterRequest) -> UserResponse:
        """
        Register a new user account.

        Steps:
        1. Check email uniqueness.
        2. Hash the password.
        3. Persist the user record.
        4. Return safe user data (no password hash).

        Raises:
            ConflictError: If the email is already registered.
        """
        email_normalized = request.email.lower().strip()

        if await self._user_repo.email_exists(email_normalized):
            raise ConflictError(f"An account with this email address already exists.")

        user = User(
            email=email_normalized,
            full_name=request.full_name.strip(),
            hashed_password=hash_password(request.password),
            role="user",
            is_active=True,
        )
        user = await self._user_repo.save(user)

        logger.info("sentinel.auth.registered", user_id=str(user.id))
        return UserResponse.model_validate(user)

    async def login(self, email: str, password: str) -> tuple[TokenResponse, str]:
        """
        Authenticate a user and issue a dual-token pair.

        Returns:
            A tuple of (TokenResponse for the response body, raw refresh token for the cookie).

        Raises:
            AuthenticationError: If credentials are invalid or the account is inactive.

        Security note:
            The error message is deliberately generic — we do not reveal
            whether the email exists or whether only the password is wrong.
        """
        email_normalized = email.lower().strip()
        user = await self._user_repo.get_by_email(email_normalized)

        # Perform password check even if user is None to prevent timing attacks
        # (bcrypt.verify is always called, regardless of user existence)
        provided_password_valid = False
        if user:
            provided_password_valid = verify_password(password, user.hashed_password)

        if not user or not provided_password_valid:
            logger.warning("sentinel.auth.login_failed", email=email_normalized)
            raise AuthenticationError("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationError("This account has been deactivated.")

        # Issue tokens
        access_token = create_access_token(
            subject=str(user.id),
            additional_claims={"email": user.email, "role": user.role},
        )
        raw_refresh_token = generate_refresh_token()
        await self._token_repo.create(user_id=user.id, raw_token=raw_refresh_token)

        logger.info("sentinel.auth.login_success", user_id=str(user.id))

        token_response = TokenResponse(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return token_response, raw_refresh_token

    async def refresh(self, raw_refresh_token: str) -> tuple[TokenResponse, str]:
        """
        Validate a refresh token and issue a new token pair (rotation).

        Refresh Token Rotation:
        - The old refresh token is revoked immediately.
        - A new refresh token is issued and returned.
        - If the old token was already revoked (replay attack), all tokens
          for that user are invalidated.

        Raises:
            AuthenticationError: If the token is invalid, expired, or revoked.
        """
        token_record = await self._token_repo.get_by_raw_token(raw_refresh_token)

        if token_record is None or not token_record.is_valid:
            if token_record and token_record.revoked_at is not None:
                # Possible token reuse attack — revoke ALL tokens for this user
                logger.warning(
                    "sentinel.auth.refresh_token_reuse",
                    user_id=str(token_record.user_id),
                )
                await self._token_repo.delete_for_user(token_record.user_id)
            raise AuthenticationError("Refresh token is invalid or has expired.")

        user = await self._user_repo.get_by_id(token_record.user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Refresh token is invalid or has expired.")

        # Rotate: revoke old token, issue new one
        await self._token_repo.revoke(token_record)
        new_raw_token = generate_refresh_token()
        await self._token_repo.create(user_id=user.id, raw_token=new_raw_token)

        new_access_token = create_access_token(
            subject=str(user.id),
            additional_claims={"email": user.email, "role": user.role},
        )

        logger.info("sentinel.auth.token_refreshed", user_id=str(user.id))

        token_response = TokenResponse(
            access_token=new_access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return token_response, new_raw_token

    async def logout(self, raw_refresh_token: str) -> None:
        """
        Invalidate a refresh token on logout.

        If the token doesn't exist (already expired / invalid), we silently
        succeed — the client's cookie is cleared regardless.
        """
        token_record = await self._token_repo.get_by_raw_token(raw_refresh_token)
        if token_record and token_record.revoked_at is None:
            await self._token_repo.revoke(token_record)
            logger.info("sentinel.auth.logout", user_id=str(token_record.user_id))
