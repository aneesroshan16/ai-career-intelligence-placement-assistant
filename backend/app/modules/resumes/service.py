from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_core.resume_parser.extractor import extract_text
from app.ai_core.resume_parser.ner_pipeline import ResumeParser
from app.core.exceptions import NotFoundError, ResumeParseError
from app.core.storage import get_storage_provider
from app.modules.resumes.models import Resume
from app.modules.resumes.repository import ResumeRepository
from app.modules.skills.models import SkillMaster

_ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


class ResumeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ResumeRepository(session)
        self.storage = get_storage_provider()
        self.parser = ResumeParser()

    async def _known_skills(self) -> list[str]:
        result = await self.session.execute(select(SkillMaster.name))
        names = [row[0] for row in result.all()]
        return names or None  # falls back to the parser's built-in gazetteer if DB is unseeded

    async def upload_and_process(self, user_id: str, filename: str, content_type: str, file_bytes: bytes) -> Resume:
        file_type = _ALLOWED_TYPES.get(content_type)
        if file_type is None:
            # also allow inference by extension for clients that send generic content-types
            if filename.lower().endswith(".pdf"):
                file_type = "pdf"
            elif filename.lower().endswith(".docx"):
                file_type = "docx"
            else:
                raise ResumeParseError("Only PDF and DOCX resumes are supported.")

        stored_path = await self.storage.upload(file_bytes, filename, content_type)
        file_url = self.storage.get_url(stored_path)

        resume = await self.repo.create(
            user_id=user_id, file_url=file_url, file_type=file_type, original_filename=filename
        )

        await self.repo.set_status(str(resume.id), "processing")
        try:
            raw_text = extract_text(file_bytes, file_type)
            known_skills = await self._known_skills()
            parsed = self.parser.parse(raw_text, known_skills=known_skills)
            await self.repo.persist_parsed_entities(str(resume.id), parsed, raw_text)
        except ResumeParseError:
            await self.repo.set_status(str(resume.id), "failed")
            raise

        return await self.repo.get_by_id(str(resume.id))

    async def get(self, resume_id: str) -> Resume:
        resume = await self.repo.get_by_id(resume_id)
        if resume is None:
            raise NotFoundError("Resume not found")
        return resume

    async def list_for_user(self, user_id: str) -> list[Resume]:
        return await self.repo.list_by_user(user_id)

    async def get_active_for_user(self, user_id: str) -> Resume:
        resume = await self.repo.get_active_for_user(user_id)
        if resume is None:
            raise NotFoundError("No active resume found. Upload a resume first.")
        return resume

    async def delete(self, resume_id: str) -> None:
        await self.repo.soft_delete(resume_id)
