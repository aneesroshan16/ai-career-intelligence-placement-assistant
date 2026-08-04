import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.placement.models import PlacementPrediction


class PlacementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **fields) -> PlacementPrediction:
        prediction = PlacementPrediction(**fields)
        self.session.add(prediction)
        await self.session.commit()
        await self.session.refresh(prediction)
        return prediction

    async def history(self, user_id: str) -> list[PlacementPrediction]:
        stmt = (
            select(PlacementPrediction)
            .where(PlacementPrediction.user_id == uuid.UUID(user_id))
            .order_by(PlacementPrediction.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
