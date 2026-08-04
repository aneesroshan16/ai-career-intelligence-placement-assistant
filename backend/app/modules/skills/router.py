from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.skills.schemas import GapAnalysisIn, RoleOut, SkillGapReportOut
from app.modules.skills.service import SkillsService

router = APIRouter(prefix="/skills", tags=["Skill Gap"])


@router.get("/roles")
async def list_roles(request: Request, db: AsyncSession = Depends(get_db)):
    service = SkillsService(db)
    roles = await service.list_roles()
    return success_envelope([RoleOut.model_validate(r, from_attributes=True) for r in roles], request)


@router.post("/gap-analysis")
async def gap_analysis(
    payload: GapAnalysisIn,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SkillsService(db)
    report = await service.analyze_gap(str(payload.resume_id), payload.role_id)
    return success_envelope(SkillGapReportOut.model_validate(report), request)


@router.get("/gap-analysis/{report_id}")
async def get_gap_report(
    report_id: str,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SkillsService(db)
    report = await service.get_report(report_id)
    return success_envelope(SkillGapReportOut.model_validate(report), request)
