"""
SENTINEL — User ORM Model
"""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.prediction import Prediction
    from app.models.refresh_token import RefreshToken


class User(UUIDMixin, TimestampMixin, Base):
    """
    Represents an authenticated user of the SENTINEL platform.

    Role values:
        - "user"  : Standard user (own predictions only)
        - "admin" : Full platform access
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False,
        index=True,
        comment="RFC 5321 max email length is 320 chars",
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(
        String(72),
        nullable=False,
        comment="bcrypt hash, always 60 chars for 2a but up to 72 for 2b/2y variants",
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="user",
        server_default="user",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # Relationships
    predictions: Mapped[list["Prediction"]] = relationship(
        "Prediction",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
