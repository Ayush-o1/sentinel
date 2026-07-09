# Engineering Decisions Log

This document records major technical choices made during the development of SENTINEL, including alternatives considered and trade-offs accepted.

## Why FastAPI?
- **Decision**: Use FastAPI over Django or Flask.
- **Why**: The project heavily relies on rapid API development, strong JSON validation, and asynchronous execution. FastAPI's native integration with Pydantic provides type-safe schemas out of the box. The asynchronous ASGI support (`async/await`) ensures that ML inferences (delegated to threads) don't block concurrent HTTP requests.
- **Trade-off**: Lacks the built-in ORM and admin panels of Django, requiring manual wire-up of SQLAlchemy and Alembic.

## Why PostgreSQL?
- **Decision**: Use PostgreSQL 15 over MongoDB or SQLite.
- **Why**: SENTINEL requires relational integrity. A User has many Predictions, and if a User is deleted, their predictions must be explicitly handled (Cascade). PostgreSQL provides powerful JSONB support, which we leverage to store the dynamic `suspicious_tokens` list from LIME without needing a dedicated join table.

## Why Linear Support Vector Machine (LinearSVC)?
- **Decision**: Use `LinearSVC` wrapped in `CalibratedClassifierCV` instead of Deep Learning (e.g., BERT).
- **Why**: The dataset (SMS Spam) is relatively simple text. An SVM trains in seconds, evaluates in milliseconds, and requires less than 20MB of disk space. A transformer model would require hundreds of megabytes, a GPU for acceptable latency, and significantly higher infrastructure costs, with only marginal gains in F1-score (95.2% vs ~97%).
- **Trade-off**: The LinearSVC cannot output probabilities inherently, which is why it must be wrapped in a Probability Calibrator.

## Why TF-IDF?
- **Decision**: Use Term Frequency-Inverse Document Frequency instead of Word Embeddings (Word2Vec, GloVe).
- **Why**: TF-IDF provides high explainability. Each token maps directly to a discrete feature column, making it perfectly compatible with LIME. Word embeddings obscure the exact feature origin.

## Why JWT (Stateless Auth)?
- **Decision**: Use stateless Access Tokens and stateful/cookie-based Refresh Tokens over session tracking (Redis).
- **Why**: Reduces backend infrastructure complexity by avoiding a Redis dependency. Access tokens are validated cryptographically via the `SECRET_KEY` with zero database hits.

## Why the Repository Pattern?
- **Decision**: Decouple database queries into a `Repository` layer.
- **Why**: Simplifies unit testing. We can mock the `PredictionRepository` entirely when testing the `PredictionService` without needing to mock complex SQLAlchemy `Select` statements.

## Why Docker?
- **Decision**: Containerize via Docker Compose.
- **Why**: Guarantee "it works on my machine" consistency. Encapsulates the Python virtual environment and the PostgreSQL database into a single `docker-compose up` command, drastically reducing developer onboarding friction.
