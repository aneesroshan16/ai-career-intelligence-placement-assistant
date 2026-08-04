from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_core.llm.base import LLMMessage
from app.ai_core.llm.factory import get_llm_provider
from app.core.exceptions import NotFoundError, ValidationFailedError
from app.modules.interview.models import InterviewSession
from app.modules.interview.repository import InterviewRepository
from app.modules.interview.schemas import NextQuestion, TurnFeedback

_MAX_TURNS = 5

_OPENING_QUESTIONS = {
    "hr": "Tell me about yourself and why you're interested in this role.",
    "technical": "Walk me through a technical project you're most proud of and the design decisions you made.",
}


class InterviewService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = InterviewRepository(session)
        self.llm = get_llm_provider()

    async def start_session(self, user_id: str, mode: str, role_id: int | None) -> tuple[InterviewSession, str]:
        if mode not in ("hr", "technical"):
            raise ValidationFailedError("mode must be 'hr' or 'technical'")

        interview = await self.repo.create_session(user_id=uuid.UUID(user_id), mode=mode, role_id=role_id)
        first_question = _OPENING_QUESTIONS[mode]
        await self.repo.add_turn(session_id=interview.id, turn_number=1, question=first_question)
        return interview, first_question

    async def submit_answer(self, session_id: str, answer: str) -> dict:
        interview = await self.repo.get_session(session_id)
        if interview is None:
            raise NotFoundError("Interview session not found")
        if interview.status != "in_progress":
            raise ValidationFailedError("This interview session has already ended.")

        current_turn = max(interview.turns, key=lambda t: t.turn_number)

        feedback_messages = [
            LLMMessage(
                role="system",
                content=f"You are conducting a {interview.mode} interview. Evaluate the candidate's answer.",
            ),
            LLMMessage(
                role="user",
                content=f"Question: {current_turn.question}\nCandidate answer: {answer}\n"
                        f"Rate clarity, correctness, and confidence (1-10) and give 2-3 tips.",
            ),
        ]
        feedback: TurnFeedback = await self.llm.complete_json(feedback_messages, TurnFeedback)
        await self.repo.update_turn_answer_feedback(current_turn.id, answer, feedback.model_dump())

        if current_turn.turn_number >= _MAX_TURNS:
            return await self._finalize(interview, feedback)

        next_q_messages = [
            LLMMessage(role="system", content=f"You are conducting a {interview.mode} interview."),
            LLMMessage(
                role="user",
                content=f"Previous question: {current_turn.question}\nCandidate answered: {answer}\n"
                        f"Ask the next relevant interview question, building naturally on the conversation.",
            ),
        ]
        next_q: NextQuestion = await self.llm.complete_json(next_q_messages, NextQuestion)
        await self.repo.add_turn(
            session_id=interview.id, turn_number=current_turn.turn_number + 1, question=next_q.question
        )

        return {"feedback": feedback, "next_question": next_q.question, "session_status": "in_progress"}

    async def _finalize(self, interview: InterviewSession, last_feedback: TurnFeedback) -> dict:
        refreshed = await self.repo.get_session(str(interview.id))
        scored_turns = [t for t in refreshed.turns if t.feedback]
        avg_score = 0.0
        if scored_turns:
            totals = [
                (t.feedback["clarity"] + t.feedback["correctness"] + t.feedback["confidence"]) / 3
                for t in scored_turns
            ]
            avg_score = round((sum(totals) / len(totals)) * 10, 2)  # scale 1-10 -> 0-100

        overall_feedback = {
            "turns_completed": len(scored_turns),
            "avg_clarity": round(sum(t.feedback["clarity"] for t in scored_turns) / max(len(scored_turns), 1), 2),
            "avg_correctness": round(sum(t.feedback["correctness"] for t in scored_turns) / max(len(scored_turns), 1), 2),
            "avg_confidence": round(sum(t.feedback["confidence"] for t in scored_turns) / max(len(scored_turns), 1), 2),
            "summary": "Session complete. Review per-question feedback for detailed improvement tips.",
        }
        await self.repo.complete_session(str(interview.id), overall_feedback, avg_score)
        return {"feedback": last_feedback, "next_question": None, "session_status": "completed"}

    async def complete_session(self, session_id: str) -> InterviewSession:
        interview = await self.repo.get_session(session_id)
        if interview is None:
            raise NotFoundError("Interview session not found")
        if interview.status == "in_progress":
            last_turn = max(interview.turns, key=lambda t: t.turn_number)
            fallback_feedback = TurnFeedback(clarity=5, correctness=5, confidence=5, tips=["Session ended early."])
            await self._finalize(interview, fallback_feedback)
        return await self.repo.get_session(session_id)

    async def get(self, session_id: str) -> InterviewSession:
        interview = await self.repo.get_session(session_id)
        if interview is None:
            raise NotFoundError("Interview session not found")
        return interview

    async def list_for_user(self, user_id: str) -> list[InterviewSession]:
        return await self.repo.list_for_user(user_id)
