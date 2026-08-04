import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, Numeric, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    role_skills: Mapped[list["RoleSkill"]] = relationship(back_populates="role")


class SkillMaster(Base):
    __tablename__ = "skills_master"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)


class RoleSkill(Base):
    __tablename__ = "role_skills"
    __table_args__ = (UniqueConstraint("role_id", "skill_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills_master.id", ondelete="CASCADE"))
    importance: Mapped[int] = mapped_column(SmallInteger, default=3)

    role: Mapped["Role"] = relationship(back_populates="role_skills")
    skill: Mapped["SkillMaster"] = relationship()


class SkillGapReport(Base):
    __tablename__ = "skill_gap_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    matched_skills: Mapped[list] = mapped_column(JSONB, nullable=False)
    missing_skills: Mapped[list] = mapped_column(JSONB, nullable=False)
    match_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    role: Mapped["Role"] = relationship()
