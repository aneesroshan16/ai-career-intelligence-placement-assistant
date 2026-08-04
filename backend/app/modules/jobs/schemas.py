import uuid

from pydantic import BaseModel

from app.shared.base_schemas import ORMBase


class CompanyOut(BaseModel):
    id: int
    name: str
    logo_url: str | None = None


class JobCreateIn(BaseModel):
    title: str
    company_name: str
    role_id: int | None = None
    description: str | None = None
    required_skills: list[str] = []
    experience_min: float = 0
    experience_max: float | None = None
    location: str | None = None
    job_type: str  # internship | full_time | contract


class JobOut(ORMBase):
    id: uuid.UUID
    title: str
    role_id: int | None = None
    description: str | None = None
    required_skills: list | None = None
    experience_min: float
    experience_max: float | None = None
    location: str | None = None
    job_type: str
    is_active: bool


class JobFilterParams(BaseModel):
    location: str | None = None
    job_type: str | None = None
    experience_max: float | None = None
    role_id: int | None = None
