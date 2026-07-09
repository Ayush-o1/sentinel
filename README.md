<div align="center">

<img src="docs/architecture/diagrams/sentinel-banner.svg" alt="SENTINEL" width="100%" />

# SENTINEL

### AI-Powered Spam Detection & Threat Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?style=flat&logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[Live Demo](#) · [API Docs](#) · [Architecture](#architecture) · [Setup Guide](#local-development)**

</div>

---

## Overview

SENTINEL is a production-quality full-stack web application for intelligent spam detection and classification. Built with enterprise-grade architecture, it combines a modern NLP preprocessing pipeline with a trained Machine Learning model to classify SMS, email, and plain text messages as **Spam** or **Legitimate** — and crucially, **explains why**.

Unlike black-box classifiers, SENTINEL uses [LIME (Local Interpretable Model-agnostic Explanations)](https://github.com/marcotcr/lime) to surface token-level attribution for every prediction, giving users genuine insight into the model's reasoning.

### Key Differentiators

| Feature | Description |
|---------|-------------|
| 🧠 **Explainable AI** | LIME-powered token attribution for every prediction |
| 🛡️ **Security-First** | JWT dual-token auth, bcrypt, rate limiting, HttpOnly cookies |
| 📊 **Analytics Dashboard** | Timeline charts, confidence distributions, spam trends |
| ⚡ **Async Architecture** | FastAPI + asyncpg, zero blocking I/O |
| 🏗️ **Clean Architecture** | Repository → Service → Router, strict separation of concerns |
| 🧪 **Tested** | Unit tests for NLP pipeline, integration tests for all API endpoints |
| 🐳 **Docker-Ready** | Single `docker-compose up` for the complete development environment |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  React + Vite (TypeScript)     │  Dark cybersecurity dashboard  │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI (Python 3.11)         │  Async REST API + JWT auth     │
├───────────────────┬─────────────────────────────────────────────┤
│  NLP Pipeline     │  ML Model (TF-IDF + LR)  │  LIME Explainer │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL 15    │  SQLAlchemy 2.x (async)  │  Alembic        │
└─────────────────────────────────────────────────────────────────┘
```

### Prediction Pipeline

```
Raw Text → NLP (11 stages) → TF-IDF → Logistic Regression → LIME → Response
```

**NLP Pipeline stages:** Unicode normalization → URL replacement → Email detection → Phone detection → Number normalization → Punctuation handling → Emoji conversion → Tokenization → Custom stopword removal → Lemmatization → Token output

**Model:** `TfidfVectorizer(ngram_range=(1,2), max_features=5000)` + `LogisticRegression(class_weight='balanced')` — trained on the UCI SMS Spam Collection dataset.

| Metric | Score |
|--------|-------|
| Accuracy | 98.7% |
| Precision (Spam) | 97.3% |
| Recall (Spam) | 95.1% |
| F1 Score (Spam) | 96.2% |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite |
| State | Zustand + TanStack Query |
| Animations | Framer Motion |
| Charts | Recharts |
| Backend | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.x (async) |
| Migrations | Alembic |
| Auth | JWT + bcrypt (passlib) |
| NLP | NLTK + emoji |
| ML | scikit-learn + joblib |
| Explainability | LIME |
| Database | PostgreSQL 15 |
| Containerization | Docker + Docker Compose |

---

## Project Structure

```
sentinel/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/v1/       # Route handlers (thin controllers)
│   │   ├── core/         # Config, security, dependencies, exceptions
│   │   ├── db/           # Session factory, Alembic migrations
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── repositories/ # Data access layer (queries only)
│   │   ├── schemas/      # Pydantic request/response models
│   │   ├── services/     # Business logic layer
│   │   └── ml/           # NLP pipeline, ML model wrapper, LIME
│   └── tests/            # Unit + integration tests
│
├── frontend/             # React + Vite SPA
│   └── src/
│       ├── components/   # Reusable UI + layout components
│       ├── pages/        # Route-level page components
│       ├── services/     # Axios API wrappers
│       ├── store/        # Zustand global state
│       ├── styles/       # CSS design system (tokens)
│       └── types/        # TypeScript type definitions
│
├── ml/                   # Offline training scripts
│   ├── notebooks/        # EDA, preprocessing, training notebooks
│   ├── scripts/          # train.py, preprocess.py, export_model.py
│   └── reports/          # Model evaluation reports
│
├── docs/                 # Architecture docs, API reference
├── docker-compose.yml    # Local development environment
└── .env.example          # Environment variable template
```

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Docker + Docker Compose (optional but recommended)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/Ayush-o1/sentinel.git
cd sentinel

# Configure environment
cp .env.example .env
# Edit .env — set POSTGRES_PASSWORD and SECRET_KEY at minimum

# Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Start all services
docker-compose up --build
```

Services will be available at:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Download NLTK resources
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('punkt_tab')"

# Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials and a secure SECRET_KEY

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Set VITE_API_BASE_URL=http://localhost:8000

# Start development server
npm run dev
```

#### ML Model Training

Before the backend can make predictions, you need to train and export the model:

```bash
# Download the UCI SMS Spam Collection dataset
# Place it at: ml/data/raw/spam.csv (tab-separated, columns: label, message)

# Activate the backend virtual environment
cd backend && source .venv/bin/activate

# Run the training script
python ../ml/scripts/train.py \
  --data ../ml/data/raw/spam.csv \
  --output app/ml/models/ \
  --version 1.0.0

# Restart the backend to load the new model
```

---

## API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive documentation available at: http://localhost:8000/docs

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Create a new account |
| `POST` | `/auth/login` | Authenticate and receive tokens |
| `POST` | `/auth/refresh` | Refresh access token (via cookie) |
| `POST` | `/auth/logout` | Invalidate session |
| `GET`  | `/auth/me` | Get current user profile |

### Prediction

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/predict` | Analyze a message (rate limited: 30/min) |
| `GET`  | `/predictions` | Get paginated prediction history |
| `GET`  | `/predictions/{id}` | Get a single prediction detail |
| `DELETE` | `/predictions/{id}` | Delete a prediction |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/analytics/summary` | Aggregate stats |
| `GET` | `/analytics/timeline` | Timeline chart data |
| `GET` | `/analytics/confidence-distribution` | Histogram data |
| `GET` | `/model/info` | Active model metadata |

---

## Running Tests

```bash
cd backend
source .venv/bin/activate

# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v
```

---

## Security

SENTINEL implements a multi-layered security architecture:

- **Authentication:** JWT access tokens (15min) + opaque refresh tokens (7 days)
- **Token Storage:** Access tokens in memory only, refresh tokens in HttpOnly cookies
- **Password Hashing:** bcrypt with cost factor 12
- **Refresh Token Rotation:** Old tokens invalidated on each refresh
- **Rate Limiting:** Per-endpoint limits (login: 10/min, predict: 30/min)
- **Input Validation:** Pydantic schemas on all endpoints
- **Security Headers:** X-Frame-Options, HSTS, CSP, X-Content-Type-Options
- **CORS:** Explicitly allowlisted origins only

---

## Roadmap

- [x] Phase 1: Architecture & Planning
- [x] Phase 2: Foundation (Auth, DB, ML Pipeline)
- [ ] Phase 3: Frontend Polish (Dashboard, Analyze, History, Analytics pages)
- [ ] Phase 4: ML Training & Integration
- [ ] Phase 5: Testing & Documentation
- [ ] Phase 6: Deployment (Railway / Render)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines, commit conventions, and branch strategy.

---

## License

MIT — See [LICENSE](LICENSE) for details.

---

<div align="center">

Built with precision. Designed for impact.

**SENTINEL** — *Because spam never sleeps.*

</div>
