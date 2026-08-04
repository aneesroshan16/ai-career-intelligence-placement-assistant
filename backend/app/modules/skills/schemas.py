import uuid

from pydantic import BaseModel

from app.shared.base_schemas import ORMBase


class RoleOut(BaseModel):
    id: int
    name: str


class SkillEntry(BaseModel):
    skill: str
    importance: int


class GapAnalysisIn(BaseModel):
    resume_id: uuid.UUID
    role_id: int


class SkillGapReportOut(ORMBase):
    id: uuid.UUID
    resume_id: uuid.UUID
    role_id: int
    matched_skills: list[dict]
    missing_skills: list[dict]
    match_percentage: float
