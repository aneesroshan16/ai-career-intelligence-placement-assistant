import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.coding.models import CodingAttempt, CodingProblem


class CodingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_problem(self, **fields) -> CodingProblem:
        problem = CodingProblem(**fields)
        self.session.add(problem)
        await self.session.commit()
        await self.session.refresh(problem)
        return problem

    async def get_problem(self, problem_id: str) -> CodingProblem | None:
        stmt = select(CodingProblem).where(CodingProblem.id == uuid.UUID(problem_id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_attempt(self, **fields) -> CodingAttempt:
        attempt = CodingAttempt(**fields)
        self.session.add(attempt)
        await self.session.commit()
        await self.session.refresh(attempt)
        return attempt

    async def list_attempts_for_user(self, user_id: str) -> list[CodingAttempt]:
        stmt = (
            select(CodingAttempt)
            .where(CodingAttempt.user_id == uuid.UUID(user_id))
            .order_by(CodingAttempt.submitted_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
