from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.dashboard.service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Student Dashboard"])


@router.get("/student")
async def get_student_dashboard(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DashboardService(db)
    data = await service.get_student_dashboard(user.id)
    return success_envelope(data, request)
