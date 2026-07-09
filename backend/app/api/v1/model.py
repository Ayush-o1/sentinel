"""
SENTINEL — Model Info Router

GET /api/v1/model/info — Return active model metadata
"""

from fastapi import APIRouter, Request

from app.core.dependencies import CurrentUser
from app.schemas.analytics import ModelInfoResponse

router = APIRouter()


@router.get(
    "/info",
    response_model=ModelInfoResponse,
    summary="Get current active model metadata",
)
async def get_model_info(
    request: Request,
    current_user: CurrentUser,
) -> ModelInfoResponse:
    """
    Returns metadata about the currently active ML model.
    This powers the "Model Health" indicator on the dashboard.

    In a production setup with multiple model versions, this would
    query the model_versions table for the active record.
    For MVP, we return the in-memory model's metadata.
    """
    ml_model = request.app.state.ml_model

    if not ml_model.is_ready():
        return ModelInfoResponse(
            version="N/A",
            algorithm="Not loaded",
            training_date="N/A",
            training_samples=0,
            accuracy=0.0,
            precision_spam=0.0,
            recall_spam=0.0,
            f1_spam=0.0,
            status="UNAVAILABLE",
        )

    # In production: query model_versions WHERE is_active = true
    # For MVP: return static metadata (updated when model is retrained)
    return ModelInfoResponse(
        version=ml_model.version,
        algorithm="Logistic Regression + TF-IDF (ngram 1-2)",
        training_date="2026-07-09",  # Updated post-training
        training_samples=5572,
        accuracy=0.98700,
        precision_spam=0.97300,
        recall_spam=0.95100,
        f1_spam=0.96200,
        status="ACTIVE",
    )
