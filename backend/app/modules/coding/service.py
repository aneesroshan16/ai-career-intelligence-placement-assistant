import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_core.llm.base import LLMMessage
from app.ai_core.llm.factory import get_llm_provider
from app.core.exceptions import NotFoundError
from app.modules.coding.executor import run_submission
from app.modules.coding.models import CodingAttempt, CodingProblem
from app.modules.coding.repository import CodingRepository
from app.modules.coding.schemas import GeneratedProblem


class CodingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CodingRepository(session)
        self.llm = get_llm_provider()

    async def generate_problem(self, role_id: int | None, difficulty: str) -> CodingProblem:
        messages = [
            LLMMessage(role="system", content="You are an expert technical interviewer creating coding challenges."),
            LLMMessage(
                role="user",
                content=f"Generate a {difficulty} difficulty coding problem appropriate for a "
                        f"role_id={role_id} candidate. Provide a clear problem statement, Python starter "
                        f"code, and 4-6 test cases (stdin input -> expected stdout), with at least 2 marked hidden.",
            ),
        ]
        generated: GeneratedProblem = await self.llm.complete_json(messages, GeneratedProblem)

        return await self.repo.create_problem(
            role_id=role_id,
            title=generated.title,
            difficulty=difficulty,
            statement=generated.statement,
            starter_code={"python": generated.starter_code_python},
            test_cases=[tc.model_dump() for tc in generated.test_cases],
        )

    async def get_problem_for_student(self, problem_id: str) -> CodingProblem:
        problem = await self.repo.get_problem(problem_id)
        if problem is None:
            raise NotFoundError("Coding problem not found")
        return problem

    async def submit(self, user_id: str, problem_id: str, code: str, language: str) -> CodingAttempt:
        problem = await self.repo.get_problem(problem_id)
        if problem is None:
            raise NotFoundError("Coding problem not found")

        result = run_submission(code, language, problem.test_cases)
        return await self.repo.create_attempt(
            user_id=uuid.UUID(user_id),
            problem_id=problem.id,
            submitted_code=code,
            language=language,
            passed_cases=result["passed_cases"],
            total_cases=result["total_cases"],
            score=result["score"],
            execution_log=result["execution_log"],
        )

    async def list_attempts(self, user_id: str) -> list[CodingAttempt]:
        return await self.repo.list_attempts_for_user(user_id)
