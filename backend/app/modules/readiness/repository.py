import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.readiness.models import ReadinessScore


class ReadinessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **fields) -> ReadinessScore:
        score = ReadinessScore(**fields)
        self.session.add(score)
        await self.session.commit()
        await self.session.refresh(score)
        return score

    async def latest(self, user_id: str) -> ReadinessScore | None:
        stmt = (
            select(ReadinessScore)
            .where(ReadinessScore.user_id == uuid.UUID(user_id))
            .order_by(ReadinessScore.computed_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def history(self, user_id: str) -> list[ReadinessScore]:
        stmt = (
            select(ReadinessScore)
            .where(ReadinessScore.user_id == uuid.UUID(user_id))
            .order_by(ReadinessScore.computed_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
