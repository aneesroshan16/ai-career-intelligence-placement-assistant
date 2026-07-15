import uuid
from datetime import date, datetime

from sqlalchemy import ARRAY, Boolean, Date, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    parse_status: Mapped[str] = mapped_column(String, default="pending")
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_id: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    skills: Mapped[list["ResumeSkill"]] = relationship(back_populates="resume", cascade="all, delete-orphan")
    education: Mapped[list["ResumeEducation"]] = relationship(back_populates="resume", cascade="all, delete-orphan")
    projects: Mapped[list["ResumeProject"]] = relationship(back_populates="resume", cascade="all, delete-orphan")
    certifications: Mapped[list["ResumeCertification"]] = relationship(back_populates="resume", cascade="all, delete-orphan")


class ResumeSkill(Base):
    __tablename__ = "resume_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"))
    skill_id: Mapped[int | None] = mapped_column(ForeignKey("skills_master.id"), nullable=True)
    raw_text: Mapped[str] = mapped_column(String, nullable=False)
    proficiency: Mapped[str | None] = mapped_column(String, nullable=True)

    resume: Mapped["Resume"] = relationship(back_populates="skills")


class ResumeEducation(Base):
    __tablename__ = "resume_education"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"))
    institution: Mapped[str | None] = mapped_column(String, nullable=True)
    degree: Mapped[str | None] = mapped_column(String, nullable=True)
    field_of_study: Mapped[str | None] = mapped_column(String, nullable=True)
    start_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gpa: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)

    resume: Mapped["Resume"] = relationship(back_populates="education")


class ResumeProject(Base):
    __tablename__ = "resume_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tech_stack: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    project_url: Mapped[str | None] = mapped_column(String, nullable=True)

    resume: Mapped["Resume"] = relationship(back_populates="projects")


class ResumeCertification(Base):
    __tablename__ = "resume_certifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    issuer: Mapped[str | None] = mapped_column(String, nullable=True)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    credential_url: Mapped[str | None] = mapped_column(String, nullable=True)

    resume: Mapped["Resume"] = relationship(back_populates="certifications")
