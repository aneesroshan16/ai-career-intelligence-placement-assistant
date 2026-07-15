from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.readiness.schemas import ReadinessScoreOut
from app.modules.readiness.service import ReadinessService

router = APIRouter(prefix="/readiness", tags=["Readiness Scoring"])


@router.get("/me")
async def get_my_readiness(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReadinessService(db)
    score = await service.latest(user.id)
    return success_envelope(ReadinessScoreOut.model_validate(score), request)


@router.post("/recompute")
async def recompute_readiness(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReadinessService(db)
    score = await service.recompute(user.id)
    return success_envelope(ReadinessScoreOut.model_validate(score), request)


@router.get("/me/history")
async def get_readiness_history(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReadinessService(db)
    history = await service.history(user.id)
    return success_envelope([ReadinessScoreOut.model_validate(s) for s in history], request)
