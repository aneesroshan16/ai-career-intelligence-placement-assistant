import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.aptitude.repository import AptitudeRepository

_CATEGORIES = ["quantitative", "logical", "verbal"]
_QUESTIONS_PER_CATEGORY = 5


class AptitudeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AptitudeRepository(session)

    async def get_test(self) -> list:
        questions = []
        for category in _CATEGORIES:
            questions.extend(await self.repo.random_questions(category, _QUESTIONS_PER_CATEGORY))
        return questions

    async def submit(self, user_id: str, answers: list) -> dict:
        question_ids = [str(a.question_id) for a in answers]
        questions = await self.repo.get_many(question_ids)
        question_map = {q.id: q for q in questions}

        category_correct = {c: 0 for c in _CATEGORIES}
        category_total = {c: 0 for c in _CATEGORIES}
        correct_answers = 0

        for ans in answers:
            question = question_map.get(ans.question_id)
            if question is None:
                continue
            category_total[question.category] += 1
            if ans.selected_option == question.correct_option:
                category_correct[question.category] += 1
                correct_answers += 1

        category_scores = {
            c: round((category_correct[c] / category_total[c]) * 100, 2) if category_total[c] else 0.0
            for c in _CATEGORIES
        }
        overall_score = round((correct_answers / len(answers)) * 100, 2) if answers else 0.0

        attempt = await self.repo.create_attempt(
            user_id=uuid.UUID(user_id),
            category_scores=category_scores,
            overall_score=overall_score,
            total_questions=len(answers),
            correct_answers=correct_answers,
        )
        return {
            "overall_score": attempt.overall_score,
            "category_scores": attempt.category_scores,
            "total_questions": attempt.total_questions,
            "correct_answers": attempt.correct_answers,
        }

    async def list_attempts(self, user_id: str):
        return await self.repo.list_for_user(user_id)
