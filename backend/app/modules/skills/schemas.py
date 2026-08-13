import uuid

from pydantic import BaseModel

from app.shared.base_schemas import ORMBase


class RoleOut(BaseModel):
    id: int
    name: str
    match_percentage: float | None = None
    reasoning: str | None = None

class RoleRecommendation(BaseModel):
    name: str
    match_percentage: float
    reasoning: str

class RoleRecommendationsList(BaseModel):
    recommendations: list[RoleRecommendation]


class SkillEntry(BaseModel):
    skill: str
    importance: int


class GapAnalysisIn(BaseModel):
    resume_id: uuid.UUID
    role_id: int


class SkillGapGeneration(BaseModel):
    matched_skills: list[SkillEntry]
    missing_skills: list[SkillEntry]
    match_percentage: float


class SkillGapReportOut(ORMBase):
    id: uuid.UUID
    resume_id: uuid.UUID
    role_id: int
    matched_skills: list[dict]
    missing_skills: list[dict]
    match_percentage: float
