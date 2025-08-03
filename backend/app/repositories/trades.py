"""
Trade repository for database operations.
"""

from typing import List, Optional
from datetime import datetime

from prisma import Prisma
from prisma.models import Trade

from ..models.schemas.trading import TradeCreate, TradeUpdate


class TradeRepository:
    """Repository for trade-related database operations."""

    def __init__(self, db: Prisma):
        self.db = db

    async def create(self, trade: TradeCreate) -> Trade:
        """Create a new trade."""
        return await self.db.trade.create(data=trade.model_dump())

    async def get_by_id(self, trade_id: str) -> Optional[Trade]:
        """Get a trade by ID."""
        return await self.db.trade.find_unique(where={"id": trade_id})

    async def get_by_symbol(self, symbol: str, limit: int = 100) -> List[Trade]:
        """Get trades for a specific symbol."""
        return await self.db.trade.find_many(
            where={"symbol": symbol}, order=[{"created_at": "desc"}], take=limit
        )

    async def get_by_strategy(self, strategy_id: str, limit: int = 100) -> List[Trade]:
        """Get trades for a specific strategy."""
        return await self.db.trade.find_many(
            where={"strategy_id": strategy_id},
            order=[{"created_at": "desc"}],
            take=limit,
        )

    async def update(self, trade_id: str, trade_update: TradeUpdate) -> Optional[Trade]:
        """Update a trade."""
        return await self.db.trade.update(
            where={"id": trade_id}, data=trade_update.model_dump(exclude_unset=True)
        )

    async def delete(self, trade_id: str) -> Optional[Trade]:
        """Delete a trade."""
        return await self.db.trade.delete(where={"id": trade_id})

    async def get_recent_trades(self, limit: int = 50) -> List[Trade]:
        """Get recent trades."""
        return await self.db.trade.find_many(order=[{"created_at": "desc"}], take=limit)
