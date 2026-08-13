"""
Authentication & authorization.

Identity is issued by Supabase Auth on the frontend. This module verifies the
resulting JWT on every request and lazily provisions a local `users` row
(see modules/users/service.py) — the backend never issues its own passwords.

Two verification modes:
  - "supabase": verifies signature against Supabase's JWKS endpoint (production).
  - "dev": decodes without signature verification, for local development
           without a live Supabase project. NEVER used when ENVIRONMENT=production.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=False)

_jwks_cache: dict = {"keys": None, "fetched_at": 0.0}
_JWKS_TTL_SECONDS = 3600


@dataclass
class AuthenticatedUser:
    id: str
    email: str
    role: str = "student"  # overwritten from DB after lookup in get_current_user


async def _get_jwks() -> dict:
    now = time.time()
    if _jwks_cache["keys"] is None or (now - _jwks_cache["fetched_at"]) > _JWKS_TTL_SECONDS:
        jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(jwks_url)
            resp.raise_for_status()
            _jwks_cache["keys"] = resp.json()
            _jwks_cache["fetched_at"] = now
    return _jwks_cache["keys"]


async def _decode_supabase_jwt(token: str) -> dict:
    try:
        header = jwt.get_unverified_header(token)
        if header.get("alg") == "HS256":
            return jwt.decode(
                token, 
                settings.SUPABASE_JWT_SECRET, 
                algorithms=["HS256"], 
                audience="authenticated", 
                options={"verify_aud": True},
                leeway=60
            )
            
        jwks = await _get_jwks()
        key = next((k for k in jwks["keys"] if k.get("kid") == header.get("kid")), None)
        if key is None:
            print(f"JWT Error: Unknown signing key. Header: {header}")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unknown signing key")
        
        public_key = jwt.PyJWK(key).key
        alg = header.get("alg", "RS256")
        payload = jwt.decode(
            token, public_key, algorithms=[alg],
            audience="authenticated", options={"verify_aud": True},
            leeway=60
        )
        return payload
    except jwt.PyJWTError as exc:
        print(f"JWT Decode Error: {exc}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid token: {exc}") from exc


async def get_current_claims(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    token = credentials.credentials
    return await _decode_supabase_jwt(token)


async def get_current_user(request: Request, claims: dict = Depends(get_current_claims)) -> AuthenticatedUser:
    """
    Resolves JWT claims into an AuthenticatedUser, then enriches with the
    backend-owned `role` field from the `users` table (lazily provisioned
    on first sight — see UserService.get_or_create_from_claims).
    """
    from app.core.database import AsyncSessionLocal  # local import avoids circular import
    from app.modules.users.service import UserService

    user_id = claims.get("sub")
    email = claims.get("email", "")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token missing subject claim")

    async with AsyncSessionLocal() as session:
        service = UserService(session)
        db_user = await service.get_or_create_from_claims(user_id=user_id, email=email)

    user = AuthenticatedUser(id=str(db_user.id), email=db_user.email, role=db_user.role)
    request.state.user = user
    return user


def require_role(allowed_roles: list[str]):
    """FastAPI dependency factory for RBAC: `Depends(require_role(["admin"]))`."""

    async def _guard(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Role '{user.role}' is not permitted to access this resource",
            )
        return user

    return _guard
