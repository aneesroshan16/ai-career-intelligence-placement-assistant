import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReadinessScore(Base):
    __tablename__ = "readiness_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    technical_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    aptitude_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    communication_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    interview_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    overall_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(server_default=func.now())
