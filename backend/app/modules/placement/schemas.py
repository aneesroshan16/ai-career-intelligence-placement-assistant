import uuid

from pydantic import BaseModel

from app.shared.base_schemas import ORMBase


class PlacementPredictIn(BaseModel):
    cgpa: float
    internships: int
    projects_count: int
    certifications_count: int
    skills_count: int
    coding_score: float
    aptitude_score: float
    ats_score: float
    interview_score: float


class PlacementPredictOut(BaseModel):
    probability: float
    predicted_label: bool
    model_version: str


class PlacementPredictionOut(ORMBase):
    id: uuid.UUID
    model_version: str
    input_features: dict
    probability: float
    predicted_label: bool | None = None
