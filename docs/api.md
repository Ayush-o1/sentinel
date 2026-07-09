# REST API Reference

The SENTINEL API is built with FastAPI and follows RESTful conventions. 
Full OpenAPI / Swagger documentation is generated automatically and is available at `http://localhost:8000/docs` when the backend is running.

## Authentication

All protected routes require a Bearer token in the `Authorization` header:
`Authorization: Bearer <access_token>`

## Endpoints

### Auth

#### `POST /api/v1/auth/register`
Creates a new user.
- **Payload**: `{ "email": "user@example.com", "password": "StrongPassword1!", "full_name": "Test User" }`
- **Response**: `201 Created` returning the serialized user object (without password hash).

#### `POST /api/v1/auth/login`
Authenticates a user and issues dual tokens.
- **Payload**: `{ "email": "user@example.com", "password": "StrongPassword1!" }`
- **Response**: `200 OK` returning `{ "access_token": "...", "token_type": "bearer" }`. 
- **Headers**: Sets the `refresh_token` as an `HttpOnly` cookie.

#### `POST /api/v1/auth/refresh`
Mints a new access token using a valid refresh token cookie.
- **Requires**: A valid `refresh_token` HttpOnly cookie.
- **Response**: `200 OK` returning `{ "access_token": "...", "token_type": "bearer" }`.

#### `POST /api/v1/auth/logout`
Invalidates the session.
- **Response**: `200 OK`.
- **Headers**: Clears the `refresh_token` cookie.

#### `GET /api/v1/auth/me`
Retrieves the currently authenticated user profile.
- **Requires**: Bearer Token.

---

### Predictions

#### `POST /api/v1/predict`
Analyzes a message using the ML pipeline and stores the result.
- **Requires**: Bearer Token.
- **Payload**: `{ "text": "Win free cash now!", "message_type": "sms" }`
- **Response**: `200 OK`
```json
{
  "id": "uuid",
  "verdict": "SPAM",
  "confidence": 0.9521,
  "risk_level": "HIGH",
  "explanation": "This message exhibits strong characteristics of spam...",
  "suspicious_tokens": [
    {"token": "free", "weight": 0.45},
    {"token": "cash", "weight": 0.32}
  ]
}
```

#### `GET /api/v1/predictions`
Fetches a paginated history of the user's predictions.
- **Requires**: Bearer Token.
- **Query Params**: `skip` (default 0), `limit` (default 100).
- **Response**: `200 OK`
```json
{
  "items": [ { ...prediction object... } ],
  "total": 1
}
```

#### `GET /api/v1/analytics/summary`
Fetches aggregated statistics for the Analytics dashboard summary metrics.
- **Requires**: Bearer Token.
- **Response**: `200 OK` containing total counts, average confidence, spam vs ham ratios, and top spam tokens.

#### `GET /api/v1/analytics/timeline`
Fetches timeline data for prediction volume over a specified period.
- **Requires**: Bearer Token.
- **Query Params**: `period` (default "30d", accepts "7d", "30d", "90d").
- **Response**: `200 OK` containing daily totals of spam and ham.

#### `GET /api/v1/analytics/confidence-distribution`
Fetches confidence score distribution for histogram generation.
- **Requires**: Bearer Token.
- **Response**: `200 OK` containing histogram buckets for prediction confidence.
