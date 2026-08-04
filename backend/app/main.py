"""
Application entry point. `create_app()` is the single place that wires
together middleware, exception handlers, rate limiting, and every module
router — see ARCHITECTURE.md §2 for the module -> router mapping.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware, register_exception_handlers
from app.core.rate_limit import limiter

# Import every module's models so SQLAlchemy's mapper registry sees the full
# schema before any relationship() string-reference is resolved (Alembic's
# autogenerate and `Base.metadata.create_all` both depend on this).
from app.modules.ats import models as _ats_models  # noqa: F401
from app.modules.aptitude import models as _aptitude_models  # noqa: F401
from app.modules.coding import models as _coding_models  # noqa: F401
from app.modules.interview import models as _interview_models  # noqa: F401
from app.modules.jobs import models as _jobs_models  # noqa: F401
from app.modules.matching import models as _matching_models  # noqa: F401
from app.modules.placement import models as _placement_models  # noqa: F401
from app.modules.readiness import models as _readiness_models  # noqa: F401
from app.modules.resumes import models as _resumes_models  # noqa: F401
from app.modules.roadmap import models as _roadmap_models  # noqa: F401
from app.modules.skills import models as _skills_models  # noqa: F401
from app.modules.users import models as _users_models  # noqa: F401

from app.modules.admin.router import router as admin_router
from app.modules.analytics.router import router as analytics_router
from app.modules.aptitude.router import router as aptitude_router
from app.modules.ats.router import router as ats_router
from app.modules.auth.router import router as auth_router
from app.modules.coding.router import router as coding_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.interview.router import router as interview_router
from app.modules.jobs.router import router as jobs_router
from app.modules.matching.router import router as matching_router
from app.modules.placement.router import router as placement_router
from app.modules.readiness.router import router as readiness_router
from app.modules.resumes.router import router as resumes_router
from app.modules.roadmap.router import router as roadmap_router
from app.modules.skills.router import router as skills_router
from app.modules.users.router import router as users_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Enterprise-grade AI platform for placement readiness: resume intelligence, "
                     "skill-gap analysis, learning roadmaps, placement prediction, job matching, "
                     "and AI-based interview/coding/aptitude preparation.",
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, lambda r, e: _rate_limit_handler(r, e))
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    prefix = settings.API_V1_PREFIX
    routers = [
        auth_router, users_router, resumes_router, ats_router, skills_router,
        roadmap_router, readiness_router, placement_router, matching_router,
        jobs_router, interview_router, coding_router, aptitude_router,
        dashboard_router, admin_router, analytics_router,
    ]
    for router in routers:
        app.include_router(router, prefix=prefix)

    @app.get("/health", tags=["System"])
    async def health_check():
        return {"status": "ok", "service": settings.APP_NAME, "environment": settings.ENVIRONMENT}

    return app


def _rate_limit_handler(request, exc):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "data": None,
            "error": {"code": "RATE_LIMITED", "message": "Too many requests. Please slow down.", "details": {}},
        },
    )


app = create_app()
