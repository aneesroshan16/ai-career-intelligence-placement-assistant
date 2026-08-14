from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_core.llm.factory import get_llm_provider
from app.core.config import get_settings
from app.core.exceptions import NotFoundError
from app.modules.roadmap.models import Roadmap
from app.modules.roadmap.repository import RoadmapRepository
from app.modules.skills.repository import SkillsRepository
from app.modules.skills.models import Role
from app.modules.skills.catalog import metadata_for


class RoadmapService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = RoadmapRepository(session)
        self.skills_repo = SkillsRepository(session)
        self.llm = get_llm_provider()
        self.settings = get_settings()

    async def generate(self, skill_gap_report_id: str, weeks: int) -> Roadmap:
        gap_report = await self.skills_repo.get_gap_report(skill_gap_report_id)
        if gap_report is None:
            raise NotFoundError("Skill gap report not found")

        missing_skills = [m for m in gap_report.missing_skills]
        role = await self.session.get(Role, gap_report.role_id)
        role_name = role.name if role else "your target role"

        # Deterministic roadmap based on the persisted gap report.  Sort by
        # priority and move unmet prerequisites before dependent topics.
        missing_skills.sort(key=lambda item: item.get("priority", item.get("importance", 0)), reverse=True)
        missing_names = {item["skill"] for item in missing_skills}
        ordered_skills = []
        visiting = set()
        def add_with_prerequisites(item):
            name = item["skill"]
            if name in visiting or any(existing["skill"] == name for existing in ordered_skills):
                return
            visiting.add(name)
            for prerequisite in item.get("prerequisites", metadata_for(name)["prerequisites"]):
                if prerequisite in missing_names:
                    prerequisite_item = next(candidate for candidate in missing_skills if candidate["skill"] == prerequisite)
                    add_with_prerequisites(prerequisite_item)
            visiting.remove(name)
            ordered_skills.append(item)
        for item in missing_skills:
            add_with_prerequisites(item)

        plan = []
        milestones = []
        
        if not missing_skills:
            plan.append({
                "week": 1,
                "focus_skill": "Interview Prep",
                "tasks": ["Review portfolio", "Mock interviews"],
                "estimated_hours": 5,
                "tasks_completed": [False, False]
            })
            milestones.append({"month": 1, "milestone": "Ready for Interviews", "deliverable": "Updated Resume"})
        else:
            import math
            skills_per_week = max(1, math.ceil(len(ordered_skills) / weeks))
            current_skill_idx = 0
            
            for w in range(1, weeks + 1):
                week_skills = ordered_skills[current_skill_idx : current_skill_idx + skills_per_week]
                
                if week_skills:
                    focus = week_skills[0]["skill"]
                    focus_meta = metadata_for(focus)
                    tasks = [f"Study {s['skill']}: {', '.join(metadata_for(s['skill'])['topics'][:2])}" for s in week_skills]
                    tasks += [f"Practice: {focus_meta['assessment']}", f"Mini-project: apply {focus} to a {role_name} scenario"]
                else:
                    focus = "Advanced Practice & Revision"
                    tasks = ["Solve related problems", "Revise previous concepts"]
                    
                plan.append({
                    "week": w,
                    "focus_skill": focus,
                    "focus_skills": [s["skill"] for s in week_skills] or [focus],
                    "why_required": f"{focus} is a {week_skills[0].get('gap_severity', 'priority')} gap for {role_name}." if week_skills else "Consolidate demonstrated skills before interviews.",
                    "current_level": week_skills[0].get("current_level", "developing") if week_skills else "developing",
                    "target_level": week_skills[0].get("required_level", "role-ready") if week_skills else "role-ready",
                    "topics": metadata_for(focus)["topics"],
                    "assessment": metadata_for(focus)["assessment"],
                    "tasks": tasks,
                    "estimated_hours": 10,
                    "tasks_completed": [False] * len(tasks)
                })
                current_skill_idx += len(week_skills)
                
                if w % 4 == 0 or w == weeks:
                    # Avoid duplicate milestones if weeks < 4
                    if len(milestones) == 0 or milestones[-1]["month"] != max(1, w // 4):
                        milestones.append({
                            "month": max(1, w // 4),
                            "milestone": f"Mastery of {focus}",
                            "deliverable": f"Project integrating {focus}"
                        })

        return await self.repo.create(
            skill_gap_report_id=gap_report.id,
            total_weeks=weeks,
            plan=plan,
            milestones=milestones,
            generated_by="deterministic_engine",
        )

    async def get(self, roadmap_id: str) -> Roadmap:
        roadmap = await self.repo.get(roadmap_id)
        if roadmap is None:
            raise NotFoundError("Roadmap not found")
        return roadmap

    async def update_progress(self, roadmap_id: str, week: int, task_index: int, completed: bool) -> Roadmap:
        roadmap = await self.get(roadmap_id)
        plan = list(roadmap.plan)
        for item in plan:
            if item.get("week") == week:
                flags = item.setdefault("tasks_completed", [False] * len(item.get("tasks", [])))
                if 0 <= task_index < len(flags):
                    flags[task_index] = completed
        await self.repo.update_plan(roadmap_id, plan)
        return await self.get(roadmap_id)
