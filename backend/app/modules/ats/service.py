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
        lines = [line for line in raw_text.split("\n") if line.strip()]
        bullet_lines = sum(1 for line in lines if line.strip().startswith(("-", "•", "*")))
        avg_line_len = sum(len(line) for line in lines) / max(len(lines), 1)

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
        from sqlalchemy.orm import joinedload
        stmt = select(RoleSkill).where(RoleSkill.role_id == target_role_id).options(joinedload(RoleSkill.skill))
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

    async def _generate_suggestions(self, missing_sections: list[str], keyword_score: float, raw_text: str, role_name: str) -> list[dict]:
        prompt = (
            f"Analyze the following resume text for a candidate targeting a {role_name} role. "
            f"The resume is missing these standard sections: {missing_sections}. "
            f"Its keyword match score for the target role is {keyword_score}%. "
            f"Based on the actual content of the resume below, generate 3-5 highly specific, actionable "
            f"improvement suggestions tailored to this exact candidate and their goal.\n\n"
            f"Resume Text:\n{raw_text[:3000]}" # Truncating to avoid massive token usage just in case
        )
        messages = [
            LLMMessage(role="system", content="You are an expert ATS resume reviewer."),
            LLMMessage(role="user", content=prompt),
        ]
        result: ATSSuggestionSet = await self.llm.complete_json(messages, ATSSuggestionSet)
        return [s.model_dump() for s in result.suggestions]

    async def _comprehensive_analysis(self, resume, role_id: int | None, role_name: str, keyword_score: float,
                                      section_score: float, formatting_score: float, missing_sections: list[str]) -> dict:
        """Create explainable UI data from stored resume evidence, never fabricated skills."""
        from app.modules.skills.service import SkillsService
        recommendations = await SkillsService(self.session).recommend_roles(str(resume.id))
        # Load names from the recommendation selected role when available; role skill
        # details are otherwise represented by the deterministic keyword score.
        selected = next((r for r in recommendations if r.id == role_id), None)
        missing_keywords = (selected.missing_skills if selected else [])[:8]
        contact_score = 100.0 if resume.email and resume.phone else 60.0 if (resume.email or resume.phone) else 0.0
        experience_score = min(100.0, len(resume.experience) * 35 + len(resume.projects) * 15)
        project_score = min(100.0, len(resume.projects) * 35)
        education_score = 100.0 if resume.education else 0.0
        skills_score = keyword_score
        strengths = []
        if resume.skills:
            strengths.append(f"Resume evidence supports {len(resume.skills)} normalized skills.")
        if resume.projects:
            strengths.append(f"Includes {len(resume.projects)} project record(s) that can support interview discussion.")
        if resume.email or resume.phone:
            strengths.append("Includes candidate contact information.")
        areas = [f"Add a clear {section} section." for section in missing_sections]
        if missing_keywords:
            areas.append(f"Demonstrate relevant {role_name} evidence for: {', '.join(missing_keywords[:3])}.")
        return {
            "overall_score": round(0.45 * keyword_score + 0.20 * section_score + 0.15 * formatting_score + 0.10 * contact_score + 0.10 * ((experience_score + project_score + education_score) / 3), 2),
            "category_scores": {"structure": section_score, "keywords": keyword_score, "skills": skills_score,
                                "experience": experience_score, "projects": project_score, "education": education_score,
                                "ats_compatibility": formatting_score, "contact_info": contact_score},
            "strengths": strengths or ["Upload a fuller resume to establish verified strengths."],
            "areas_to_improve": areas or ["Tailor project outcomes and keywords to the selected role."],
            "missing_keywords": missing_keywords,
            "resume_summary": f"Parsed resume contains {len(resume.skills)} skills, {len(resume.projects)} projects and {len(resume.experience)} experience entries; analysis is targeted to {role_name}.",
            "recommended_roles": [{"role_name": r.name, "match_percentage": r.match_percentage,
                                    "why_matches": r.matched_skills[:3] or ["No required-skill evidence found yet"],
                                    "missing_skills": r.missing_skills[:5]} for r in recommendations],
            "actionable_improvements": areas[:5] or ["Quantify project outcomes and tailor the resume for the target role."],
            "suggested_changes": [{"current": "Skills are listed without role context.", "suggested": f"Connect verified skills and projects to {role_name} responsibilities."}],
        }

    async def analyze(self, resume_id: str, target_role_id: int | None = None) -> ATSReport:
        resume = await self.resume_repo.get_by_id(resume_id)
        raw_text = resume.raw_text or " ".join(s.raw_text for s in resume.skills)

        formatting_score = self._formatting_score(raw_text)
        section_score, missing_sections = self._section_score_and_missing(raw_text)
        
        role_name = "general industry standards"
        keyword_score = 50.0
        
        if target_role_id is None:
            # Try to infer a top role using deterministic SkillsService
            from app.modules.skills.service import SkillsService
            skills_service = SkillsService(self.session)
            recommended = await skills_service.recommend_roles(resume_id)
            if recommended and hasattr(recommended[0], "id"):
                target_role_id = recommended[0].id
                role_name = recommended[0].name
                keyword_score = await self._keyword_score(resume, target_role_id)
        else:
            keyword_score = await self._keyword_score(resume, target_role_id)
            from app.modules.skills.models import Role
            role = await self.session.get(Role, target_role_id)
            if role:
                role_name = role.name

        comprehensive = await self._comprehensive_analysis(resume, target_role_id, role_name, keyword_score,
                                                           section_score, formatting_score, missing_sections)
        # Deterministic report content is used for scores and recommendations.  The
        # optional LLM advice is deliberately not required for a valid ATS report.
        suggestions = [comprehensive]

        return await self.repo.create(
            resume_id=resume.id,
            overall_score=comprehensive["overall_score"],
            keyword_score=keyword_score,
            formatting_score=formatting_score,
            section_score=section_score,
            missing_sections=missing_sections,
            suggestions=suggestions,
            recommended_roles=comprehensive["recommended_roles"],
            target_role_id=target_role_id,
        )

    async def latest(self, resume_id: str) -> ATSReport | None:
        return await self.repo.latest_for_resume(resume_id)

    async def history(self, resume_id: str) -> list[ATSReport]:
        return await self.repo.history_for_resume(resume_id)
