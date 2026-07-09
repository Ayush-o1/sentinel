# Backend Services

## Application Lifecycle
The backend is built with FastAPI. The entry point is `app/main.py`.
SENTINEL uses the ASGI `lifespan` context manager to handle startup and shutdown logic:
1. **Startup**: Binds the asynchronous SQLAlchemy engine to PostgreSQL. Loads the ML model into `app.state.ml_model` to ensure inference runs entirely in memory without disk I/O per request.
2. **Running**: Accepts connections, routes traffic.
3. **Shutdown**: Disposes of all database connections safely.

## FastAPI Structure
- `app.api`: Contains Routers (thin controllers).
- `app.core`: System configuration, rate limiters (`slowapi`), and exception handlers.
- `app.db`: SQLAlchemy declarative bases and async session makers.
- `app.ml`: The intelligence wrapper and NLP logic.
- `app.models`: SQLAlchemy ORM classes.
- `app.schemas`: Pydantic definitions.
- `app.services`: Business logic orchestration.
- `app.repositories`: Database abstractions.

## Dependency Injection
FastAPI's `Depends()` is used pervasively.
- `get_db`: Yields an `AsyncSession` per request.
- `get_current_user`: Extracts the `Authorization` header, decodes the JWT, and queries the user from the DB.
- Services and Repositories are injected into routers to easily swap them out during unit testing.

## Error Handling
Exceptions in SENTINEL are handled globally via `app.core.exceptions`.
If a developer raises a `SentinelException`, it is caught globally by the FastAPI exception handler and formatted into a consistent JSON response:
```json
{
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "Invalid credentials",
    "details": {}
  }
}
```

## Logging
SENTINEL uses `structlog` for structured JSON logging. This ensures logs are easily parseable by aggregators like Datadog or ELK. Standard python `logging` is intercepted and rerouted to `structlog`.
