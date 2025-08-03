"""
Symbol repository for data access operations.
"""

from typing import List, Optional, Dict, Any
import structlog
from prisma import Prisma

from ..models.schemas.symbols import SymbolCreate, SymbolUpdate, SymbolResponse

logger = structlog.get_logger(__name__)


class SymbolRepository:
    """Repository for symbol data access operations."""

    def __init__(self, db: Prisma) -> None:
        self.db = db

    def create(self, symbol_data: SymbolCreate) -> SymbolResponse:
        """Create a new symbol."""
        try:
            symbol = self.db.symbol.create(
                data={
                    "symbol": symbol_data.symbol.upper(),
                    "name": symbol_data.name or symbol_data.symbol.upper(),
                    "description": symbol_data.description,
                    "isActive": True,
                }
            )

            logger.info("Symbol created successfully", symbol=symbol.symbol)
            return SymbolResponse.model_validate(symbol)

        except Exception as e:
            logger.error(
                "Failed to create symbol", symbol=symbol_data.symbol, error=str(e)
            )
            raise

    def get_by_symbol(self, symbol: str) -> Optional[SymbolResponse]:
        """Get symbol by symbol code."""
        try:
            symbol_data = self.db.symbol.find_unique(where={"symbol": symbol.upper()})

            if symbol_data:
                return SymbolResponse.model_validate(symbol_data)
            return None

        except Exception as e:
            logger.error("Failed to get symbol", symbol=symbol, error=str(e))
            return None

    def get_all(self, active_only: bool = True) -> List[SymbolResponse]:
        """Get all symbols."""
        try:
            where = {"isActive": True} if active_only else {}
            symbols = self.db.symbol.find_many(where=where, order={"symbol": "asc"})

            return [SymbolResponse.model_validate(symbol) for symbol in symbols]

        except Exception as e:
            logger.error("Failed to get symbols", error=str(e))
            return []

    def update(
        self, symbol: str, update_data: SymbolUpdate
    ) -> Optional[SymbolResponse]:
        """Update symbol."""
        try:
            update_dict = {}
            if update_data.name is not None:
                update_dict["name"] = update_data.name
            if update_data.description is not None:
                update_dict["description"] = update_data.description
            if update_data.is_active is not None:
                update_dict["isActive"] = update_data.is_active

            if not update_dict:
                return None

            symbol_data = self.db.symbol.update(
                where={"symbol": symbol.upper()}, data=update_dict
            )

            logger.info("Symbol updated successfully", symbol=symbol)
            return SymbolResponse.model_validate(symbol_data)

        except Exception as e:
            logger.error("Failed to update symbol", symbol=symbol, error=str(e))
            return None

    def delete(self, symbol: str) -> bool:
        """Delete symbol."""
        try:
            self.db.symbol.delete(where={"symbol": symbol.upper()})
            logger.info("Symbol deleted successfully", symbol=symbol)
            return True

        except Exception as e:
            logger.error("Failed to delete symbol", symbol=symbol, error=str(e))
            return False

    def get_symbol_codes(self) -> List[str]:
        """Get list of symbol codes."""
        try:
            symbols = self.db.symbol.find_many(
                where={"isActive": True}, order={"symbol": "asc"}
            )
            return [symbol.symbol for symbol in symbols]

        except Exception as e:
            logger.error("Failed to get symbol codes", error=str(e))
            return []
