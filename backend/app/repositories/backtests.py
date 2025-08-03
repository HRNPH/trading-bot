"""
Backtest repository for database operations.
"""

from typing import List, Optional
from datetime import datetime

from prisma import Prisma
from prisma.models import Backtest

from ..models.schemas.backtest import BacktestCreate, BacktestUpdate


class BacktestRepository:
    """Repository for backtest-related database operations."""

    def __init__(self, db: Prisma):
        self.db = db

    async def create(self, backtest: BacktestCreate) -> Backtest:
        """Create a new backtest."""
        return await self.db.backtest.create(data=backtest.model_dump())

    async def get_by_id(self, backtest_id: str) -> Optional[Backtest]:
        """Get a backtest by ID."""
        return await self.db.backtest.find_unique(where={"id": backtest_id})

    async def get_by_strategy(
        self, strategy_id: str, limit: int = 100
    ) -> List[Backtest]:
        """Get backtests for a specific strategy."""
        return await self.db.backtest.find_many(
            where={"strategy_id": strategy_id},
            order=[{"created_at": "desc"}],
            take=limit,
        )

    async def get_by_symbol(self, symbol: str, limit: int = 100) -> List[Backtest]:
        """Get backtests for a specific symbol."""
        return await self.db.backtest.find_many(
            where={"symbol": symbol}, order=[{"created_at": "desc"}], take=limit
        )

    async def update(
        self, backtest_id: str, backtest_update: BacktestUpdate
    ) -> Optional[Backtest]:
        """Update a backtest."""
        return await self.db.backtest.update(
            where={"id": backtest_id},
            data=backtest_update.model_dump(exclude_unset=True),
        )

    async def delete(self, backtest_id: str) -> Optional[Backtest]:
        """Delete a backtest."""
        return await self.db.backtest.delete(where={"id": backtest_id})

    async def get_recent_backtests(self, limit: int = 50) -> List[Backtest]:
        """Get recent backtests."""
        return await self.db.backtest.find_many(
            order=[{"created_at": "desc"}], take=limit
        )

    async def get_completed_backtests(self, limit: int = 50) -> List[Backtest]:
        """Get completed backtests."""
        return await self.db.backtest.find_many(
            where={"status": "completed"}, order=[{"created_at": "desc"}], take=limit
        )
