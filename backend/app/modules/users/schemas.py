import uuid

from pydantic import BaseModel

from app.shared.base_schemas import ORMBase


class StudentProfileOut(ORMBase):
    id: uuid.UUID
    roll_number: str | None = None
    department_id: int | None = None
    graduation_year: int | None = None
    cgpa: float | None = None
    internships: int
    active_backlogs: int
    phone: str | None = None
    location: str | None = None


class UserOut(ORMBase):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    avatar_url: str | None = None
    profile: StudentProfileOut | None = None


class ProfileUpdateIn(BaseModel):
    roll_number: str | None = None
    department_id: int | None = None
    graduation_year: int | None = None
    cgpa: float | None = None
    internships: int | None = None
    active_backlogs: int | None = None
    phone: str | None = None
    location: str | None = None
    full_name: str | None = None
