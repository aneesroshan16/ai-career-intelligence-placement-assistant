from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_core.embeddings.sentence_transformer_provider import get_embedding_provider
from app.ai_core.vector_store.faiss_store import get_faiss_store
from app.core.exceptions import NotFoundError
from app.modules.jobs.models import Job
from app.modules.jobs.repository import JobsRepository


def _job_embedding_text(title: str, description: str | None, required_skills: list[str]) -> str:
    return f"{title}. Required skills: {', '.join(required_skills)}. {description or ''}"


class JobsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = JobsRepository(session)
        self.embedder = get_embedding_provider()
        self.job_store = get_faiss_store("jobs")

    async def create(self, payload) -> Job:
        company = await self.repo.get_or_create_company(payload.company_name)
        job = await self.repo.create(
            company_id=company.id,
            title=payload.title,
            role_id=payload.role_id,
            description=payload.description,
            required_skills=payload.required_skills,
            experience_min=payload.experience_min,
            experience_max=payload.experience_max,
            location=payload.location,
            job_type=payload.job_type,
        )
        # Index immediately so the job is discoverable via matching right away.
        text = _job_embedding_text(job.title, job.description, payload.required_skills)
        vector = self.embedder.embed([text])[0]
        row_id = self.job_store.add(str(job.id), vector)
        await self.repo.set_embedding_id(str(job.id), str(row_id))
        return job

    async def get(self, job_id: str) -> Job:
        job = await self.repo.get(job_id)
        if job is None:
            raise NotFoundError("Job not found")
        return job

    async def list_filtered(self, location, job_type, experience_max, role_id) -> list[Job]:
        return await self.repo.list_filtered(location, job_type, experience_max, role_id)
