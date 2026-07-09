"""
SENTINEL — LIME Explainability Wrapper

Wraps the LIME text explainer to produce per-prediction token importance scores.

LIME works by:
1. Creating perturbed versions of the input text.
2. Getting predictions for each perturbation from the model.
3. Fitting a locally linear surrogate model.
4. Returning feature weights (token → importance score).

Design:
    - The explainer is stateless and can be called from multiple threads.
    - Results are filtered to only include tokens with positive weights
      (tokens that pushed toward the predicted class).
    - Weights are normalized to [0, 1] for consistent frontend display.
"""

from typing import Any

from lime.lime_text import LimeTextExplainer


class SentinelExplainer:
    """
    LIME-based explainability layer for SENTINEL predictions.

    Produces a list of (token, importance_weight) pairs for the
    predicted class of a given text.
    """

    def __init__(self) -> None:
        self._explainer = LimeTextExplainer(
            class_names=["HAM", "SPAM"],
            random_state=42,  # Reproducible explanations
        )

    def explain(
        self,
        text: str,
        predict_fn: Any,
        verdict: str,
        num_features: int = 10,
        num_samples: int = 500,
    ) -> list[dict[str, Any]]:
        """
        Generate token importance scores for a prediction.

        Args:
            text: The preprocessed text to explain.
            predict_fn: A callable that accepts a list of texts and returns
                        a 2D array of class probabilities [[ham_prob, spam_prob], ...].
            verdict: The predicted verdict ("SPAM" or "HAM").
            num_features: Maximum number of tokens to include in the explanation.
            num_samples: Number of perturbations LIME generates (higher = more accurate but slower).

        Returns:
            A list of dicts: [{"token": str, "weight": float}, ...]
            Sorted by weight descending. Only positive-weight tokens included.
        """
        # LIME class index: 0=HAM, 1=SPAM
        label_index = 1 if verdict == "SPAM" else 0

        explanation = self._explainer.explain_instance(
            text_instance=text,
            classifier_fn=predict_fn,
            num_features=num_features,
            num_samples=num_samples,
            labels=[label_index],
        )

        # Extract (word, weight) pairs for the predicted label
        raw_weights = explanation.as_list(label=label_index)

        # Filter: keep only positive contributions and non-placeholder tokens
        _skip_tokens = {"url_token", "email_token", "phone_token", "number_token"}
        positive = [
            (token, weight)
            for token, weight in raw_weights
            if weight > 0 and token.lower() not in _skip_tokens
        ]

        if not positive:
            return []

        # Normalize weights to [0, 1]
        max_weight = max(w for _, w in positive)
        if max_weight == 0:
            return []

        return [
            {
                "token": token,
                "weight": round(weight / max_weight, 4),
            }
            for token, weight in sorted(positive, key=lambda x: x[1], reverse=True)
        ]
