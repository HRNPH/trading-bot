"""
Backtest-related API schemas.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class BacktestResult(BaseModel):
    """Backtest result model."""

    id: str = Field(description="Backtest result ID")
    symbol: str = Field(description="Trading symbol")
    strategy: str = Field(description="Strategy used")
    timeframe: str = Field(description="Timeframe used")
    start_date: datetime = Field(description="Backtest start date")
    end_date: datetime = Field(description="Backtest end date")
    total_return: float = Field(description="Total return")
    sharpe_ratio: float = Field(description="Sharpe ratio")
    max_drawdown: float = Field(description="Maximum drawdown")
    win_rate: float = Field(description="Win rate")
    total_trades: int = Field(description="Total trades")
    parameters: Dict[str, Any] = Field(description="Strategy parameters")
    created_at: datetime = Field(description="Creation timestamp")

    class Config:
        from_attributes = True


class BacktestResultCreate(BaseModel):
    """Create backtest result request."""

    symbol: str = Field(description="Trading symbol")
    strategy: str = Field(description="Strategy used")
    timeframe: str = Field(description="Timeframe used")
    start_date: datetime = Field(description="Backtest start date")
    end_date: datetime = Field(description="Backtest end date")
    total_return: float = Field(description="Total return")
    sharpe_ratio: float = Field(description="Sharpe ratio")
    max_drawdown: float = Field(description="Maximum drawdown")
    win_rate: float = Field(description="Win rate")
    total_trades: int = Field(description="Total trades")
    parameters: Dict[str, Any] = Field(description="Strategy parameters")


class BacktestCreate(BaseModel):
    """Create backtest request."""

    symbol: str = Field(description="Trading symbol")
    strategy_id: str = Field(description="Strategy ID")
    timeframe: str = Field(description="Timeframe used")
    start_date: datetime = Field(description="Backtest start date")
    end_date: datetime = Field(description="Backtest end date")
    parameters: Dict[str, Any] = Field(description="Strategy parameters")
    status: str = Field(default="pending", description="Backtest status")


class BacktestUpdate(BaseModel):
    """Update backtest request."""

    total_return: Optional[float] = Field(default=None, description="Total return")
    sharpe_ratio: Optional[float] = Field(default=None, description="Sharpe ratio")
    max_drawdown: Optional[float] = Field(default=None, description="Maximum drawdown")
    win_rate: Optional[float] = Field(default=None, description="Win rate")
    total_trades: Optional[int] = Field(default=None, description="Total trades")
    status: Optional[str] = Field(default=None, description="Backtest status")


class BacktestRequest(BaseModel):
    """Backtest request model."""

    symbol: str = Field(description="Trading symbol")
    strategy: str = Field(description="Strategy ID")
    timeframe: str = Field(description="Timeframe (e.g., 1Day, 1Hour)")
    days: int = Field(description="Number of days to backtest", ge=1, le=365)
    initialBalance: float = Field(default=100000, description="Initial balance for backtest")
