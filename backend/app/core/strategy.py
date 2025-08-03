"""Base strategy class for implementing PineScript strategies."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import structlog

from .models import Bar, OrderSide, Signal, StrategyConfig, StrategyResult


class BaseStrategy(ABC):
    """Base class for all trading strategies."""

    def __init__(self, config: StrategyConfig) -> None:
        """Initialize strategy with configuration."""
        self.config = config
        self.logger = structlog.get_logger(f"{self.__class__.__name__}")
        self.signals: List[Signal] = []
        self.current_position: Optional[str] = None  # "long", "short", or None

        self.logger.info(
            "Strategy initialized",
            name=config.name,
            symbol=config.symbol,
            parameters=config.parameters,
        )

    @abstractmethod
    def calculate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """Calculate trading signals from market data."""
        pass

    @abstractmethod
    def get_indicators(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate technical indicators."""
        pass

    def run_backtest(self, data: pd.DataFrame) -> StrategyResult:
        """Run backtest on historical data."""
        self.logger.info(
            "Starting backtest", symbol=self.config.symbol, data_points=len(data)
        )

        # Calculate indicators
        indicators = self.get_indicators(data)

        # Calculate signals
        signals = self.calculate_signals(data)

        # Simulate trading
        equity_curve = self._simulate_trading(data, signals)

        # Calculate performance metrics
        total_return = (
            equity_curve.iloc[-1] - equity_curve.iloc[0]
        ) / equity_curve.iloc[0]
        returns = equity_curve.pct_change().dropna()
        sharpe_ratio = (
            returns.mean() / returns.std() * (252**0.5) if returns.std() > 0 else 0
        )

        # Calculate max drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # Calculate win rate
        winning_trades = len([s for s in signals if s.side == OrderSide.BUY])
        total_trades = len(signals)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        result = StrategyResult(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=total_trades,
            signals=signals,
            equity_curve=equity_curve,
        )

        self.logger.info(
            "Backtest completed",
            total_return=f"{total_return:.2%}",
            sharpe_ratio=f"{sharpe_ratio:.2f}",
            max_drawdown=f"{max_drawdown:.2%}",
            win_rate=f"{win_rate:.2%}",
            total_trades=total_trades,
        )

        return result

    def _simulate_trading(self, data: pd.DataFrame, signals: List[Signal]) -> pd.Series:
        """Simulate trading based on signals."""
        equity = pd.Series(index=data.index, dtype=float)
        equity.iloc[0] = self.config.cash

        current_cash = self.config.cash
        current_position: float = 0.0
        current_price: float = 0.0

        for i, (timestamp, row) in enumerate(data.iterrows()):
            # Update current price
            current_price = row["close"]

            # Check for signals at this timestamp
            for signal in signals:
                if signal.timestamp == timestamp:
                    if signal.side == OrderSide.BUY and current_position <= 0:
                        # Buy signal
                        shares_to_buy = (
                            current_cash * self.config.max_position_size / current_price
                        )
                        cost = shares_to_buy * current_price
                        if cost <= current_cash:
                            current_position += shares_to_buy
                            current_cash -= cost
                            self.logger.debug(
                                "Buy signal executed",
                                shares=shares_to_buy,
                                price=current_price,
                                cost=cost,
                            )

                    elif signal.side == OrderSide.SELL and current_position > 0:
                        # Sell signal
                        proceeds = current_position * current_price
                        current_cash += proceeds
                        current_position = 0
                        self.logger.debug(
                            "Sell signal executed",
                            shares=current_position,
                            price=current_price,
                            proceeds=proceeds,
                        )

            # Calculate current equity
            equity.iloc[i] = current_cash + (current_position * current_price)

        return equity

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information."""
        return {
            "name": self.config.name,
            "symbol": self.config.symbol,
            "timeframe": self.config.timeframe,
            "parameters": self.config.parameters,
            "class": self.__class__.__name__,
        }
