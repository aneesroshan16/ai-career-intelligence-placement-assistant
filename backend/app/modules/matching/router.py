from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.matching.schemas import ComputeMatchIn
from app.modules.matching.service import MatchingService

router = APIRouter(prefix="/matching", tags=["Job Matching"])


@router.post("/compute")
async def compute_matches(
    payload: ComputeMatchIn,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MatchingService(db)
    matches = await service.compute(str(payload.resume_id))
    return success_envelope(matches, request)


@router.get("/{resume_id}")
async def get_matches(
    resume_id: str,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MatchingService(db)
    matches = await service.get_saved_matches(resume_id)
    return success_envelope(matches, request)
