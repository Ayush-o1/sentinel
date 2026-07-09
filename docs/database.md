# Database Schema

## Overview
SENTINEL uses PostgreSQL 15, managed via SQLAlchemy 2.0 (async) and Alembic migrations.

## Entity Relational Mapping (ERM)

### `users`
**Purpose**: Represents authenticated individuals using the platform.
- **`id`**: UUID (Primary Key).
- **`email`**: String (Unique, Indexed) - Used for authentication.
- **`hashed_password`**: String - Bcrypt hash.
- **Lifecycle**: Created via registration. If deleted, all associated `predictions` are cascade-deleted to respect user data sovereignty.

### `predictions`
**Purpose**: Stores the historical record of all ML inferences.
- **`id`**: UUID (Primary Key).
- **`user_id`**: UUID (Foreign Key to `users.id`, `ON DELETE CASCADE`, Indexed).
- **`original_text`**: Text - Preserved exactly as input.
- **`processed_text`**: Text - After NLP stripping and lemmatization (used for debugging ML behavior).
- **`verdict`**: String - `SPAM` or `HAM`.
- **`confidence`**: Decimal(5,4) - High precision probability.
- **`suspicious_tokens`**: JSONB - Stores the LIME explanation weights without needing a heavy join table.
- **`created_at`**: DateTime with Timezone (Indexed) - Used heavily by the Analytics charting queries.
- **Lifecycle**: Immutable. Predictions are created but never updated.

### `model_versions`
**Purpose**: Auditing. Tracks which version of the ML pipeline was active when a prediction occurred.
- **`id`**: UUID.
- **`version_string`**: String (e.g., "1.0.0").
- **Lifecycle**: Allows data scientists to query if older models performed better or worse on historical data.

## Why PostgreSQL?
We rely heavily on indexing (`user_id` + `created_at`) to rapidly serve the Analytics dashboard charts. Additionally, the `JSONB` data type allows us to cleanly store dynamic lists of LIME token weights (e.g., `[{"token": "free", "weight": 0.4}]`) in a queryable format without the overhead of maintaining a `prediction_tokens` join table.
