# Testing Strategy

SENTINEL employs a robust automated testing strategy centered entirely around `pytest` and `httpx`.

## Structure
- `tests/unit/`: Tests individual functions in isolation (e.g., the `app/ml/pipeline.py` NLP functions) without requiring a database connection or ML model load.
- `tests/integration/`: End-to-end tests that spin up an ephemeral test database, load the actual ML model, hit the FastAPI routing layer via `AsyncClient`, and verify database persistence.

## Executing Tests

To run the complete test suite locally:
```bash
cd backend
source .venv/bin/activate

# Execute all tests
pytest -v

# Execute only unit tests
pytest tests/unit/ -v
```

## Integration Test Mechanics
Integration testing in an async FastAPI + SQLAlchemy environment is complex. SENTINEL solves this cleanly in `tests/conftest.py`:
1. **Ephemeral DB**: An entirely separate SQLite (or ephemeral Postgres) database is spun up for tests to prevent corrupting development data.
2. **Dependency Overrides**: The `app.dependency_overrides[get_db]` is utilized to inject the test database session into the FastAPI routers.
3. **Lifespan Simulation**: `httpx.ASGITransport` does not natively trigger FastAPI lifespan events. Therefore, `conftest.py` manually instantiates the `MLModel` and forces the `.joblib` model load so the `/api/v1/predict` endpoints function perfectly.
4. **Rate Limiting Bypass**: The `slowapi` limiter is explicitly disabled in the test fixture to prevent `429 Too Many Requests` when tests run at millisecond speeds.

## Continuous Integration (CI)
The test suite is hooked into GitHub Actions (`.github/workflows/ci.yml`). Every push or pull request to the `main` branch spins up an isolated Ubuntu container, installs PostgreSQL, runs Alembic migrations, and enforces the `pytest` suite before allowing merges.
