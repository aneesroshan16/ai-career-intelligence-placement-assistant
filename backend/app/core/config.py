"""
Centralized application configuration.
All environment-dependent values are read here ONCE and injected via
FastAPI dependency (`get_settings`) rather than read ad-hoc across the codebase.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "AI-Powered Career Intelligence and Placement Assistant"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "local"  # local | staging | production
    DEBUG: bool = True

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/career_intel"

    # --- Supabase ---
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_JWT_SECRET: str = "change-me-in-env"
    SUPABASE_SERVICE_ROLE_KEY: str = "change-me-in-env"
    SUPABASE_STORAGE_BUCKET: str = "resumes"

    # --- Auth (local/dev fallback, bypasses Supabase JWKS verification) ---
    AUTH_MODE: str = "supabase"  # "supabase" | "dev" (dev = trust decoded claims, no signature check)
    DEV_JWT_SECRET: str = "dev-only-secret-do-not-use-in-prod"

    # --- AI Providers ---
    LLM_PROVIDER: str = "mock"  # mock | openai | gemini
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # --- Caching ---
    REDIS_URL: str | None = None  # if None, falls back to in-memory TTL cache
    CACHE_TTL_SECONDS: int = 300

    # --- Rate limiting ---
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AI_HEAVY: str = "10/minute"

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "https://your-frontend.vercel.app"]

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    # --- Storage paths (local dev fallback when Supabase Storage isn't wired) ---
    LOCAL_STORAGE_DIR: str = "./data/uploads"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
