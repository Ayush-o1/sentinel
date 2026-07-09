# Deployment Guide

SENTINEL is built with cloud-native deployment in mind. The fastest way to deploy the application is via Docker.

## Docker Deployment (Production)

The repository includes a multi-stage `Dockerfile` for both the frontend and the backend.
In a production environment, you should build the images and run them behind a reverse proxy (e.g., Nginx, Traefik, or an AWS Application Load Balancer).

### Environment Variables
Before deploying, create a `.env` file containing robust secrets:
```env
APP_ENV=production
SECRET_KEY=<generate_secure_random_string>
POSTGRES_USER=production_user
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=sentinel_prod
VITE_API_BASE_URL=https://api.yourdomain.com
```

### Database Initialization
The backend container is configured to automatically run `alembic upgrade head` before starting the Uvicorn ASGI server. This guarantees that your PostgreSQL schema is always perfectly aligned with the deployed codebase version. 

### Model Loading
The trained machine learning model (`sentinel_v1.0.0.joblib`) is committed to the repository and copied directly into the Docker image during the build step. It is loaded natively into the FastAPI application state at startup.

## Common Deployment Issues
- **`500 Internal Server Error` on Predict**: This usually indicates the `.joblib` model file is missing from `app/ml/models/`. Ensure it was correctly copied into the container during the build stage.
- **`401 Unauthorized` Loop**: If the frontend continuously redirects to `/login` despite successful authentication, ensure your `CORS_ORIGINS` environment variable in the backend matches the exact URL of your deployed frontend. Additionally, ensure your frontend is served over HTTPS; otherwise, the `Secure` flag on the `HttpOnly` refresh cookie will cause browsers to reject it.
- **Database Connection Refused**: Ensure the backend container's `POSTGRES_HOST` points to the correct Docker Compose service name (`db`) or the managed database's endpoint (e.g., AWS RDS).
