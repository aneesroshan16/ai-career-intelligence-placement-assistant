import uuid

from pydantic import BaseModel

from app.shared.base_schemas import ORMBase


class ATSAnalyzeIn(BaseModel):
    resume_id: uuid.UUID
    target_role_id: int | None = None

class ATSSuggestion(BaseModel):
    issue: str
    recommendation: str
    severity: str  # low | medium | high

class ATSCategoryScores(BaseModel):
    structure: float
    keywords: float
    skills: float
    experience: float
    projects: float
    education: float
    ats_compatibility: float
    contact_info: float

class RecommendedRole(BaseModel):
    role_name: str
    match_percentage: float
    why_matches: list[str]
    missing_skills: list[str]

class ResumeImprovement(BaseModel):
    current: str
    suggested: str

class ComprehensiveATSAnalysis(BaseModel):
    overall_score: float
    category_scores: ATSCategoryScores
    strengths: list[str]
    areas_to_improve: list[str]
    missing_keywords: list[str]
    resume_summary: str
    recommended_roles: list[RecommendedRole]
    actionable_improvements: list[str]
    suggested_changes: list[ResumeImprovement]

class ATSSuggestionSet(BaseModel):
    """Structured-generation target passed to LLMProvider.complete_json()."""
    suggestions: list[ATSSuggestion]

class ATSReportOut(ORMBase):
    id: uuid.UUID
    resume_id: uuid.UUID
    overall_score: float
    keyword_score: float | None = None
    formatting_score: float | None = None
    section_score: float | None = None
    missing_sections: list[str] | None = None
    suggestions: list[dict] | None = None
    recommended_roles: list[dict] | None = None
    target_role_id: int | None = None
