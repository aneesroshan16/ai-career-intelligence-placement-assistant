import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.aptitude.models import AptitudeAttempt, AptitudeQuestion


class AptitudeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def random_questions(self, category: str, limit: int) -> list[AptitudeQuestion]:
        stmt = (
            select(AptitudeQuestion)
            .where(AptitudeQuestion.category == category)
            .order_by(func.random())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_many(self, ids: list[str]) -> list[AptitudeQuestion]:
        stmt = select(AptitudeQuestion).where(AptitudeQuestion.id.in_([uuid.UUID(i) for i in ids]))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_attempt(self, **fields) -> AptitudeAttempt:
        attempt = AptitudeAttempt(**fields)
        self.session.add(attempt)
        await self.session.commit()
        await self.session.refresh(attempt)
        return attempt

    async def list_for_user(self, user_id: str) -> list[AptitudeAttempt]:
        stmt = (
            select(AptitudeAttempt)
            .where(AptitudeAttempt.user_id == uuid.UUID(user_id))
            .order_by(AptitudeAttempt.submitted_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
