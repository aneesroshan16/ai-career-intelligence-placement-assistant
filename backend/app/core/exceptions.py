"""
Domain-level exceptions. Route/service code raises these; the central
exception handler in middleware.py maps them to the standard error envelope.
"""


class AppException(Exception):
    code: str = "APP_ERROR"
    status_code: int = 500

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppException):
    code = "NOT_FOUND"
    status_code = 404


class ValidationFailedError(AppException):
    code = "VALIDATION_FAILED"
    status_code = 422


class ResumeParseError(AppException):
    code = "RESUME_PARSE_FAILED"
    status_code = 422


class ModelNotFoundError(AppException):
    code = "ML_MODEL_NOT_FOUND"
    status_code = 500


class UnauthorizedError(AppException):
    code = "UNAUTHORIZED"
    status_code = 401


class ForbiddenError(AppException):
    code = "FORBIDDEN"
    status_code = 403


class RateLimitedError(AppException):
    code = "RATE_LIMITED"
    status_code = 429


class ExternalServiceError(AppException):
    code = "EXTERNAL_SERVICE_ERROR"
    status_code = 502
