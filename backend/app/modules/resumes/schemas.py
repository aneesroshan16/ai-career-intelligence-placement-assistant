import uuid
from datetime import date

from pydantic import BaseModel

from app.shared.base_schemas import ORMBase


class ResumeSkillOut(ORMBase):
    id: int
    raw_text: str
    proficiency: str | None = None
    category: str | None = None


class ResumeEducationOut(ORMBase):
    id: int
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    gpa: float | None = None


class ResumeProjectOut(ORMBase):
    id: int
    title: str
    description: str | None = None
    tech_stack: list[str] | None = None
    project_url: str | None = None


class ResumeCertificationOut(ORMBase):
    id: int
    title: str
    issuer: str | None = None
    issue_date: date | None = None
    credential_url: str | None = None


class ResumeExperienceOut(ORMBase):
    id: int
    company: str
    role: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool


class ResumeOut(ORMBase):
    id: uuid.UUID
    file_type: str
    original_filename: str
    parse_status: str
    is_active: bool
    
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    achievements: list[str] | None = None

    skills: list[ResumeSkillOut] = []
    education: list[ResumeEducationOut] = []
    projects: list[ResumeProjectOut] = []
    certifications: list[ResumeCertificationOut] = []
    experience: list[ResumeExperienceOut] = []


class ResumeSummaryOut(ORMBase):
    id: uuid.UUID
    file_type: str
    original_filename: str
    parse_status: str
    is_active: bool


class ResumeStatusOut(BaseModel):
    id: uuid.UUID
    parse_status: str
