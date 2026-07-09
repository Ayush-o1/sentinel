# Security Model

## Threat Model & Mitigations
SENTINEL handles potentially sensitive user communication data. As such, security is baked in at multiple layers.

## Authentication Strategy: Dual-Token JWT
SENTINEL uses a modern, stateless dual-token strategy to maximize security without requiring a heavy stateful backend (like Redis).

### 1. Access Tokens (Short-Lived)
- **Format**: JSON Web Token (JWT) signed with HS256 (`SECRET_KEY`).
- **Lifespan**: 15 minutes.
- **Storage**: Stored entirely in JavaScript memory (React state/variables).
- **Why**: They are completely immune to Cross-Site Request Forgery (CSRF). Because they are never placed in `localStorage`, they are highly resistant to Cross-Site Scripting (XSS) exfiltration.

### 2. Refresh Tokens (Long-Lived)
- **Format**: JWT signed with HS256.
- **Lifespan**: 7 days.
- **Storage**: Stored as an `HttpOnly`, `Secure`, `SameSite=Strict` cookie.
- **Why**: The `HttpOnly` flag makes the token 100% invisible to JavaScript. An attacker successfully executing an XSS attack cannot steal the refresh token. The backend `/auth/refresh` endpoint blindly accepts this cookie to mint a fresh Access Token when the frontend needs one.

## API Hardening
- **Password Hashing**: Passwords are never stored in plaintext. They are hashed using `bcrypt` via the `passlib` library before touching the database.
- **Rate Limiting**: `slowapi` enforces strict IP-based and User-based rate limits (e.g., 5 registrations per minute, 30 predictions per minute) to prevent brute-force and Denial of Wallet (DoW) attacks.
- **CORS Configuration**: The `CORSMiddleware` strictly whitelists origins defined in the `CORS_ORIGINS` environment variable.
- **Host Validation**: `TrustedHostMiddleware` is enabled in production to prevent HTTP Host header attacks.

## Database Security
- **No Raw SQL**: Every database query utilizes SQLAlchemy 2.0 ORM constructs. This ensures robust parameterization, rendering SQL Injection practically impossible.
- **UUIDs**: All database primary keys are UUIDv4s, not auto-incrementing integers. This prevents Insecure Direct Object Reference (IDOR) attacks where an attacker might guess sequential IDs.
