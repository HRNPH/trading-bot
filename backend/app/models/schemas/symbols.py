"""
Symbol-related API schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SymbolBase(BaseModel):
    """Base symbol model."""

    symbol: str = Field(description="Trading symbol (e.g., AAPL)")
    name: Optional[str] = Field(default=None, description="Symbol name")
    description: Optional[str] = Field(default=None, description="Symbol description")


class SymbolCreate(SymbolBase):
    """Create symbol request."""

    symbol: str = Field(..., description="Trading symbol (e.g., AAPL)")


class SymbolUpdate(BaseModel):
    """Update symbol request."""

    name: Optional[str] = Field(default=None, description="Symbol name")
    description: Optional[str] = Field(default=None, description="Symbol description")
    is_active: Optional[bool] = Field(default=None, description="Symbol active status")


class SymbolResponse(SymbolBase):
    """Symbol response model."""

    id: str = Field(description="Symbol ID")
    is_active: bool = Field(description="Symbol active status")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    class Config:
        from_attributes = True


class SymbolListResponse(BaseModel):
    """Symbol list response."""

    symbols: list[str] = Field(description="List of symbol codes")
