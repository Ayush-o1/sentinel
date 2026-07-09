"""
SENTINEL — Prediction History Router

GET    /api/v1/predictions              — List paginated history
GET    /api/v1/predictions/{id}         — Get single prediction detail
DELETE /api/v1/predictions/{id}         — Delete a prediction
"""

import math
from typing import Optional
import uuid

from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import AuthorizationError, NotFoundError
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.prediction import PredictionDetail, PredictionSummary

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[PredictionSummary],
    summary="Get paginated prediction history",
)
async def get_history(
    current_user: CurrentUser,
    db: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    verdict: Optional[str] = Query(default=None, pattern="^(SPAM|HAM)$"),
    message_type: Optional[str] = Query(default=None, pattern="^(sms|email|text)$"),
    sort_by: str = Query(default="created_at", pattern="^(created_at|confidence)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
) -> PaginatedResponse[PredictionSummary]:
    repo = PredictionRepository(db)
    predictions, total = await repo.get_paginated_for_user(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        verdict_filter=verdict,
        message_type_filter=message_type,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    items = [
        PredictionSummary(
            id=p.id,
            verdict=p.verdict,  # type: ignore[arg-type]
            confidence=float(p.confidence),
            risk_level=p.risk_level,  # type: ignore[arg-type]
            message_type=p.message_type,  # type: ignore[arg-type]
            text_preview=p.original_text[:120] if p.original_text else None,
            created_at=p.created_at,
        )
        for p in predictions
    ]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.get(
    "/{prediction_id}",
    response_model=PredictionDetail,
    summary="Get a single prediction by ID",
)
async def get_prediction(
    prediction_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> PredictionDetail:
    repo = PredictionRepository(db)
    prediction = await repo.get_by_id_for_user(prediction_id, current_user.id)

    if prediction is None:
        raise NotFoundError("Prediction", str(prediction_id))

    return PredictionDetail(
        id=prediction.id,
        verdict=prediction.verdict,  # type: ignore[arg-type]
        confidence=float(prediction.confidence),
        risk_level=prediction.risk_level,  # type: ignore[arg-type]
        message_type=prediction.message_type,  # type: ignore[arg-type]
        text_preview=prediction.original_text[:120],
        created_at=prediction.created_at,
        original_text=prediction.original_text,
        processed_text=prediction.processed_text,
        explanation=prediction.explanation,
        suspicious_tokens=prediction.suspicious_tokens,  # type: ignore[arg-type]
    )


@router.delete(
    "/{prediction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a prediction from history",
)
async def delete_prediction(
    prediction_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> None:
    repo = PredictionRepository(db)
    prediction = await repo.get_by_id_for_user(prediction_id, current_user.id)

    if prediction is None:
        raise NotFoundError("Prediction", str(prediction_id))

    await repo.delete(prediction)
