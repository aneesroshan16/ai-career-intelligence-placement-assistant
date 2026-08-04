import math

from fastapi import Query
from pydantic import BaseModel


class PageParams(BaseModel):
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def page_params(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)) -> PageParams:
    return PageParams(page=page, page_size=page_size)


def total_pages(total: int, page_size: int) -> int:
    return max(1, math.ceil(total / page_size))
