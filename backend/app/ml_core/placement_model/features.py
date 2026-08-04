"""
Feature definition for the placement prediction model. `FEATURE_ORDER` is the
single source of truth for column order — used identically at training time
(train.py reads the CSV in this order) and inference time (FeatureBuilder
produces a vector in this order), so the two never drift apart silently.
"""
from pydantic import BaseModel, Field

FEATURE_ORDER = [
    "cgpa",
    "internships",
    "projects_count",
    "certifications_count",
    "skills_count",
    "coding_score",
    "aptitude_score",
    "ats_score",
    "interview_score",
]


class PlacementFeatures(BaseModel):
    cgpa: float = Field(ge=0, le=10)
    internships: int = Field(ge=0)
    projects_count: int = Field(ge=0)
    certifications_count: int = Field(ge=0)
    skills_count: int = Field(ge=0)
    coding_score: float = Field(ge=0, le=100)
    aptitude_score: float = Field(ge=0, le=100)
    ats_score: float = Field(ge=0, le=100)
    interview_score: float = Field(ge=0, le=100)

    def to_vector(self) -> list[float]:
        return [getattr(self, f) for f in FEATURE_ORDER]
