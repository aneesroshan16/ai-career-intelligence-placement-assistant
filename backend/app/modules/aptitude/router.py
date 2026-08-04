from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.aptitude.schemas import (
    AptitudeAttemptOut,
    AptitudeQuestionOut,
    AptitudeResultOut,
    SubmitAptitudeIn,
)
from app.modules.aptitude.service import AptitudeService

router = APIRouter(prefix="/aptitude", tags=["Aptitude Assessment"])


@router.get("/test")
async def get_test(
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AptitudeService(db)
    questions = await service.get_test()
    # correct_option is intentionally omitted from the response payload.
    payload = [
        AptitudeQuestionOut(id=q.id, category=q.category, question=q.question, options=q.options, difficulty=q.difficulty)
        for q in questions
    ]
    return success_envelope(payload, request)


@router.post("/submit")
async def submit_test(
    payload: SubmitAptitudeIn,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AptitudeService(db)
    result = await service.submit(user.id, payload.answers)
    return success_envelope(AptitudeResultOut(**result), request)


@router.get("/attempts")
async def list_attempts(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AptitudeService(db)
    attempts = await service.list_attempts(user.id)
    return success_envelope([AptitudeAttemptOut.model_validate(a) for a in attempts], request)
