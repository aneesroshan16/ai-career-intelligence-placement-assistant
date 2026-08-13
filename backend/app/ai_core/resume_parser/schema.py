from pydantic import BaseModel


class ParsedEducation(BaseModel):
    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    gpa: float | None = None


class ParsedExperience(BaseModel):
    company: str
    role: str | None = None
    description: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    is_current: bool = False


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
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    
    raw_text: str
    skills: list[ParsedSkill] = []
    education: list[ParsedEducation] = []
    experience: list[ParsedExperience] = []
    projects: list[ParsedProject] = []
    certifications: list[ParsedCertification] = []
    achievements: list[str] = []
    emails: list[str] = []
    phones: list[str] = []
