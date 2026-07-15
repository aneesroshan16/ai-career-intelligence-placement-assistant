import uuid

from pydantic import BaseModel

from app.shared.base_schemas import ORMBase


class StartSessionIn(BaseModel):
    mode: str  # hr | technical
    role_id: int | None = None


class AnswerIn(BaseModel):
    answer: str


class TurnFeedback(BaseModel):
    """Structured-generation target for per-answer feedback."""
    clarity: int  # 1-10
    correctness: int  # 1-10
    confidence: int  # 1-10
    tips: list[str]


class NextQuestion(BaseModel):
    """Structured-generation target for the next interview question."""
    question: str


class InterviewTurnOut(ORMBase):
    id: uuid.UUID
    turn_number: int
    question: str
    answer: str | None = None
    feedback: dict | None = None


class InterviewSessionOut(ORMBase):
    id: uuid.UUID
    mode: str
    role_id: int | None = None
    status: str
    overall_feedback: dict | None = None
    score: float | None = None


class InterviewSessionDetailOut(InterviewSessionOut):
    turns: list[InterviewTurnOut] = []


class AnswerResponseOut(BaseModel):
    feedback: TurnFeedback
    next_question: str | None = None
    session_status: str
