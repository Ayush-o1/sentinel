"""
SENTINEL — Common Pydantic Schemas

Shared schema components used across multiple features:
- Pagination
- Standard success responses
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Generic paginated list response envelope."""

    items: list[DataT]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    """Simple success message response."""

    message: str
