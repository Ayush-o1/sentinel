"""
SENTINEL — ML Model Wrapper

Loads the trained scikit-learn pipeline from disk and exposes a clean
async-compatible predict() interface.

The model is loaded ONCE at application startup via the lifespan event
and held in app.state.ml_model. This means:
- Zero per-request model loading overhead.
- Prediction is synchronous (sklearn is CPU-bound, not I/O-bound) but
  wrapped in asyncio.to_thread() to avoid blocking the event loop.

Architecture note:
    This class wraps the sklearn pipeline, not sklearn directly.
    If the underlying model is ever swapped (e.g., to DistilBERT),
    only this class needs to change — not the service or the routes.
"""

import asyncio
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import structlog

from app.core.config import settings
from app.ml.explainer import SentinelExplainer
from app.ml.pipeline import preprocess

logger = structlog.get_logger(__name__)

# Path to the directory containing serialized model files
MODELS_DIR = Path(__file__).parent / "models"


class MLModel:
    """
    Wrapper around the trained scikit-learn spam classification pipeline.

    Responsibilities:
    - Load the model from disk at startup.
    - Preprocess input text via the NLP pipeline.
    - Run TF-IDF + Logistic Regression inference.
    - Generate LIME explanations.
    - Return a structured result dict.
    """

    def __init__(self) -> None:
        self._pipeline = None  # sklearn Pipeline (TF-IDF + LogisticRegression)
        self._explainer = SentinelExplainer()
        self.version: str = settings.ACTIVE_MODEL_VERSION
        self._model_path = MODELS_DIR / settings.MODEL_FILE_NAME

    async def load(self) -> None:
        """
        Load the model pipeline from disk (non-blocking).

        If the model file does not exist (e.g., first run before training),
        the model is set to None and a warning is logged. Prediction requests
        will fail gracefully with an MLInferenceError.
        """
        if not self._model_path.exists():
            logger.warning(
                "sentinel.model.file_not_found",
                path=str(self._model_path),
                message="Run the training script to generate the model file.",
            )
            return

        # Load in a thread to avoid blocking the event loop during startup
        self._pipeline = await asyncio.to_thread(joblib.load, self._model_path)
        logger.info(
            "sentinel.model.loaded",
            path=str(self._model_path),
            version=self.version,
        )

    def is_ready(self) -> bool:
        """True if the model has been loaded and is ready to serve predictions."""
        return self._pipeline is not None

    async def predict(self, raw_text: str) -> dict[str, Any]:
        """
        Run the full inference pipeline on raw input text.

        Steps:
            1. NLP preprocessing
            2. TF-IDF transform + Logistic Regression predict_proba
            3. LIME explanation
            4. Return structured result

        Args:
            raw_text: The raw, unprocessed message text.

        Returns:
            Dict with keys: verdict, confidence, processed_text, suspicious_tokens.

        Raises:
            RuntimeError: If the model has not been loaded.
        """
        if not self.is_ready():
            raise RuntimeError(
                "ML model is not loaded. Run the training script first."
            )

        # Step 1: Preprocess (pure CPU — run in thread)
        nlp_result = await asyncio.to_thread(preprocess, raw_text)
        processed_text: str = nlp_result["processed_text"]

        # Step 2: Inference (sklearn — run in thread to avoid blocking event loop)
        probabilities = await asyncio.to_thread(
            self._pipeline.predict_proba, [processed_text]
        )
        proba = probabilities[0]  # [ham_prob, spam_prob]
        spam_prob = float(proba[1])
        ham_prob = float(proba[0])

        verdict = "SPAM" if spam_prob >= 0.5 else "HAM"
        confidence = spam_prob if verdict == "SPAM" else ham_prob

        # Step 3: LIME explanation (runs multiple predictions — most expensive step)
        def _predict_fn(texts: list[str]) -> np.ndarray:
            """Adapter: LIME requires a synchronous callable."""
            return self._pipeline.predict_proba(texts)

        suspicious_tokens = await asyncio.to_thread(
            self._explainer.explain,
            processed_text,
            _predict_fn,
            verdict,
        )

        return {
            "verdict": verdict,
            "confidence": round(confidence, 4),
            "processed_text": processed_text,
            "suspicious_tokens": suspicious_tokens,
        }
