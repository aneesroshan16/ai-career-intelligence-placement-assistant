import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.roadmap.models import Roadmap


class RoadmapRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **fields) -> Roadmap:
        roadmap = Roadmap(**fields)
        self.session.add(roadmap)
        await self.session.commit()
        await self.session.refresh(roadmap)
        return roadmap

    async def get(self, roadmap_id: str) -> Roadmap | None:
        stmt = select(Roadmap).where(Roadmap.id == uuid.UUID(roadmap_id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_plan(self, roadmap_id: str, plan: list[dict]) -> None:
        await self.session.execute(
            update(Roadmap).where(Roadmap.id == uuid.UUID(roadmap_id)).values(plan=plan)
        )
        await self.session.commit()
