import uuid

from pydantic import BaseModel

from app.shared.base_schemas import ORMBase


class GenerateProblemIn(BaseModel):
    role_id: int | None = None
    difficulty: str = "medium"  # easy | medium | hard


class TestCase(BaseModel):
    input: str
    expected_output: str
    hidden: bool = False


class GeneratedProblem(BaseModel):
    """Structured-generation target passed to LLMProvider.complete_json()."""
    title: str
    statement: str
    starter_code_python: str
    test_cases: list[TestCase]


class CodingProblemOut(ORMBase):
    id: uuid.UUID
    title: str
    difficulty: str
    statement: str
    starter_code: dict | None = None
    # Hidden test cases are intentionally excluded from the response payload.
    visible_test_cases: list[dict] = []


class SubmitCodeIn(BaseModel):
    code: str
    language: str = "python"


class SubmitResultOut(BaseModel):
    passed_cases: int
    total_cases: int
    score: float
    execution_log: list[dict]


class CodingAttemptOut(ORMBase):
    id: uuid.UUID
    problem_id: uuid.UUID
    language: str
    passed_cases: int
    total_cases: int
    score: float | None = None
