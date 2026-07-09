# PROJECT_GUIDE

Welcome to Project SENTINEL. This guide serves as the ultimate knowledge transfer document, designed to quickly onboard new engineers or AI assistants.

## What is this project?
SENTINEL is an AI-powered Threat Intelligence Platform. It intercepts text messages, emails, or plain text, processes them using Natural Language Processing (NLP), and runs them through a calibrated Machine Learning model (Linear Support Vector Machine) to classify them as `SPAM` or `HAM`. It uses LIME to provide explainability (highlighting exactly *why* a message is spam). 

## How is the code organized?
The repository is split into three main areas:
1. **`backend/`**: A Python 3.11 FastAPI application using asynchronous SQLAlchemy 2.0 with PostgreSQL.
2. **`frontend/`**: A React 19 Single Page Application built with Vite and TypeScript.
3. **`ml/`** *(Offline)*: Jupyter notebooks and scripts used to train and serialize the model.

## How does a request flow?
When a user submits a message for analysis:
1. **Frontend**: React captures the text and sends a `POST /api/v1/predict` request with the JWT access token.
2. **Backend Router**: `app/api/v1/predict.py` receives the request and validates the payload using Pydantic.
3. **Backend Service**: `PredictionService.analyze()` is invoked.
4. **ML Inference**: The text is passed to `app.state.ml_model` (loaded into memory at startup).
   - `preprocess()` strips URLs, normalizes whitespace, and lemmatizes the text.
   - `_pipeline.predict_proba()` calculates the Spam vs. Ham probability.
   - `LIME` runs multiple perturbations to determine token weights.
5. **Database**: `PredictionRepository` saves the raw text, processed text, verdict, confidence, and LIME tokens into PostgreSQL.
6. **Response**: FastAPI returns the structured payload. The frontend displays the verdict, a confidence chart, and a highlighted text breakdown.

## Where does Authentication happen?
SENTINEL uses a stateless dual-token JWT strategy.
- **Access Tokens** (15-min expiry) are returned in the JSON payload of `/auth/login` and stored *in memory* by the React frontend.
- **Refresh Tokens** (7-day expiry) are returned exclusively as `HttpOnly` cookies, shielding them from XSS.
- The `frontend/src/services/api.ts` Axios interceptor automatically catches 401 Unauthorized responses and seamlessly hits `/auth/refresh` using the cookie to get a new access token.

## Where does Machine Learning happen?
The inference happens inside `backend/app/ml/model.py`. 
The actual offline training happens in `ml/scripts/train.py`, which outputs a serialized `sentinel_v1.0.0.joblib` file into `backend/app/ml/models/`. The backend loads this joblib file asynchronously into the FastAPI `app.state` during startup using the ASGI lifespan context manager.

## How do I run it?
See the [README.md](README.md) for quickstart using Docker Compose.

## How do I debug it?
- **Backend Logs**: The backend uses `structlog` for structured JSON logging. Check the docker-compose logs for `sentinel.*` events.
- **Frontend State**: Install the React DevTools. The app uses Zustand for state management; you can log `useAuthStore.getState()`.
- **Database**: Connect to `localhost:5432` using `sentinel_user` and `sentinel` as the DB. Query the `predictions` table.

## What should I read next?
If you are modifying a specific area, dive into the dedicated `docs/`:
- Changing the UI? Read [docs/frontend.md](docs/frontend.md)
- Adding an API? Read [docs/backend.md](docs/backend.md)
- Retraining the ML model? Read [docs/machine-learning.md](docs/machine-learning.md)
