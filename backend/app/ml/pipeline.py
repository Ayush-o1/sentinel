"""
SENTINEL — NLP Preprocessing Pipeline

Implements the 11-stage text preprocessing pipeline defined in the
Phase 1 architecture document.

This pipeline transforms raw input text into a clean, normalized form
suitable for TF-IDF vectorization. It also retains the token list
for LIME explainability.

Design:
    - The pipeline is stateless: calling preprocess(text) always produces
      the same output for the same input.
    - NLTK resources are downloaded lazily on first use (with a check to
      avoid re-downloading).
    - The pipeline is a pure Python function — no ML model dependency.
      This makes it independently testable.
"""

import re
import string
from typing import Any

import emoji
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ---------------------------------------------------------------------------
# NLTK Resource Bootstrap
# ---------------------------------------------------------------------------
# These downloads are idempotent (NLTK checks before re-downloading).
# In production, bake these into the Docker image via a setup script.
# ---------------------------------------------------------------------------

def _ensure_nltk_resources() -> None:
    """Download required NLTK datasets if not already present."""
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4"),
    ]
    for path, package in resources:
        try:
            nltk.data.find(path)
        except (LookupError, OSError):
            nltk.download(package, quiet=True)


_ensure_nltk_resources()

# ---------------------------------------------------------------------------
# Domain-Specific Stopword Customization
# ---------------------------------------------------------------------------
# Standard NLTK stopwords include words like "free", "win", "now", "today"
# which are strong spam signals. We remove these from the stopword list
# so they are PRESERVED in the token stream and contribute to TF-IDF scores.
# ---------------------------------------------------------------------------

_SPAM_SIGNAL_WORDS = {
    "free", "win", "winner", "won", "prize", "offer", "urgent",
    "now", "today", "call", "click", "reply", "send", "buy",
    "cash", "money", "cheap", "deal", "discount", "limited",
    "you", "your", "you've", "claim",
}

_BASE_STOPWORDS = set(stopwords.words("english"))
CUSTOM_STOPWORDS = _BASE_STOPWORDS - _SPAM_SIGNAL_WORDS

# ---------------------------------------------------------------------------
# Regex Patterns (compiled once at module load for performance)
# ---------------------------------------------------------------------------

_URL_PATTERN = re.compile(
    r"https?://\S+|www\.\S+|bit\.ly/\S+|tinyurl\.com/\S+",
    re.IGNORECASE,
)
_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
_PHONE_PATTERN = re.compile(
    r"(\+?\d{1,3}[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}"
)
_NUMBER_PATTERN = re.compile(r"\b\d+\b")
_EXCESS_PUNCT_PATTERN = re.compile(r"([!?]){2,}")
_WHITESPACE_PATTERN = re.compile(r"\s+")

# ---------------------------------------------------------------------------
# Lemmatizer Instance
# ---------------------------------------------------------------------------
_lemmatizer = WordNetLemmatizer()


# ---------------------------------------------------------------------------
# Pipeline Implementation
# ---------------------------------------------------------------------------

def preprocess(text: str) -> dict[str, Any]:
    """
    Run the full 11-stage NLP preprocessing pipeline.

    Args:
        text: Raw input text (SMS, email, or plain text).

    Returns:
        A dict with:
            - "processed_text": The cleaned, normalized string for TF-IDF.
            - "tokens": The list of individual processed tokens.
            - "original_length": Length of the raw input.
    """
    original_length = len(text)

    # Stage 1: Normalize unicode & lowercase
    text = text.strip().lower()

    # Stage 2: URL replacement
    text = _URL_PATTERN.sub(" URL_TOKEN ", text)

    # Stage 3: Email address replacement
    text = _EMAIL_PATTERN.sub(" EMAIL_TOKEN ", text)

    # Stage 4: Phone number replacement
    text = _PHONE_PATTERN.sub(" PHONE_TOKEN ", text)

    # Stage 5: Number normalization
    text = _NUMBER_PATTERN.sub(" NUMBER_TOKEN ", text)

    # Stage 6: Punctuation — collapse excess, then remove most punctuation
    text = _EXCESS_PUNCT_PATTERN.sub(r"\1", text)  # !!!→! ???→?
    # Remove punctuation except our placeholder underscores
    text = text.translate(
        str.maketrans("", "", string.punctuation.replace("_", ""))
    )

    # Stage 7: Emoji → text description
    text = emoji.demojize(text, delimiters=(" ", " "))

    # Stage 8: Normalize whitespace
    text = _WHITESPACE_PATTERN.sub(" ", text).strip()

    # Stage 9: Tokenize
    tokens = word_tokenize(text)

    # Stage 10: Stopword removal (using our custom list)
    tokens = [t for t in tokens if t not in CUSTOM_STOPWORDS and len(t) > 1]

    # Stage 11: Lemmatization
    tokens = [_lemmatizer.lemmatize(t) for t in tokens]

    processed_text = " ".join(tokens)

    return {
        "processed_text": processed_text,
        "tokens": tokens,
        "original_length": original_length,
    }
