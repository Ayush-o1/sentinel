"""
SENTINEL — Prediction Router

POST /api/v1/predict — Analyze a message
"""

import uuid

from fastapi import APIRouter, Request, status

from app.core.config import settings
from app.core.dependencies import CurrentUser, DbSession
from app.core.limiter import limiter
from app.schemas.prediction import PredictRequest, PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter()


@router.post(
    "",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze a message for spam",
    description=(
        "Submit a text message (SMS, email, or plain text) for spam classification. "
        "Returns the verdict, confidence score, suspicious tokens, and a natural-language explanation."
    ),
)
@limiter.limit(settings.RATE_LIMIT_PREDICT)
async def predict(
    request_data: PredictRequest,
    request: Request,          # Required by slowapi for rate limiting key extraction
    current_user: CurrentUser,
    db: DbSession,
) -> PredictionResponse:
    service = PredictionService(db=db, request=request)
    return await service.analyze(
        user_id=current_user.id,
        request_data=request_data,
    )
