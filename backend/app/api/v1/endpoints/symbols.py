"""
Symbol API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import structlog

from ....core.database import get_db
from ....models.schemas.symbols import (
    SymbolCreate,
    SymbolUpdate,
    SymbolResponse,
    SymbolListResponse,
)
from ....models.schemas.common import DataResponse, ErrorResponse
from ....repositories.symbols import SymbolRepository
from ....core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/symbols", tags=["symbols"])


@router.get("/", response_model=DataResponse[SymbolListResponse])
def get_symbols(db=Depends(get_db)) -> DataResponse[SymbolListResponse]:
    """Get all available symbols."""
    try:
        symbol_repo = SymbolRepository(db)
        symbols = symbol_repo.get_symbol_codes()

        return DataResponse(success=True, data=SymbolListResponse(symbols=symbols))
    except Exception as e:
        logger.error("Failed to get symbols", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve symbols",
        )


@router.post("/", response_model=DataResponse[SymbolResponse])
def create_symbol(
    symbol_data: SymbolCreate, db=Depends(get_db)
) -> DataResponse[SymbolResponse]:
    """Create a new symbol."""
    try:
        symbol_repo = SymbolRepository(db)

        # Check if symbol already exists
        existing = symbol_repo.get_by_symbol(symbol_data.symbol)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Symbol {symbol_data.symbol} already exists",
            )

        symbol = symbol_repo.create(symbol_data)

        return DataResponse(
            success=True, data=symbol, message="Symbol created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create symbol", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create symbol",
        )


@router.get("/{symbol}", response_model=DataResponse[SymbolResponse])
def get_symbol(symbol: str, db=Depends(get_db)) -> DataResponse[SymbolResponse]:
    """Get symbol by symbol code."""
    try:
        symbol_repo = SymbolRepository(db)
        symbol_data = symbol_repo.get_by_symbol(symbol)

        if not symbol_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Symbol {symbol} not found",
            )

        return DataResponse(success=True, data=symbol_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get symbol", symbol=symbol, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve symbol",
        )


@router.put("/{symbol}", response_model=DataResponse[SymbolResponse])
def update_symbol(
    symbol: str, update_data: SymbolUpdate, db=Depends(get_db)
) -> DataResponse[SymbolResponse]:
    """Update symbol."""
    try:
        symbol_repo = SymbolRepository(db)

        # Check if symbol exists
        existing = symbol_repo.get_by_symbol(symbol)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Symbol {symbol} not found",
            )

        updated_symbol = symbol_repo.update(symbol, update_data)

        if not updated_symbol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid update data provided",
            )

        return DataResponse(
            success=True, data=updated_symbol, message="Symbol updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update symbol", symbol=symbol, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update symbol",
        )


@router.delete("/{symbol}", response_model=DataResponse[dict])
def delete_symbol(symbol: str, db=Depends(get_db)) -> DataResponse[dict]:
    """Delete symbol."""
    try:
        symbol_repo = SymbolRepository(db)

        # Check if symbol exists
        existing = symbol_repo.get_by_symbol(symbol)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Symbol {symbol} not found",
            )

        success = symbol_repo.delete(symbol)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete symbol",
            )

        return DataResponse(
            success=True, data={"deleted": True}, message="Symbol deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete symbol", symbol=symbol, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete symbol",
        )
