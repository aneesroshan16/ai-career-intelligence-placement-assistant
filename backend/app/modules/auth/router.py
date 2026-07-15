"""
Real signup/login is handled client-side by Supabase Auth (email/password +
Google OAuth) — the backend only verifies the resulting JWT (see
core/security.py). This router exposes:
  - GET /auth/session: confirms the current token is valid and returns identity.
  - POST /auth/dev-token: (AUTH_MODE=dev only) issues a locally-signed test JWT
    so the whole API can be exercised without a live Supabase project during
    early development.
"""
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.exceptions import ForbiddenError
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()


@router.get("/session")
async def get_session(request: Request, user: AuthenticatedUser = Depends(get_current_user)):
    return success_envelope({"id": user.id, "email": user.email, "role": user.role}, request)


class DevTokenRequest(BaseModel):
    user_id: str
    email: str
    role: str = "student"


@router.post("/dev-token")
async def issue_dev_token(payload: DevTokenRequest, request: Request):
    """Local-development-only helper. Disabled unless AUTH_MODE=dev."""
    if settings.AUTH_MODE != "dev":
        raise ForbiddenError("Dev token issuance is disabled outside AUTH_MODE=dev")

    import jwt

    token = jwt.encode(
        {"sub": payload.user_id, "email": payload.email, "role": payload.role},
        settings.DEV_JWT_SECRET,
        algorithm="HS256",
    )
    return success_envelope({"access_token": token, "token_type": "bearer"}, request)
