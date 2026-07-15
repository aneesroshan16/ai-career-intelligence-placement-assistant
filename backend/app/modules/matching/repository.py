import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.matching.models import JobMatch


class MatchingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_match(self, resume_id: str, job_id: str, similarity_score: float) -> None:
        stmt = (
            pg_insert(JobMatch)
            .values(resume_id=uuid.UUID(resume_id), job_id=uuid.UUID(job_id), similarity_score=similarity_score)
            .on_conflict_do_update(
                index_elements=["resume_id", "job_id"],
                set_={"similarity_score": similarity_score},
            )
        )
        await self.session.execute(stmt)

    async def commit(self) -> None:
        await self.session.commit()

    async def list_for_resume(self, resume_id: str) -> list[JobMatch]:
        stmt = (
            select(JobMatch)
            .where(JobMatch.resume_id == uuid.UUID(resume_id))
            .order_by(JobMatch.similarity_score.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
