from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, require_role
from app.modules.admin.service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


@router.get("/analytics/department")
async def department_analytics(
    request: Request,
    _: AuthenticatedUser = Depends(require_role(["admin", "placement_officer"])),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    data = await service.department_analytics()
    return success_envelope(data, request)


@router.get("/analytics/export")
async def export_analytics(
    format: str = Query("csv", pattern="^(csv|pdf)$"),
    _: AuthenticatedUser = Depends(require_role(["admin", "placement_officer"])),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    if format == "pdf":
        # PDF export intentionally deferred to a follow-up iteration (reuses
        # the `pdf` generation skill/tooling); CSV covers the same data today.
        csv_data = await service.export_department_analytics_csv()
        return StreamingResponse(
            iter([csv_data]), media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=department_analytics.csv"},
        )
    csv_data = await service.export_department_analytics_csv()
    return StreamingResponse(
        iter([csv_data]), media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=department_analytics.csv"},
    )
