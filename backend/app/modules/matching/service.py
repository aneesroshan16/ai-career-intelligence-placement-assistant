from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_core.embeddings.sentence_transformer_provider import get_embedding_provider
from app.ai_core.vector_store.faiss_store import get_faiss_store
from app.core.exceptions import NotFoundError
from app.modules.jobs.repository import JobsRepository
from app.modules.matching.repository import MatchingRepository
from app.modules.resumes.repository import ResumeRepository


def _resume_embedding_text(resume) -> str:
    skills = ", ".join(s.raw_text for s in resume.skills)
    projects = " ".join(p.title + " " + (p.description or "") for p in resume.projects)
    return f"Skills: {skills}. Projects: {projects}. {resume.raw_text or ''}"[:5000]


class MatchingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = MatchingRepository(session)
        self.resume_repo = ResumeRepository(session)
        self.jobs_repo = JobsRepository(session)
        self.embedder = get_embedding_provider()
        self.resume_store = get_faiss_store("resumes")
        self.job_store = get_faiss_store("jobs")

    async def compute(self, resume_id: str, top_k: int = 15) -> list[dict]:
        resume = await self.resume_repo.get_by_id(resume_id)
        if resume is None:
            raise NotFoundError("Resume not found")

        text = _resume_embedding_text(resume)
        vector = self.embedder.embed([text])[0]
        row_id = self.resume_store.add(str(resume.id), vector)
        resume.embedding_id = str(row_id)

        matches = self.job_store.search(vector, top_k=top_k)  # [(job_id, score), ...]
        for job_id, score in matches:
            await self.repo.upsert_match(str(resume.id), job_id, similarity_score=score)
        await self.repo.commit()

        return await self._enrich(matches)

    async def _enrich(self, matches: list[tuple[str, float]]) -> list[dict]:
        if not matches:
            return []
        jobs = await self.jobs_repo.get_many_by_ids([m[0] for m in matches])
        job_map = {str(j.id): j for j in jobs}
        enriched = []
        for job_id, score in matches:
            job = job_map.get(job_id)
            if job is None:
                continue
            enriched.append({
                "job_id": job.id,
                "title": job.title,
                "company_name": job.company.name if job.company else None,
                "location": job.location,
                "job_type": job.job_type,
                "similarity_score": round(score, 4),
            })
        return enriched

    async def get_saved_matches(self, resume_id: str) -> list[dict]:
        matches = await self.repo.list_for_resume(resume_id)
        pairs = [(str(m.job_id), m.similarity_score) for m in matches]
        return await self._enrich(pairs)
