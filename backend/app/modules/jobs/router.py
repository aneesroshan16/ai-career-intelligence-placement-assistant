from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user, require_role
from app.modules.jobs.schemas import JobCreateIn, JobOut
from app.modules.jobs.service import JobsService
from app.modules.matching.service import MatchingService
from app.modules.resumes.service import ResumeService

router = APIRouter(prefix="/jobs", tags=["Jobs & Recommendations"])


@router.get("")
async def list_jobs(
    request: Request,
    location: str | None = Query(None),
    job_type: str | None = Query(None),
    experience_max: float | None = Query(None),
    role_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = JobsService(db)
    jobs = await service.list_filtered(location, job_type, experience_max, role_id)
    return success_envelope([JobOut.model_validate(j) for j in jobs], request)


@router.get("/recommended")
async def get_recommended_jobs(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume_service = ResumeService(db)
    matching_service = MatchingService(db)
    resume = await resume_service.get_active_for_user(user.id)
    matches = await matching_service.compute(str(resume.id))
    return success_envelope(matches, request)


@router.get("/{job_id}")
async def get_job(
    job_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = JobsService(db)
    job = await service.get(job_id)
    return success_envelope(JobOut.model_validate(job), request)


@router.post("")
async def create_job(
    payload: JobCreateIn,
    request: Request,
    _: AuthenticatedUser = Depends(require_role(["admin", "placement_officer"])),
    db: AsyncSession = Depends(get_db),
):
    service = JobsService(db)
    job = await service.create(payload)
    return success_envelope(JobOut.model_validate(job), request)
