from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.coding.schemas import (
    CodingAttemptOut,
    CodingProblemOut,
    GenerateProblemIn,
    SubmitCodeIn,
)
from app.modules.coding.service import CodingService

router = APIRouter(prefix="/coding", tags=["Coding Assessment"])


def _to_student_view(problem) -> CodingProblemOut:
    visible = [tc for tc in problem.test_cases if not tc.get("hidden", False)]
    return CodingProblemOut(
        id=problem.id, title=problem.title, difficulty=problem.difficulty,
        statement=problem.statement, starter_code=problem.starter_code, visible_test_cases=visible,
    )


@router.post("/generate")
async def generate_problem(
    payload: GenerateProblemIn,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CodingService(db)
    problem = await service.generate_problem(payload.role_id, payload.difficulty)
    return success_envelope(_to_student_view(problem), request)


@router.post("/{problem_id}/submit")
async def submit_solution(
    problem_id: str,
    payload: SubmitCodeIn,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CodingService(db)
    attempt = await service.submit(user.id, problem_id, payload.code, payload.language)
    return success_envelope(CodingAttemptOut.model_validate(attempt), request)


@router.get("/attempts")
async def list_attempts(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CodingService(db)
    attempts = await service.list_attempts(user.id)
    return success_envelope([CodingAttemptOut.model_validate(a) for a in attempts], request)
