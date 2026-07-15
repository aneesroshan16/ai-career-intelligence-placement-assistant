import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.jobs.models import Company, Job


class JobsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_company(self, name: str) -> Company:
        stmt = select(Company).where(Company.name == name)
        result = await self.session.execute(stmt)
        company = result.scalar_one_or_none()
        if company is None:
            company = Company(name=name)
            self.session.add(company)
            await self.session.commit()
            await self.session.refresh(company)
        return company

    async def create(self, **fields) -> Job:
        job = Job(**fields)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get(self, job_id: str) -> Job | None:
        stmt = select(Job).where(Job.id == uuid.UUID(job_id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all_active(self) -> list[Job]:
        stmt = select(Job).where(Job.is_active.is_(True)).options(selectinload(Job.company))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_filtered(
        self, location: str | None, job_type: str | None, experience_max: float | None, role_id: int | None
    ) -> list[Job]:
        stmt = select(Job).where(Job.is_active.is_(True)).options(selectinload(Job.company))
        if location:
            stmt = stmt.where(Job.location.ilike(f"%{location}%"))
        if job_type:
            stmt = stmt.where(Job.job_type == job_type)
        if experience_max is not None:
            stmt = stmt.where(Job.experience_min <= experience_max)
        if role_id is not None:
            stmt = stmt.where(Job.role_id == role_id)
        stmt = stmt.order_by(Job.posted_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_many_by_ids(self, job_ids: list[str]) -> list[Job]:
        stmt = (
            select(Job)
            .where(Job.id.in_([uuid.UUID(j) for j in job_ids]))
            .options(selectinload(Job.company))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_embedding_id(self, job_id: str, embedding_id: str) -> None:
        job = await self.get(job_id)
        if job:
            job.embedding_id = embedding_id
            await self.session.commit()
