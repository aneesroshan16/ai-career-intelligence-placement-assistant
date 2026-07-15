"""
Read-only aggregation across ATS, Readiness, Skill Gap, and Interview
modules for the student dashboard (Module 13). Deliberately has no models
of its own — it composes other modules' repositories.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ats.repository import ATSRepository
from app.modules.interview.repository import InterviewRepository
from app.modules.readiness.repository import ReadinessRepository
from app.modules.resumes.repository import ResumeRepository


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ats_repo = ATSRepository(session)
        self.readiness_repo = ReadinessRepository(session)
        self.interview_repo = InterviewRepository(session)
        self.resume_repo = ResumeRepository(session)

    async def get_student_dashboard(self, user_id: str) -> dict:
        resume = await self.resume_repo.get_active_for_user(user_id)

        ats_history = await self.ats_repo.history_for_resume(str(resume.id)) if resume else []
        readiness_history = await self.readiness_repo.history(user_id)
        interview_sessions = await self.interview_repo.list_for_user(user_id)

        skill_progress = {
            "total_skills": len(resume.skills) if resume else 0,
            "matched_skill_names": [s.raw_text for s in resume.skills] if resume else [],
        }

        return {
            "active_resume_id": str(resume.id) if resume else None,
            "ats_score_trend": [
                {"date": r.created_at.isoformat(), "score": r.overall_score} for r in ats_history
            ],
            "readiness_trend": [
                {"date": r.computed_at.isoformat(), "overall_score": r.overall_score} for r in readiness_history
            ],
            "skill_progress": skill_progress,
            "interview_history": [
                {
                    "id": str(s.id), "mode": s.mode, "status": s.status,
                    "score": s.score, "started_at": s.started_at.isoformat(),
                }
                for s in interview_sessions
            ],
        }
