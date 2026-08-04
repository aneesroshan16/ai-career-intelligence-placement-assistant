"""
Cross-cutting middleware: request-id tagging + centralized exception handling
that maps every error (domain or unhandled) to the standard response envelope
documented in ARCHITECTURE.md §6.13.
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import AppException

logger = structlog.get_logger()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attaches a request_id, times the request, and logs structured access lines."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()

        response = await call_next(request)

        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            latency_ms=latency_ms,
        )
        return response


def _envelope(success: bool, data=None, error=None, request_id: str = "") -> dict:
    return {
        "success": success,
        "data": data,
        "meta": {"request_id": request_id, "timestamp": datetime.now(timezone.utc).isoformat()},
        "error": error,
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException):
        request_id = getattr(request.state, "request_id", "")
        logger.warning("app_exception", code=exc.code, message=exc.message, request_id=request_id)
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(
                success=False,
                error={"code": exc.code, "message": exc.message, "details": exc.details},
                request_id=request_id,
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "")
        logger.error("unhandled_exception", error=str(exc), request_id=request_id, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_envelope(
                success=False,
                error={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred.", "details": {}},
                request_id=request_id,
            ),
        )


def success_envelope(data, request: Request) -> dict:
    """Helper routers can use to wrap successful payloads consistently."""
    request_id = getattr(request.state, "request_id", "")
    return _envelope(success=True, data=data, request_id=request_id)
