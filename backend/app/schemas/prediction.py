"""
SENTINEL — Prediction Pydantic Schemas
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums / Literals
# ---------------------------------------------------------------------------

MessageType = Literal["sms", "email", "text"]
Verdict = Literal["SPAM", "HAM"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]


# ---------------------------------------------------------------------------
# Sub-schemas
# ---------------------------------------------------------------------------

class SuspiciousToken(BaseModel):
    """A single token with its LIME importance weight."""
    token: str
    weight: float = Field(..., ge=0.0, le=1.0)


class PredictionExplanation(BaseModel):
    """The explainability output for a single prediction."""
    summary: str
    suspicious_tokens: List[SuspiciousToken]
    risk_level: RiskLevel


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class PredictRequest(BaseModel):
    """Request body for POST /api/v1/predict"""

    text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="The message text to analyze.",
    )
    message_type: MessageType = Field(
        default="text",
        description="The type of message: 'sms', 'email', or 'text'.",
    )

    @field_validator("text")
    @classmethod
    def strip_and_validate_text(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 10:
            raise ValueError("Message text must be at least 10 characters after trimming whitespace.")
        return stripped


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class PredictionResponse(BaseModel):
    """Full prediction result returned to the client."""

    model_config = {"from_attributes": True}

    prediction_id: uuid.UUID
    verdict: Verdict
    confidence: float
    message_type: MessageType
    processed_at: datetime
    explanation: PredictionExplanation


class PredictionSummary(BaseModel):
    """Compact prediction item for list views."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    verdict: Verdict
    confidence: float
    risk_level: RiskLevel
    message_type: MessageType
    # Truncated preview of the original message (first 120 chars)
    text_preview: Optional[str] = None
    created_at: datetime


class PredictionDetail(PredictionSummary):
    """Full prediction detail including the original text and explanation."""

    original_text: str
    processed_text: str
    explanation: str
    suspicious_tokens: List[SuspiciousToken]
