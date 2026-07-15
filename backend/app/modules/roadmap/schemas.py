import uuid

from pydantic import BaseModel

from app.shared.base_schemas import ORMBase


class RoadmapGenerateIn(BaseModel):
    skill_gap_report_id: uuid.UUID
    weeks: int = 8


class WeeklyPlanItem(BaseModel):
    week: int
    focus_skills: list[str]
    tasks: list[str]
    est_hours: int


class Milestone(BaseModel):
    month: int
    goal: str
    deliverable: str


class RoadmapPlanGeneration(BaseModel):
    """Structured-generation target passed to LLMProvider.complete_json()."""
    plan: list[WeeklyPlanItem]
    milestones: list[Milestone]


class RoadmapOut(ORMBase):
    id: uuid.UUID
    skill_gap_report_id: uuid.UUID
    total_weeks: int
    plan: list[dict]
    milestones: list[dict]
    generated_by: str


class ProgressUpdateIn(BaseModel):
    week: int
    task_index: int
    completed: bool
