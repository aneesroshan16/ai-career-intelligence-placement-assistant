import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.resumes.models import (
    Resume,
    ResumeCertification,
    ResumeEducation,
    ResumeProject,
    ResumeSkill,
)


class ResumeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _with_children(self):
        return (
            selectinload(Resume.skills),
            selectinload(Resume.education),
            selectinload(Resume.projects),
            selectinload(Resume.certifications),
        )

    async def create(self, user_id: str, file_url: str, file_type: str, original_filename: str) -> Resume:
        # Mark previous resumes inactive — we treat the newest upload as canonical
        # for downstream scoring (ATS, skill gap, matching) while preserving history.
        await self.session.execute(
            update(Resume).where(Resume.user_id == uuid.UUID(user_id)).values(is_active=False)
        )
        resume = Resume(
            user_id=uuid.UUID(user_id),
            file_url=file_url,
            file_type=file_type,
            original_filename=original_filename,
            parse_status="pending",
            is_active=True,
        )
        self.session.add(resume)
        await self.session.commit()
        await self.session.refresh(resume)
        return resume

    async def get_by_id(self, resume_id: str) -> Resume | None:
        stmt = select(Resume).where(Resume.id == uuid.UUID(resume_id)).options(*self._with_children())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: str) -> list[Resume]:
        stmt = (
            select(Resume)
            .where(Resume.user_id == uuid.UUID(user_id))
            .order_by(Resume.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_for_user(self, user_id: str) -> Resume | None:
        stmt = (
            select(Resume)
            .where(Resume.user_id == uuid.UUID(user_id), Resume.is_active.is_(True))
            .options(*self._with_children())
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_status(self, resume_id: str, status: str) -> None:
        await self.session.execute(
            update(Resume).where(Resume.id == uuid.UUID(resume_id)).values(parse_status=status)
        )
        await self.session.commit()

    async def persist_parsed_entities(self, resume_id: str, parsed, raw_text: str) -> None:
        rid = uuid.UUID(resume_id)
        await self.session.execute(update(Resume).where(Resume.id == rid).values(raw_text=raw_text))

        for skill in parsed.skills:
            self.session.add(ResumeSkill(resume_id=rid, raw_text=skill.raw_text))
        for edu in parsed.education:
            self.session.add(
                ResumeEducation(
                    resume_id=rid, institution=edu.institution, degree=edu.degree,
                    field_of_study=edu.field_of_study, start_year=edu.start_year,
                    end_year=edu.end_year, gpa=edu.gpa,
                )
            )
        for proj in parsed.projects:
            self.session.add(
                ResumeProject(
                    resume_id=rid, title=proj.title, description=proj.description,
                    tech_stack=proj.tech_stack, project_url=proj.project_url,
                )
            )
        for cert in parsed.certifications:
            self.session.add(ResumeCertification(resume_id=rid, title=cert.title, issuer=cert.issuer))

        await self.session.execute(update(Resume).where(Resume.id == rid).values(parse_status="completed"))
        await self.session.commit()

    async def soft_delete(self, resume_id: str) -> None:
        await self.session.execute(
            update(Resume).where(Resume.id == uuid.UUID(resume_id)).values(is_active=False)
        )
        await self.session.commit()
