import uuid

from pydantic import BaseModel


class ComputeMatchIn(BaseModel):
    resume_id: uuid.UUID


class JobMatchOut(BaseModel):
    job_id: uuid.UUID
    title: str
    company_name: str | None = None
    location: str | None = None
    job_type: str
    similarity_score: float
