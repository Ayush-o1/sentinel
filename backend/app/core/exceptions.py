"""
SENTINEL — Custom Exception Classes & Handlers

Defines the exception hierarchy for the application and registers
FastAPI exception handlers that return consistent JSON error responses.

Design:
    All application exceptions inherit from SentinelBaseException.
    This makes it trivial to add new exception types and ensures
    that all errors follow the same response envelope format.

Response envelope:
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable message",
            "details": {}   # Optional — only in development
        }
    }
"""

from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Exception Hierarchy
# ---------------------------------------------------------------------------

class SentinelBaseException(Exception):
    """Base class for all SENTINEL application exceptions."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(SentinelBaseException):
    """Raised when authentication fails (invalid token, wrong password, etc.)."""

    def __init__(self, message: str = "Authentication failed.") -> None:
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationError(SentinelBaseException):
    """Raised when the user lacks permission to perform an action."""

    def __init__(self, message: str = "You do not have permission to perform this action.") -> None:
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundError(SentinelBaseException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, identifier: str | None = None) -> None:
        message = f"{resource} not found."
        if identifier:
            message = f"{resource} '{identifier}' not found."
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConflictError(SentinelBaseException):
    """Raised when a resource already exists (e.g., duplicate email)."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
        )


class ValidationError(SentinelBaseException):
    """Raised for domain-level validation failures (distinct from Pydantic validation)."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class MLInferenceError(SentinelBaseException):
    """Raised when the ML model fails to produce a prediction."""

    def __init__(self, message: str = "Prediction failed. Please try again.") -> None:
        super().__init__(
            message=message,
            code="ML_INFERENCE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ---------------------------------------------------------------------------
# Response Builder
# ---------------------------------------------------------------------------

def _error_response(
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """Build a standardized JSON error response."""
    content: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
        }
    }
    if details:
        content["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=content)


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------

def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI application."""

    @app.exception_handler(SentinelBaseException)
    async def sentinel_exception_handler(
        request: Request,
        exc: SentinelBaseException,
    ) -> JSONResponse:
        logger.warning(
            "sentinel.exception",
            code=exc.code,
            message=exc.message,
            path=request.url.path,
        )
        return _error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors from request body/query parsing.
        Returns a clean, field-level error breakdown instead of the default 422 body.
        """
        field_errors: dict[str, list[str]] = {}
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
            field_errors.setdefault(field, []).append(error["msg"])

        logger.info("sentinel.validation_error", path=request.url.path, errors=field_errors)
        return _error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message="Request validation failed. Check the 'details' field for per-field errors.",
            details=field_errors,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Catch-all for unexpected exceptions. Logs the full traceback."""
        logger.exception(
            "sentinel.unhandled_exception",
            path=request.url.path,
            exception=str(exc),
        )
        return _error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred. Please try again later.",
        )
