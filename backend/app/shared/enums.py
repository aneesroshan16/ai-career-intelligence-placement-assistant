import enum


class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"
    PLACEMENT_OFFICER = "placement_officer"


class ParseStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProficiencyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class InterviewMode(str, enum.Enum):
    HR = "hr"
    TECHNICAL = "technical"


class SessionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class AptitudeCategory(str, enum.Enum):
    QUANTITATIVE = "quantitative"
    LOGICAL = "logical"
    VERBAL = "verbal"


class JobType(str, enum.Enum):
    INTERNSHIP = "internship"
    FULL_TIME = "full_time"
    CONTRACT = "contract"


class FileType(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"


class LLMProviderName(str, enum.Enum):
    MOCK = "mock"
    OPENAI = "openai"
    GEMINI = "gemini"
