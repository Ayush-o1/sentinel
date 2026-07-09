"""
Unit tests for the NLP preprocessing pipeline.

These tests verify each stage of the pipeline in isolation.
No ML model or database is required.
"""

import pytest

from app.ml.pipeline import preprocess


class TestNLPPipeline:
    """Tests for the text preprocessing pipeline."""

    def test_basic_ham_message(self):
        result = preprocess("Hey, are you coming to the meeting tomorrow?")
        assert result["processed_text"]
        assert "hey" in result["tokens"] or "coming" in result["tokens"]
        assert result["original_length"] > 0

    def test_url_replacement(self):
        result = preprocess("Click here to claim your prize: https://spam.example.com/win")
        assert "url_token" in result["processed_text"]
        assert "spam.example.com" not in result["processed_text"]

    def test_email_replacement(self):
        result = preprocess("Send your details to scammer@badactor.com immediately")
        assert "email_token" in result["processed_text"]

    def test_phone_replacement(self):
        result = preprocess("Call us now at 555-123-4567 for a free prize!")
        assert "phone_token" in result["processed_text"]

    def test_number_replacement(self):
        result = preprocess("You have won 5000 dollars in the lottery")
        assert "number_token" in result["processed_text"]

    def test_spam_signal_words_preserved(self):
        """Words like 'free', 'win', 'prize' must NOT be removed as stopwords."""
        result = preprocess("You have won a free prize worth 1000 dollars!")
        tokens_str = " ".join(result["tokens"])
        # At least some spam signal words should survive
        spam_signals = {"free", "win", "winner", "prize"}
        preserved = spam_signals.intersection(set(result["tokens"]))
        assert len(preserved) > 0, f"No spam signals preserved in: {tokens_str}"

    def test_lowercase_normalization(self):
        result = preprocess("URGENT! You MUST claim your FREE offer NOW!")
        # All tokens should be lowercase after processing
        for token in result["tokens"]:
            if token not in {"URL_TOKEN", "EMAIL_TOKEN", "PHONE_TOKEN", "NUMBER_TOKEN"}:
                assert token == token.lower(), f"Token not lowercased: {token}"

    def test_empty_after_strip_short_message(self):
        """Messages that are too short after processing should still not crash."""
        result = preprocess("Hello there friend, how are you doing today?")
        assert isinstance(result["processed_text"], str)
        assert isinstance(result["tokens"], list)

    def test_output_keys(self):
        result = preprocess("Test message for pipeline output validation.")
        assert "processed_text" in result
        assert "tokens" in result
        assert "original_length" in result
