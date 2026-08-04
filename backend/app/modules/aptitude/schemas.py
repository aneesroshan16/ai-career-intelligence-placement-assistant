import uuid

from pydantic import BaseModel

from app.shared.base_schemas import ORMBase


class AptitudeQuestionOut(BaseModel):
    id: uuid.UUID
    category: str
    question: str
    options: list[str]
    difficulty: str | None = None


class AnswerEntry(BaseModel):
    question_id: uuid.UUID
    selected_option: int


class SubmitAptitudeIn(BaseModel):
    answers: list[AnswerEntry]


class AptitudeResultOut(BaseModel):
    overall_score: float
    category_scores: dict
    total_questions: int
    correct_answers: int


class AptitudeAttemptOut(ORMBase):
    id: uuid.UUID
    overall_score: float
    category_scores: dict
    total_questions: int
    correct_answers: int
