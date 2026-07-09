"""
SENTINEL — RefreshToken ORM Model
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if __name__ != "__main__":
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from app.models.user import User


class RefreshToken(Base):
    """
    Stores hashed refresh tokens for server-side session management.

    Design:
    - Only the SHA-256 hash is stored — raw tokens are never persisted.
    - revoked_at enables graceful invalidation without deleting records
      (useful for audit trails of logout events).
    - On refresh token rotation, the old record is deleted (or revoked_at
      is set) and a new record is inserted.
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="SHA-256 hex digest of the raw refresh token UUID",
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("NOW()"),
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Set when the token is invalidated (logout or rotation)",
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    @property
    def is_valid(self) -> bool:
        """True if the token has not expired and has not been revoked."""
        now = datetime.now(timezone.utc)
        return self.revoked_at is None and self.expires_at > now

    def __repr__(self) -> str:
        return f"<RefreshToken id={self.id} user_id={self.user_id} valid={self.is_valid}>"
