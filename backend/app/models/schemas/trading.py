"""
Trading-related API schemas.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class StrategyInfo(BaseModel):
    """Strategy information."""

    id: str = Field(description="Strategy ID")
    name: str = Field(description="Strategy name")
    description: str = Field(description="Strategy description")
    parameters: Dict[str, Any] = Field(description="Strategy parameters")


class BacktestRequest(BaseModel):
    """Backtest request model."""

    symbol: str = Field(description="Trading symbol")
    strategy: str = Field(description="Strategy ID")
    timeframe: str = Field(description="Timeframe (e.g., 1Day, 1Hour)")
    days: int = Field(description="Number of days to backtest", ge=1, le=365)


class LiveTradingRequest(BaseModel):
    """Live trading request model."""

    symbol: str = Field(description="Trading symbol")
    strategy: str = Field(description="Strategy ID")
    timeframe: str = Field(description="Timeframe (e.g., 1Day, 1Hour)")


class TradeInfo(BaseModel):
    """Trade information."""

    trade_id: str = Field(description="Trade ID")
    entry_time: str = Field(description="Entry timestamp")
    entry_price: float = Field(description="Entry price")
    exit_time: Optional[str] = Field(default=None, description="Exit timestamp")
    exit_price: Optional[float] = Field(default=None, description="Exit price")
    profit_loss: float = Field(description="Profit/Loss")
    profit_loss_pct: str = Field(description="Profit/Loss percentage")
    duration_days: float = Field(description="Trade duration in days")
    status: str = Field(description="Trade status")


class BacktestResults(BaseModel):
    """Backtest results."""

    total_return: float = Field(description="Total return percentage")
    sharpe_ratio: float = Field(description="Sharpe ratio")
    max_drawdown: float = Field(description="Maximum drawdown percentage")
    win_rate: float = Field(description="Win rate percentage")
    total_trades: int = Field(description="Total number of trades")
    volatility: float = Field(description="Volatility percentage")
    equity_chart: Optional[Dict[str, Any]] = Field(
        default=None, description="Equity chart data"
    )
    price_chart: Optional[Dict[str, Any]] = Field(
        default=None, description="Price chart data"
    )
    trades: list[TradeInfo] = Field(description="List of trades")


class LiveStatus(BaseModel):
    """Live trading status."""

    portfolio_value: float = Field(description="Current portfolio value")
    cash: float = Field(description="Available cash")
    position: float = Field(description="Current position size")
    total_return: float = Field(description="Total return percentage")
    price_chart: Optional[Dict[str, Any]] = Field(
        default=None, description="Price chart data"
    )
    trades: list[TradeInfo] = Field(description="Recent trades")


class TradeCreate(BaseModel):
    """Create trade request."""

    symbol: str = Field(description="Trading symbol")
    strategy_id: str = Field(description="Strategy ID")
    entry_price: float = Field(description="Entry price")
    entry_time: datetime = Field(description="Entry timestamp")
    position_size: float = Field(description="Position size")
    side: str = Field(description="Trade side (buy/sell)")
    status: str = Field(default="open", description="Trade status")


class TradeUpdate(BaseModel):
    """Update trade request."""

    exit_price: Optional[float] = Field(default=None, description="Exit price")
    exit_time: Optional[datetime] = Field(default=None, description="Exit timestamp")
    profit_loss: Optional[float] = Field(default=None, description="Profit/Loss")
    status: Optional[str] = Field(default=None, description="Trade status")
