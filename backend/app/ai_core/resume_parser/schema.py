from pydantic import BaseModel


class ParsedEducation(BaseModel):
    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    gpa: float | None = None


class ParsedProject(BaseModel):
    title: str
    description: str | None = None
    tech_stack: list[str] = []
    project_url: str | None = None


class ParsedCertification(BaseModel):
    title: str
    issuer: str | None = None


class ParsedSkill(BaseModel):
    raw_text: str
    normalized_name: str | None = None  # matched against skills_master, if found


class ParsedResume(BaseModel):
    raw_text: str
    skills: list[ParsedSkill] = []
    education: list[ParsedEducation] = []
    projects: list[ParsedProject] = []
    certifications: list[ParsedCertification] = []
    emails: list[str] = []
    phones: list[str] = []
