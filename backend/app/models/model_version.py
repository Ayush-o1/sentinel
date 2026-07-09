"""
SENTINEL — ModelVersion ORM Model
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from app.models.prediction import Prediction


class ModelVersion(Base):
    """
    Tracks every trained model version deployed to SENTINEL.

    Only one record should have is_active=True at any time.
    The application loads the active model at startup.

    Storing model metrics in the database allows the model health dashboard
    to display historical accuracy trends across versions without reading
    model files directly.
    """

    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    version: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        comment="Semantic version string, e.g. '1.0.0'",
    )
    algorithm: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Human-readable algorithm name",
    )
    training_date: Mapped[date] = mapped_column(Date, nullable=False)
    training_samples: Mapped[int] = mapped_column(Integer, nullable=False)

    # Evaluation metrics (stored as DECIMAL for precision)
    accuracy: Mapped[float] = mapped_column(Numeric(6, 5), nullable=False)
    precision_spam: Mapped[float] = mapped_column(Numeric(6, 5), nullable=False)
    recall_spam: Mapped[float] = mapped_column(Numeric(6, 5), nullable=False)
    f1_spam: Mapped[float] = mapped_column(Numeric(6, 5), nullable=False)

    model_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("NOW()"),
        nullable=False,
    )

    # Relationship
    predictions: Mapped[List["Prediction"]] = relationship(
        "Prediction", back_populates="model_version"
    )

    def __repr__(self) -> str:
        return f"<ModelVersion version={self.version} active={self.is_active}>"
