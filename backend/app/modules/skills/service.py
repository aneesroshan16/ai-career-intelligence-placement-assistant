from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.resumes.repository import ResumeRepository
from app.modules.skills.models import SkillGapReport
from app.modules.skills.repository import SkillsRepository
from app.modules.skills.schemas import RoleOut


class SkillsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SkillsRepository(session)
        self.resume_repo = ResumeRepository(session)

    async def list_roles(self):
        return await self.repo.list_roles()

    async def recommend_roles(self, resume_id: str):
        resume = await self.resume_repo.get_by_id(resume_id)
        if not resume or not resume.skills:
            return await self.list_roles()
            
        resume_skill_names = {s.raw_text.lower() for s in resume.skills if s.raw_text}
        
        all_role_skills = await self.repo.get_all_role_skills()
        
        # Group role_skills by role_id
        from collections import defaultdict
        role_reqs = defaultdict(list)
        for rs in all_role_skills:
            role_reqs[rs.role_id].append(rs)
            
        # Get all roles to have names
        all_roles = {r.id: r for r in await self.repo.list_roles()}
        
        scored_roles = []
        for role_id, reqs in role_reqs.items():
            if role_id not in all_roles:
                continue
            
            max_score = sum(rs.importance for rs in reqs)
            if max_score == 0:
                continue
                
            matched_skills = []
            missing_skills = []
            base_score = 0
            
            for rs in reqs:
                if rs.skill.name.lower() in resume_skill_names:
                    base_score += rs.importance
                    matched_skills.append(rs.skill.name)
                else:
                    missing_skills.append(rs.skill.name)
                    
            match_percentage = (base_score / max_score) * 100
            
            # Formulate reasoning
            reasoning = "Excellent match."
            if matched_skills:
                reasoning = f"Matched {', '.join(matched_skills[:3])}."
            if missing_skills:
                reasoning += f" Missing {', '.join(missing_skills[:2])}."
                
            scored_roles.append({
                "role": all_roles[role_id],
                "match_percentage": round(match_percentage, 1),
                "reasoning": reasoning
            })
            
        # Sort by match percentage desc
        scored_roles.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        # Return top 4
        results = []
        for sr in scored_roles[:4]:
            results.append(RoleOut(
                id=sr["role"].id,
                name=sr["role"].name,
                match_percentage=sr["match_percentage"],
                reasoning=sr["reasoning"]
            ))
            
        return results

    async def analyze_gap(self, resume_id: str, role_id: int) -> SkillGapReport:
        resume = await self.resume_repo.get_by_id(resume_id)
        if resume is None:
            raise NotFoundError("Resume not found")

        from app.modules.skills.models import Role
        role = await self.session.get(Role, role_id)
        if not role:
            raise NotFoundError("Target role not found")

        resume_skill_names = {s.raw_text.lower() for s in resume.skills if s.raw_text}
        role_skills = await self.repo.get_role_skills(role_id)
        
        matched = []
        missing = []
        max_score = sum(rs.importance for rs in role_skills)
        base_score = 0
        
        for rs in role_skills:
            skill_name = rs.skill.name
            importance = rs.importance
            
            if skill_name.lower() in resume_skill_names:
                base_score += importance
                matched.append({
                    "skill": skill_name,
                    "importance": importance,
                    "status": "Strong" if importance >= 4 else "Developing"
                })
            else:
                missing.append({
                    "skill": skill_name,
                    "importance": importance,
                    "status": "Missing",
                    "priority": importance * 2  # Higher importance missing = highest priority
                })
                
        # Sort missing by priority desc
        missing.sort(key=lambda e: e["priority"], reverse=True)
        
        match_percentage = (base_score / max_score * 100) if max_score > 0 else 0

        return await self.repo.create_gap_report(
            resume_id=resume.id,
            role_id=role_id,
            matched_skills=matched,
            missing_skills=missing,
            match_percentage=round(match_percentage, 1),
        )

    async def get_report(self, report_id: str) -> SkillGapReport:
        report = await self.repo.get_gap_report(report_id)
        if report is None:
            raise NotFoundError("Skill gap report not found")
        return report
