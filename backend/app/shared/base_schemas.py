from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ORMBase(BaseModel):
    """Base for schemas that read directly from SQLAlchemy ORM objects."""
    model_config = ConfigDict(from_attributes=True)


class TimestampedSchema(ORMBase):
    created_at: datetime


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
