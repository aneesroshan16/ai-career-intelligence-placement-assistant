"""
Real signup/login is handled client-side by Supabase Auth (email/password +
Google OAuth) — the backend only verifies the resulting JWT (see
core/security.py). This router exposes:
  - GET /auth/session: confirms the current token is valid and returns identity.
"""
from fastapi import APIRouter, Depends, Request

from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/session")
async def get_session(request: Request, user: AuthenticatedUser = Depends(get_current_user)):
    return success_envelope({"id": user.id, "email": user.email, "role": user.role}, request)
