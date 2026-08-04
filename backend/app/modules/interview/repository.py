import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.interview.models import InterviewSession, InterviewTurn


class InterviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(self, **fields) -> InterviewSession:
        interview = InterviewSession(**fields)
        self.session.add(interview)
        await self.session.commit()
        await self.session.refresh(interview)
        return interview

    async def get_session(self, session_id: str) -> InterviewSession | None:
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.id == uuid.UUID(session_id))
            .options(selectinload(InterviewSession.turns))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_turn(self, **fields) -> InterviewTurn:
        turn = InterviewTurn(**fields)
        self.session.add(turn)
        await self.session.commit()
        await self.session.refresh(turn)
        return turn

    async def update_turn_answer_feedback(self, turn_id, answer: str, feedback: dict) -> None:
        turn = await self.session.get(InterviewTurn, turn_id)
        turn.answer = answer
        turn.feedback = feedback
        await self.session.commit()

    async def complete_session(self, session_id: str, overall_feedback: dict, score: float) -> InterviewSession:
        from datetime import datetime, timezone

        interview = await self.get_session(session_id)
        interview.status = "completed"
        interview.overall_feedback = overall_feedback
        interview.score = score
        interview.completed_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(interview)
        return interview

    async def list_for_user(self, user_id: str) -> list[InterviewSession]:
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.user_id == uuid.UUID(user_id))
            .order_by(InterviewSession.started_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
