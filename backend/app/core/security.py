"""
SENTINEL — Security Utilities

Centralizes all cryptographic operations:
- Password hashing and verification (bcrypt via passlib)
- JWT access token creation and decoding
- Refresh token generation

Design principles:
    - All security logic is isolated in this module.
    - Application code NEVER calls bcrypt or jose directly.
    - This makes it trivial to swap implementations if needed.
"""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# ---------------------------------------------------------------------------
# Password Hashing
# ---------------------------------------------------------------------------

# bcrypt with a cost factor validated for ~250ms compute time on modern hardware.
# This strikes the right balance: fast enough for UX, slow enough to resist brute force.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Returns:
        The bcrypt hash string (60 chars, includes salt).
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.

    Uses a timing-safe comparison internally (passlib handles this).
    Never implement your own equality check for hashes.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT Access Tokens
# ---------------------------------------------------------------------------

def create_access_token(subject: str, additional_claims: dict[str, Any] | None = None) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: The user's UUID (str) — stored in the 'sub' claim.
        additional_claims: Optional dict of extra claims (e.g., role, email).

    Returns:
        A signed JWT string.
    """
    now = datetime.now(tz=UTC)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "jti": str(uuid.uuid4()),  # JWT ID — unique per token, enables future blacklisting
    }

    if additional_claims:
        payload.update(additional_claims)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Raises:
        JWTError: If the token is invalid, expired, or tampered with.

    Returns:
        The decoded payload dict.
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


# ---------------------------------------------------------------------------
# Refresh Tokens
# ---------------------------------------------------------------------------

def generate_refresh_token() -> str:
    """
    Generate a cryptographically secure opaque refresh token.

    Refresh tokens are NOT JWTs. They are random 256-bit hex strings.
    Only the SHA-256 hash is stored in the database — the raw token
    is sent to the client once and never stored in plaintext.

    Returns:
        A 64-character hex string (256 bits of entropy).
    """
    return secrets.token_hex(32)


def hash_refresh_token(raw_token: str) -> str:
    """
    SHA-256 hash a refresh token for database storage.

    We store the hash, not the raw token, so a database breach does not
    expose valid refresh tokens. This mirrors how bcrypt protects passwords.

    Returns:
        64-character lowercase hex SHA-256 digest.
    """
    return hashlib.sha256(raw_token.encode()).hexdigest()
