"""
ATS Resume Analyzer.

Scoring is entirely rule-based/deterministic (no LLM dependency for the
scores themselves — ATS score reproducibility matters for the dashboard
trend chart). Only the qualitative *suggestions* go through the LLM
provider (mock by default), since natural-language advice benefits from
generation while numeric scoring should not be non-deterministic.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_core.llm.base import LLMMessage
from app.ai_core.llm.factory import get_llm_provider
from app.modules.ats.models import ATSReport
from app.modules.ats.repository import ATSRepository
from app.modules.ats.schemas import ATSSuggestionSet
from app.modules.resumes.repository import ResumeRepository
from app.modules.skills.models import RoleSkill

_STANDARD_SECTIONS = ["education", "skills", "projects", "experience", "certifications"]
_SECTION_KEYWORDS = {
    "education": ["education", "academic"],
    "skills": ["skills", "technical skills"],
    "projects": ["projects"],
    "experience": ["experience", "work experience", "internship"],
    "certifications": ["certifications", "certificates"],
}


class ATSService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ATSRepository(session)
        self.resume_repo = ResumeRepository(session)
        self.llm = get_llm_provider()

    def _formatting_score(self, raw_text: str) -> float:
        if not raw_text:
            return 0.0
        lines = [l for l in raw_text.split("\n") if l.strip()]
        bullet_lines = sum(1 for l in lines if l.strip().startswith(("-", "•", "*")))
        avg_line_len = sum(len(l) for l in lines) / max(len(lines), 1)

        score = 60.0
        score += min(20.0, bullet_lines * 1.5)          # bullet usage is ATS-friendly
        score += 10.0 if 30 <= avg_line_len <= 120 else -10.0  # not walls of text, not too sparse
        score += 10.0 if 200 <= len(raw_text.split()) <= 1200 else -5.0  # reasonable length
        return round(max(0.0, min(100.0, score)), 2)

    def _section_score_and_missing(self, raw_text: str) -> tuple[float, list[str]]:
        lower = raw_text.lower()
        present = []
        missing = []
        for section, keywords in _SECTION_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                present.append(section)
            else:
                missing.append(section)
        score = round((len(present) / len(_STANDARD_SECTIONS)) * 100, 2)
        return score, missing

    async def _keyword_score(self, resume, target_role_id: int) -> float:
        stmt = select(RoleSkill).where(RoleSkill.role_id == target_role_id)
        result = await self.session.execute(stmt)
        role_skills = list(result.scalars().all())
        if not role_skills:
            return 50.0  # neutral default if role has no defined skill taxonomy yet

        resume_skill_names = {s.raw_text.lower() for s in resume.skills}
        total_weight = sum(rs.importance for rs in role_skills)
        matched_weight = sum(
            rs.importance for rs in role_skills
            if rs.skill and rs.skill.name.lower() in resume_skill_names
        )
        return round((matched_weight / total_weight) * 100, 2) if total_weight else 50.0

    async def _generate_suggestions(self, missing_sections: list[str], keyword_score: float) -> list[dict]:
        prompt = (
            f"Resume is missing sections: {missing_sections}. Keyword match score vs target role: "
            f"{keyword_score}%. Generate 3-5 specific, actionable resume improvement suggestions."
        )
        messages = [
            LLMMessage(role="system", content="You are an expert ATS resume reviewer."),
            LLMMessage(role="user", content=prompt),
        ]
        result: ATSSuggestionSet = await self.llm.complete_json(messages, ATSSuggestionSet)
        return [s.model_dump() for s in result.suggestions]

    async def analyze(self, resume_id: str, target_role_id: int) -> ATSReport:
        resume = await self.resume_repo.get_by_id(resume_id)
        raw_text = resume.raw_text or ""

        formatting_score = self._formatting_score(raw_text)
        section_score, missing_sections = self._section_score_and_missing(raw_text)
        keyword_score = await self._keyword_score(resume, target_role_id)

        overall_score = round(
            0.45 * keyword_score + 0.30 * section_score + 0.25 * formatting_score, 2
        )
        suggestions = await self._generate_suggestions(missing_sections, keyword_score)

        return await self.repo.create(
            resume_id=resume.id,
            overall_score=overall_score,
            keyword_score=keyword_score,
            formatting_score=formatting_score,
            section_score=section_score,
            missing_sections=missing_sections,
            suggestions=suggestions,
            target_role_id=target_role_id,
        )

    async def latest(self, resume_id: str) -> ATSReport | None:
        return await self.repo.latest_for_resume(resume_id)

    async def history(self, resume_id: str) -> list[ATSReport]:
        return await self.repo.history_for_resume(resume_id)
