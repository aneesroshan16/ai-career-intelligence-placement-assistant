import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.skills.models import Role, RoleSkill, SkillGapReport


class SkillsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_roles(self) -> list[Role]:
        result = await self.session.execute(select(Role).order_by(Role.name))
        return list(result.scalars().all())

    async def get_role_skills(self, role_id: int) -> list[RoleSkill]:
        stmt = (
            select(RoleSkill)
            .where(RoleSkill.role_id == role_id)
            .options(selectinload(RoleSkill.skill))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_gap_report(self, **fields) -> SkillGapReport:
        report = SkillGapReport(**fields)
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_gap_report(self, report_id: str) -> SkillGapReport | None:
        stmt = select(SkillGapReport).where(SkillGapReport.id == uuid.UUID(report_id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
