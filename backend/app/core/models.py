"""Data models for the trading platform."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import pandas as pd


class OrderSide(str, Enum):
    """Order side enumeration."""

    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order type enumeration."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class PositionSide(str, Enum):
    """Position side enumeration."""

    LONG = "long"
    SHORT = "short"


@dataclass
class Bar:
    """OHLCV bar data."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_dict(self) -> Dict[str, Union[datetime, float]]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


@dataclass
class Signal:
    """Trading signal."""

    timestamp: datetime
    symbol: str
    side: OrderSide
    price: float
    quantity: float
    signal_type: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "symbol": self.symbol,
            "side": self.side.value,
            "price": self.price,
            "quantity": self.quantity,
            "signal_type": self.signal_type,
            "metadata": self.metadata or {},
        }


@dataclass
class Position:
    """Trading position."""

    symbol: str
    side: PositionSide
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float

    @property
    def market_value(self) -> float:
        """Calculate market value."""
        return self.quantity * self.current_price

    @property
    def total_pnl(self) -> float:
        """Calculate total P&L."""
        return self.unrealized_pnl + self.realized_pnl


@dataclass
class StrategyResult:
    """Strategy backtest result."""

    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    signals: List[Signal]
    equity_curve: pd.Series

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_return": self.total_return,
            "sharpe_ratio": self.sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "win_rate": self.win_rate,
            "total_trades": self.total_trades,
            "signals": [signal.to_dict() for signal in self.signals],
            "equity_curve": self.equity_curve.to_dict(),
        }


@dataclass
class StrategyConfig:
    """Strategy configuration."""

    name: str
    symbol: str
    timeframe: str
    cash: float
    max_position_size: float
    parameters: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "cash": self.cash,
            "max_position_size": self.max_position_size,
            "parameters": self.parameters,
        }
