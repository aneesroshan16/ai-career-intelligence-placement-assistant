import uuid

from app.shared.base_schemas import ORMBase


class ReadinessScoreOut(ORMBase):
    id: uuid.UUID
    technical_score: float | None = None
    aptitude_score: float | None = None
    communication_score: float | None = None
    interview_score: float | None = None
    overall_score: float
