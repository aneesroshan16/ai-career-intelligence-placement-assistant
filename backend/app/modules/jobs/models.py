import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String, nullable=True)

    jobs: Mapped[list["Job"]] = relationship(back_populates="company")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"), nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    role_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_skills: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    experience_min: Mapped[float] = mapped_column(Numeric(3, 1), default=0)
    experience_max: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    job_type: Mapped[str] = mapped_column(String, nullable=False)
    embedding_id: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    posted_at: Mapped[datetime] = mapped_column(server_default=func.now())

    company: Mapped["Company | None"] = relationship(back_populates="jobs")
    role: Mapped["Role | None"] = relationship()
