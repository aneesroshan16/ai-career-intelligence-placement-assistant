from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_core.llm.base import LLMMessage
from app.ai_core.llm.factory import get_llm_provider
from app.core.config import get_settings
from app.core.exceptions import NotFoundError
from app.modules.roadmap.models import Roadmap
from app.modules.roadmap.repository import RoadmapRepository
from app.modules.roadmap.schemas import RoadmapPlanGeneration
from app.modules.skills.repository import SkillsRepository


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

        missing_skill_names = [m["skill"] for m in gap_report.missing_skills]
        prompt = (
            f"Create a {weeks}-week personalized learning roadmap to close these skill gaps, "
            f"ordered by priority: {missing_skill_names}. Include weekly focus skills, concrete "
            f"tasks, estimated hours per week, and monthly milestones with deliverables."
        )
        messages = [
            LLMMessage(role="system", content="You are an expert technical career mentor and curriculum designer."),
            LLMMessage(role="user", content=prompt),
        ]
        generated: RoadmapPlanGeneration = await self.llm.complete_json(messages, RoadmapPlanGeneration)

        return await self.repo.create(
            skill_gap_report_id=gap_report.id,
            total_weeks=weeks,
            plan=[p.model_dump() | {"tasks_completed": [False] * len(p.tasks)} for p in generated.plan],
            milestones=[m.model_dump() for m in generated.milestones],
            generated_by=self.settings.LLM_PROVIDER,
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
