"""
Per-user rate limiting via slowapi. General endpoints get a generous quota;
AI-heavy endpoints (interview, coding generation, roadmap generation) are
throttled more tightly since they're the most expensive to serve.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.core.config import get_settings

settings = get_settings()


def _rate_limit_key(request: Request) -> str:
    """Key by authenticated user id when present, else fall back to IP."""
    user = getattr(request.state, "user", None)
    if user is not None:
        return f"user:{user.id}"
    return get_remote_address(request)


limiter = Limiter(key_func=_rate_limit_key, default_limits=[settings.RATE_LIMIT_DEFAULT])

# Import and apply as: @limiter.limit(settings.RATE_LIMIT_AI_HEAVY) on specific routes.
