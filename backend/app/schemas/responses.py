from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Wrap any list endpoint with pagination metadata."""

    items: List[T]
    total: int
    skip: int
    limit: int


class MessageResponse(BaseModel):
    """Simple message confirmation response."""

    message: str


class ErrorResponse(BaseModel):
    """FastAPI returns this shape automatically via HTTPException.
    Defined here so OpenAPI schema shows the correct 4xx/5xx body."""

    detail: str
