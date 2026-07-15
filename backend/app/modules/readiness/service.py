"""
Composite placement-readiness score. Pulls the latest available signal from
each contributing module and combines them with fixed weights; any
component missing (e.g. student hasn't attempted a coding test yet) is
excluded and the remaining weights are renormalized, so the score is always
computable from partial data.
"""
from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ats.models import ATSReport
from app.modules.aptitude.models import AptitudeAttempt
from app.modules.coding.models import CodingAttempt
from app.modules.interview.models import InterviewSession
from app.modules.readiness.models import ReadinessScore
from app.modules.readiness.repository import ReadinessRepository
from app.modules.resumes.models import Resume

_WEIGHTS = {
    "technical_score": 0.30,
    "aptitude_score": 0.20,
    "communication_score": 0.20,
    "interview_score": 0.30,
}


class ReadinessService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ReadinessRepository(session)

    async def _avg_coding_score(self, user_id: str) -> float | None:
        stmt = select(func.avg(CodingAttempt.score)).where(CodingAttempt.user_id == uuid.UUID(user_id))
        return (await self.session.execute(stmt)).scalar()

    async def _latest_ats_score(self, user_id: str) -> float | None:
        stmt = (
            select(ATSReport.overall_score)
            .join(Resume, Resume.id == ATSReport.resume_id)
            .where(Resume.user_id == uuid.UUID(user_id))
            .order_by(ATSReport.created_at.desc())
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalar()

    async def _latest_aptitude_score(self, user_id: str) -> float | None:
        stmt = (
            select(AptitudeAttempt.overall_score)
            .where(AptitudeAttempt.user_id == uuid.UUID(user_id))
            .order_by(AptitudeAttempt.submitted_at.desc())
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalar()

    async def _avg_interview_score(self, user_id: str, mode: str | None = None) -> float | None:
        stmt = select(func.avg(InterviewSession.score)).where(
            InterviewSession.user_id == uuid.UUID(user_id), InterviewSession.status == "completed"
        )
        if mode:
            stmt = stmt.where(InterviewSession.mode == mode)
        return (await self.session.execute(stmt)).scalar()

    async def recompute(self, user_id: str) -> ReadinessScore:
        coding_score = await self._avg_coding_score(user_id)
        ats_score = await self._latest_ats_score(user_id)
        # Technical readiness blends hands-on coding performance with resume/ATS strength.
        technical_components = [s for s in [coding_score, ats_score] if s is not None]
        technical_score = round(sum(technical_components) / len(technical_components), 2) if technical_components else None

        aptitude_score = await self._latest_aptitude_score(user_id)
        aptitude_score = round(float(aptitude_score), 2) if aptitude_score is not None else None

        # Communication readiness derived from HR-mode interview performance specifically.
        communication_score = await self._avg_interview_score(user_id, mode="hr")
        communication_score = round(float(communication_score), 2) if communication_score is not None else None

        interview_score = await self._avg_interview_score(user_id)
        interview_score = round(float(interview_score), 2) if interview_score is not None else None

        components = {
            "technical_score": technical_score,
            "aptitude_score": aptitude_score,
            "communication_score": communication_score,
            "interview_score": interview_score,
        }
        available = {k: v for k, v in components.items() if v is not None}
        if available:
            weight_sum = sum(_WEIGHTS[k] for k in available)
            overall_score = round(sum(_WEIGHTS[k] * v for k, v in available.items()) / weight_sum, 2)
        else:
            overall_score = 0.0

        return await self.repo.create(user_id=uuid.UUID(user_id), overall_score=overall_score, **components)

    async def latest(self, user_id: str) -> ReadinessScore:
        score = await self.repo.latest(user_id)
        if score is None:
            score = await self.recompute(user_id)
        return score

    async def history(self, user_id: str) -> list[ReadinessScore]:
        return await self.repo.history(user_id)
