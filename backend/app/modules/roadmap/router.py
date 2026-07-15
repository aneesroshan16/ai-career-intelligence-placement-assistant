from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.roadmap.schemas import ProgressUpdateIn, RoadmapGenerateIn, RoadmapOut
from app.modules.roadmap.service import RoadmapService

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])


@router.post("/generate")
async def generate_roadmap(
    payload: RoadmapGenerateIn,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = RoadmapService(db)
    roadmap = await service.generate(str(payload.skill_gap_report_id), payload.weeks)
    return success_envelope(RoadmapOut.model_validate(roadmap), request)


@router.get("/{roadmap_id}")
async def get_roadmap(
    roadmap_id: str,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = RoadmapService(db)
    roadmap = await service.get(roadmap_id)
    return success_envelope(RoadmapOut.model_validate(roadmap), request)


@router.patch("/{roadmap_id}/progress")
async def update_progress(
    roadmap_id: str,
    payload: ProgressUpdateIn,
    request: Request,
    _: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = RoadmapService(db)
    roadmap = await service.update_progress(roadmap_id, payload.week, payload.task_index, payload.completed)
    return success_envelope(RoadmapOut.model_validate(roadmap), request)
