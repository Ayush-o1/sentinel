"""
SENTINEL — Authentication Pydantic Schemas

Request and response models for all auth endpoints.
All schemas use strict validation — no silent coercion.
"""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """Request body for POST /api/v1/auth/register"""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=128, description="Plain-text password")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full display name")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Enforce password policy:
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit.")
        return v

    @field_validator("full_name")
    @classmethod
    def sanitize_full_name(cls, v: str) -> str:
        return v.strip()


class LoginRequest(BaseModel):
    """Request body for POST /api/v1/auth/login"""

    email: EmailStr
    password: str = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    """User profile data returned by the API. Never includes the password hash."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime


class UserProfileResponse(UserResponse):
    """Extended profile response including usage statistics."""

    total_predictions: int = 0


class TokenResponse(BaseModel):
    """Response body for login and token refresh endpoints."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until expiry
