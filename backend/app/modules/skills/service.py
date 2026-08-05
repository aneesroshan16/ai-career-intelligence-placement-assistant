from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.resumes.repository import ResumeRepository
from app.modules.skills.models import SkillGapReport
from app.modules.skills.repository import SkillsRepository


class SkillsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SkillsRepository(session)
        self.resume_repo = ResumeRepository(session)

    async def list_roles(self):
        return await self.repo.list_roles()

    async def recommend_roles(self, resume_id: str):
        resume = await self.resume_repo.get_by_id(resume_id)
        if not resume:
            return await self.list_roles()
            
        all_roles = await self.repo.list_roles()
        all_role_skills = await self.repo.get_all_role_skills()
        
        # Group skills by role_id
        from collections import defaultdict
        role_skills_map = defaultdict(list)
        for rs in all_role_skills:
            role_skills_map[rs.role_id].append(rs)
            
        resume_skill_names = {s.raw_text.lower() for s in resume.skills}
        
        results = []
        for role in all_roles:
            role_skills = role_skills_map.get(role.id, [])
            total_weight = 0
            matched_weight = 0
            for rs in role_skills:
                total_weight += rs.importance
                if rs.skill and rs.skill.name.lower() in resume_skill_names:
                    matched_weight += rs.importance
            
            match_pct = round((matched_weight / total_weight) * 100, 2) if total_weight else 0.0
            
            from app.modules.skills.schemas import RoleOut
            results.append(RoleOut(id=role.id, name=role.name, match_percentage=match_pct))
            
        results.sort(key=lambda r: r.match_percentage or 0.0, reverse=True)
        return results

    async def analyze_gap(self, resume_id: str, role_id: int) -> SkillGapReport:
        resume = await self.resume_repo.get_by_id(resume_id)
        if resume is None:
            raise NotFoundError("Resume not found")

        role_skills = await self.repo.get_role_skills(role_id)
        if not role_skills:
            raise NotFoundError(f"No skill taxonomy defined for role_id={role_id}. Seed role_skills first.")

        resume_skill_names = {s.raw_text.lower() for s in resume.skills}

        matched, missing = [], []
        total_weight = 0
        matched_weight = 0
        for rs in role_skills:
            total_weight += rs.importance
            entry = {"skill": rs.skill.name, "importance": rs.importance}
            if rs.skill.name.lower() in resume_skill_names:
                matched.append(entry)
                matched_weight += rs.importance
            else:
                missing.append(entry)

        match_percentage = round((matched_weight / total_weight) * 100, 2) if total_weight else 0.0
        # Highest-importance gaps surfaced first — most actionable for the roadmap generator.
        missing.sort(key=lambda e: -e["importance"])

        return await self.repo.create_gap_report(
            resume_id=resume.id,
            role_id=role_id,
            matched_skills=matched,
            missing_skills=missing,
            match_percentage=match_percentage,
        )

    async def get_report(self, report_id: str) -> SkillGapReport:
        report = await self.repo.get_gap_report(report_id)
        if report is None:
            raise NotFoundError("Skill gap report not found")
        return report
