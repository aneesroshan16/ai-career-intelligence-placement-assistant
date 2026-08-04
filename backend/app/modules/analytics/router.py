from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, require_role
from app.modules.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics Dashboard"])


@router.get("/skill-demand")
async def skill_demand(
    request: Request,
    _: AuthenticatedUser = Depends(require_role(["admin", "placement_officer"])),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    data = await service.skill_demand()
    return success_envelope(data, request)


@router.get("/placement-trends")
async def placement_trends(
    request: Request,
    _: AuthenticatedUser = Depends(require_role(["admin", "placement_officer"])),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    data = await service.placement_trends()
    return success_envelope(data, request)
