# Architecture & Design

## System Overview
SENTINEL follows a strict layered architecture to ensure separation of concerns, scalability, and testability. The platform relies on a React Single Page Application (SPA) communicating with an asynchronous FastAPI backend via REST.

## High-Level Architecture
1. **Presentation Layer**: React 19 Frontend (Vite, TypeScript).
2. **Transport Layer**: Nginx (if deployed), Uvicorn ASGI server.
3. **Application Layer**: FastAPI Routers and Pydantic validation.
4. **Business Layer**: Services (`PredictionService`, `AuthService`).
5. **Intelligence Layer**: Scikit-Learn `LinearSVC` and LIME.
6. **Data Access Layer**: SQLAlchemy Repositories (`UserRepository`).
7. **Persistence Layer**: PostgreSQL 15.

## Request Lifecycle (Prediction)
1. **Client** issues `POST /api/v1/predict` with `{ "text": "Win free cash!" }`.
2. **Router** (`app/api/v1/predict.py`) parses the payload and injects the `PredictionService`.
3. **PredictionService** intercepts the request and calls the in-memory `MLModel`.
4. **MLModel**:
   - Dispatches NLP preprocessing to a background thread (`asyncio.to_thread`).
   - Executes `predict_proba` via the loaded scikit-learn pipeline.
   - Triggers the `SentinelExplainer` (LIME) to calculate word weights.
5. **PredictionService** passes the generated result to `PredictionRepository.save()`.
6. **PredictionRepository** inserts the row into PostgreSQL and commits the async transaction.
7. **Router** returns the Pydantic-serialized JSON back to the client.

## Component Responsibilities
- **Controllers (Routers)**: Handle HTTP boundaries, parse inputs, and format outputs. No business logic.
- **Services**: Orchestrate workflows, enforce business rules, and tie multiple repositories together.
- **Repositories**: Encapsulate all database interaction and SQLAlchemy syntax.
- **Models**: SQLAlchemy ORM definitions mapping directly to PostgreSQL tables.
- **Schemas**: Pydantic definitions defining exact JSON shapes and performing input validation.

## Future Scalability
- **Horizontal Scaling**: The FastAPI backend is entirely stateless. Access tokens are JWTs. Multiple Uvicorn workers or Docker containers can be spawned behind a load balancer without configuration changes.
- **Model Decoupling**: If the ML pipeline becomes heavy, the `MLModel` class can be easily refactored to wrap a gRPC call to a dedicated GPU-backed microservice (e.g., NVIDIA Triton or TorchServe).
