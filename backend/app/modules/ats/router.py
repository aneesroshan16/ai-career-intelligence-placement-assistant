from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.ats.schemas import ATSAnalyzeIn, ATSReportOut
from app.modules.ats.service import ATSService

router = APIRouter(prefix="/ats", tags=["ATS Analyzer"])


@router.post("/analyze")
async def analyze_resume(
    payload: ATSAnalyzeIn,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ATSService(db)
    report = await service.analyze(str(payload.resume_id), payload.target_role_id)
    return success_envelope(ATSReportOut.model_validate(report), request)


@router.get("/reports/{resume_id}")
async def get_latest_report(
    resume_id: str,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ATSService(db)
    report = await service.latest(resume_id)
    if report is None:
        raise NotFoundError("No ATS report found for this resume yet.")
    return success_envelope(ATSReportOut.model_validate(report), request)


@router.get("/reports/{resume_id}/history")
async def get_report_history(
    resume_id: str,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ATSService(db)
    reports = await service.history(resume_id)
    return success_envelope([ATSReportOut.model_validate(r) for r in reports], request)
