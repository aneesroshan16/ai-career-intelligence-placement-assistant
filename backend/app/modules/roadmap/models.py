import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_gap_report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skill_gap_reports.id", ondelete="CASCADE")
    )
    total_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    plan: Mapped[list] = mapped_column(JSONB, nullable=False)
    milestones: Mapped[list] = mapped_column(JSONB, nullable=False)
    generated_by: Mapped[str] = mapped_column(String, default="mock")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
