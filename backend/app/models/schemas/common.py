"""
Common API response schemas.
"""

from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base API response model."""

    success: bool = Field(description="Operation success status")
    message: Optional[str] = Field(default=None, description="Response message")


class DataResponse(BaseResponse, Generic[T]):
    """API response with data."""

    data: Optional[T] = Field(default=None, description="Response data")


class ErrorResponse(BaseResponse):
    """API error response."""

    error: str = Field(description="Error message")
    details: Optional[Any] = Field(default=None, description="Error details")


class PaginatedResponse(BaseResponse, Generic[T]):
    """Paginated API response."""

    data: list[T] = Field(description="Response data")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    size: int = Field(description="Page size")
    pages: int = Field(description="Total number of pages")
