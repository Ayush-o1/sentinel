"""
SENTINEL — Prediction ORM Model
"""

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy import Uuid as UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.model_version import ModelVersion
    from app.models.user import User


class Prediction(UUIDMixin, Base):
    """
    Stores the result of a single spam analysis request.

    Design decisions:
    - original_text is stored to allow re-analysis if the model changes.
    - processed_text is stored for audit and debugging purposes.
    - suspicious_tokens is JSONB — flexible enough to store the weighted
      token list without a separate join table.
    - confidence is DECIMAL(5,4) for precision: 4 decimal places, max 1.0000.
    - created_at only (no updated_at) — predictions are immutable once created.
    """

    __tablename__ = "predictions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("model_versions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Input
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    processed_text: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="'sms' | 'email' | 'text'",
    )

    # Result
    verdict: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
        comment="'SPAM' | 'HAM'",
    )
    confidence: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=4),
        nullable=False,
        comment="0.0000 to 1.0000",
    )
    risk_level: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
        comment="'LOW' | 'MEDIUM' | 'HIGH'",
    )

    # Explainability
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    suspicious_tokens: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
        comment="[{token: str, weight: float}, ...]",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="predictions")
    model_version: Mapped[Optional["ModelVersion"]] = relationship(
        "ModelVersion", back_populates="predictions"
    )

    def __repr__(self) -> str:
        return f"<Prediction id={self.id} verdict={self.verdict} confidence={self.confidence}>"
