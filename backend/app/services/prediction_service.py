"""
SENTINEL — Prediction Service

Orchestrates the complete spam analysis pipeline:
NLP Preprocessing → ML Inference → Explainability → Persistence

This is the core of SENTINEL's intelligence layer.
The service coordinates the NLP pipeline, ML model, and LIME explainer
without implementing any of them directly — adhering to SRP.
"""

import uuid
from decimal import Decimal
from typing import Any

import structlog
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import MLInferenceError
from app.models.prediction import Prediction
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.prediction import (
    PredictionExplanation,
    PredictionResponse,
    PredictRequest,
    SuspiciousToken,
)

logger = structlog.get_logger(__name__)


def _compute_risk_level(confidence: float, verdict: str) -> str:
    """
    Derive a human-readable risk level from confidence and verdict.

    Ham predictions are always LOW risk regardless of confidence.
    Spam predictions are classified by confidence tier.
    """
    if verdict == "HAM":
        return "LOW"
    if confidence >= 0.85:
        return "HIGH"
    if confidence >= 0.65:
        return "MEDIUM"
    return "LOW"


def _generate_explanation_text(
    verdict: str,
    confidence: float,
    suspicious_tokens: list[dict[str, Any]],
) -> str:
    """
    Generate a natural-language explanation for a prediction.

    This produces readable, informative output — not boilerplate.
    """
    if verdict == "HAM":
        if confidence >= 0.90:
            return (
                "This message shows strong characteristics of legitimate communication. "
                "The language is natural, contextual, and free from known spam patterns."
            )
        return (
            "This message appears to be legitimate, though some elements warranted closer inspection. "
            "No significant spam indicators were detected."
        )

    # Spam explanations
    top_tokens = [t["token"] for t in suspicious_tokens[:3]] if suspicious_tokens else []
    token_str = ", ".join(f'"{t}"' for t in top_tokens)

    if confidence >= 0.90:
        base = "This message exhibits multiple high-confidence spam indicators"
    elif confidence >= 0.70:
        base = "This message shows several characteristics commonly associated with spam"
    else:
        base = "This message contains some patterns that suggest it may be spam"

    if token_str:
        return f"{base}, including the use of {token_str}. Exercise caution before acting on this message."
    return f"{base}. Exercise caution before acting on this message."


class PredictionService:
    """
    Orchestrates the complete analysis pipeline for a single message.

    Dependencies are injected via the constructor to keep this class
    independently testable.
    """

    def __init__(self, db: AsyncSession, request: Request) -> None:
        self._db = db
        self._prediction_repo = PredictionRepository(db)
        # ML model is loaded once at app startup and stored in app.state
        self._ml_model = request.app.state.ml_model

    async def analyze(
        self,
        user_id: uuid.UUID,
        request_data: PredictRequest,
    ) -> PredictionResponse:
        """
        Run the full analysis pipeline on a submitted message.

        Pipeline:
            1. NLP preprocessing
            2. ML inference (verdict + confidence)
            3. LIME explainability (suspicious tokens)
            4. Natural language explanation generation
            5. Persist prediction to database
            6. Return structured response

        Raises:
            MLInferenceError: If the ML model fails to produce a result.
        """
        try:
            # Step 1 & 2: Preprocess + predict (the model handles preprocessing internally)
            ml_result = await self._ml_model.predict(request_data.text)

            verdict: str = ml_result["verdict"]
            confidence: float = ml_result["confidence"]
            processed_text: str = ml_result["processed_text"]
            raw_tokens: list[dict[str, Any]] = ml_result["suspicious_tokens"]

        except Exception as e:
            logger.exception("sentinel.prediction.inference_failed", error=str(e))
            raise MLInferenceError() from e

        # Step 3: Compute derived fields
        risk_level = _compute_risk_level(confidence, verdict)
        explanation_text = _generate_explanation_text(verdict, confidence, raw_tokens)

        # Step 4: Persist
        prediction = Prediction(
            user_id=user_id,
            original_text=request_data.text,
            processed_text=processed_text,
            message_type=request_data.message_type,
            verdict=verdict,
            confidence=Decimal(str(round(confidence, 4))),
            risk_level=risk_level,
            explanation=explanation_text,
            suspicious_tokens=raw_tokens,
        )
        prediction = await self._prediction_repo.save(prediction)

        logger.info(
            "sentinel.prediction.complete",
            prediction_id=str(prediction.id),
            verdict=verdict,
            confidence=confidence,
        )

        # Step 5: Build response
        return PredictionResponse(
            prediction_id=prediction.id,
            verdict=verdict,  # type: ignore[arg-type]
            confidence=float(prediction.confidence),
            message_type=request_data.message_type,  # type: ignore[arg-type]
            processed_at=prediction.created_at,
            explanation=PredictionExplanation(
                summary=explanation_text,
                suspicious_tokens=[
                    SuspiciousToken(token=t["token"], weight=t["weight"])
                    for t in raw_tokens
                ],
                risk_level=risk_level,  # type: ignore[arg-type]
            ),
        )
