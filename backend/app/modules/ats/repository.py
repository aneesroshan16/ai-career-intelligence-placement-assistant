import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ats.models import ATSReport


class ATSRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **fields) -> ATSReport:
        report = ATSReport(**fields)
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def latest_for_resume(self, resume_id: str) -> ATSReport | None:
        stmt = (
            select(ATSReport)
            .where(ATSReport.resume_id == uuid.UUID(resume_id))
            .order_by(ATSReport.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def history_for_resume(self, resume_id: str) -> list[ATSReport]:
        stmt = (
            select(ATSReport)
            .where(ATSReport.resume_id == uuid.UUID(resume_id))
            .order_by(ATSReport.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
