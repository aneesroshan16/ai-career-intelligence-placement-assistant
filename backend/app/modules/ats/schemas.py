import uuid

from pydantic import BaseModel

from app.shared.base_schemas import ORMBase


class ATSAnalyzeIn(BaseModel):
    resume_id: uuid.UUID
    target_role_id: int


class ATSSuggestion(BaseModel):
    issue: str
    recommendation: str
    severity: str  # low | medium | high


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
    target_role_id: int | None = None
