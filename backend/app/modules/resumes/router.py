from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.resumes.schemas import ResumeOut, ResumeStatusOut, ResumeSummaryOut
from app.modules.resumes.service import ResumeService

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    file_bytes = await file.read()
    resume = await service.upload_and_process(
        user_id=user.id, filename=file.filename, content_type=file.content_type or "", file_bytes=file_bytes
    )
    return success_envelope(ResumeOut.model_validate(resume), request)


@router.get("")
async def list_resumes(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    resumes = await service.list_for_user(user.id)
    return success_envelope([ResumeSummaryOut.model_validate(r) for r in resumes], request)


@router.get("/{resume_id}")
async def get_resume(
    resume_id: str,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    resume = await service.get(resume_id)
    return success_envelope(ResumeOut.model_validate(resume), request)


@router.get("/{resume_id}/status")
async def get_resume_status(
    resume_id: str,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    resume = await service.get(resume_id)
    return success_envelope(ResumeStatusOut(id=resume.id, parse_status=resume.parse_status), request)


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    await service.delete(resume_id)
    return success_envelope({"deleted": True}, request)
