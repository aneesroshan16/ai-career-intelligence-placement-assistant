from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.interview.schemas import (
    AnswerIn,
    InterviewSessionDetailOut,
    InterviewSessionOut,
    StartSessionIn,
)
from app.modules.interview.service import InterviewService

router = APIRouter(prefix="/interview", tags=["Interview Simulator"])


@router.post("/sessions")
async def start_session(
    payload: StartSessionIn,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = InterviewService(db)
    interview, first_question = await service.start_session(user.id, payload.mode, payload.role_id)
    return success_envelope(
        {"session": InterviewSessionOut.model_validate(interview), "first_question": first_question}, request
    )


@router.post("/sessions/{session_id}/answer")
async def submit_answer(
    session_id: str,
    payload: AnswerIn,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = InterviewService(db)
    result = await service.submit_answer(session_id, payload.answer)
    return success_envelope(result, request)


@router.post("/sessions/{session_id}/complete")
async def complete_session(
    session_id: str,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = InterviewService(db)
    interview = await service.complete_session(session_id)
    return success_envelope(InterviewSessionDetailOut.model_validate(interview), request)


@router.get("/sessions")
async def list_sessions(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = InterviewService(db)
    sessions = await service.list_for_user(user.id)
    return success_envelope([InterviewSessionOut.model_validate(s) for s in sessions], request)


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = InterviewService(db)
    interview = await service.get(session_id)
    return success_envelope(InterviewSessionDetailOut.model_validate(interview), request)
