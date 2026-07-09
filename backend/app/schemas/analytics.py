"""
SENTINEL — Analytics Pydantic Schemas
"""


from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    """Aggregate statistics for a user's prediction history."""

    total_predictions: int
    spam_count: int
    ham_count: int
    spam_rate: float
    avg_confidence: float
    high_confidence_spam: int
    predictions_today: int
    most_common_spam_tokens: list[str]


class TimelineDataPoint(BaseModel):
    """A single date's prediction breakdown for the timeline chart."""

    date: str  # ISO date string "YYYY-MM-DD"
    spam: int
    ham: int
    total: int


class TimelineResponse(BaseModel):
    period: str
    data: list[TimelineDataPoint]


class ConfidenceBucket(BaseModel):
    """A single bucket in the confidence distribution histogram."""

    range: str  # e.g. "0.9–1.0"
    count: int


class ConfidenceDistributionResponse(BaseModel):
    buckets: list[ConfidenceBucket]


class ModelInfoResponse(BaseModel):
    """Current active model metadata."""

    version: str
    algorithm: str
    training_date: str
    training_samples: int
    accuracy: float
    precision_spam: float
    recall_spam: float
    f1_spam: float
    status: str  # "ACTIVE" | "INACTIVE"
