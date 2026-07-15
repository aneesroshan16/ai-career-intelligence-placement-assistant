import uuid
from datetime import datetime

from sqlalchemy import ARRAY, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ATSReport(Base):
    __tablename__ = "ats_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"))
    overall_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    keyword_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    formatting_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    section_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    missing_sections: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    suggestions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    target_role_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    role: Mapped["Role | None"] = relationship()
