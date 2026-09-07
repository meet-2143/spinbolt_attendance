from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorResponse(BaseModel):
    success: bool = False
    message: str


class PagedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
