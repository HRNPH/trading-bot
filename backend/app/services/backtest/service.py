"""Backtest service for running strategy backtests."""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import structlog

from ...core.strategy_factory import strategy_factory
from ...core.models import StrategyConfig
from ...data.alpaca_provider import AlpacaDataProvider

logger = structlog.get_logger(__name__)


class BacktestService:
    """Service for running backtests and generating reports."""

    def __init__(self):
        """Initialize backtest service."""
        self.logger = logger
        self.data_provider = AlpacaDataProvider()
        self.strategy_factory = strategy_factory

    async def run_backtest(
        self,
        symbol: str,
        strategy: str,
        timeframe: str = "1Day",
        days: int = 90,
        initial_balance: float = 100000,
    ) -> Dict[str, Any]:
        """Run a backtest and return detailed results."""
        try:
            self.logger.info(
                "Starting backtest",
                symbol=symbol,
                strategy=strategy,
                timeframe=timeframe,
                days=days,
                initial_balance=initial_balance,
            )

            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            data = self.data_provider.get_bars(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                timeframe=timeframe,
            )

            if data.empty:
                raise ValueError(f"No data available for {symbol}")

            # Create strategy configuration
            config = StrategyConfig(
                name=strategy,
                symbol=symbol,
                timeframe=timeframe,
                cash=initial_balance,
                max_position_size=0.1,  # 10% of cash per trade
                parameters={},
            )

            # Get strategy instance
            strategy_instance = self.strategy_factory.create_strategy(strategy, config)
            if not strategy_instance:
                raise ValueError(f"Strategy '{strategy}' not found")

            # Run backtest
            portfolio = strategy_instance.run_backtest(data)

            # Generate report
            from ...core.backtest_report import BacktestReport

            report = BacktestReport(portfolio, initial_balance)
            summary = report.generate_summary()

            self.logger.info(
                "Backtest completed",
                symbol=symbol,
                strategy=strategy,
                total_return=summary["performance"]["total_return"],
                total_trades=summary["trade_statistics"]["total_trades"],
            )

            return {
                "summary": summary,
                "trades": report.generate_trade_list(),
                "charts": self._generate_charts(data, portfolio, initial_balance),
                "metadata": {
                    "symbol": symbol,
                    "strategy": strategy,
                    "timeframe": timeframe,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "initial_balance": initial_balance,
                },
            }

        except Exception as e:
            self.logger.error("Backtest failed", error=str(e))
            raise

    def _generate_charts(self, data: pd.DataFrame, result, initial_balance: float) -> Dict[str, Any]:
        """Generate chart data for visualization."""
        # Equity curve chart - both balance and percentage
        equity_values = result.equity_curve.values.tolist()
        equity_dates = [d.isoformat() for d in result.equity_curve.index]
        
        # Calculate percentage returns
        percentage_values = [((value / initial_balance) - 1) * 100 for value in equity_values]
        
        equity_data = {
            "x": equity_dates,
            "y": equity_values,
            "percentage": percentage_values,
        }

        # Candlestick data for TradingView
        candlestick_data = []
        for idx, row in data.iterrows():
            candlestick_data.append(
                {
                    "time": idx.isoformat(),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                }
            )

        # Calculate indicators
        indicators = self._calculate_indicators(data)

        # Add signals to candlestick data
        buy_signals = []
        sell_signals = []

        for signal in result.signals:
            signal_data = {
                "time": signal.timestamp.isoformat(),
                "price": signal.price,
                "text": "BUY" if signal.side.value == "buy" else "SELL",
            }

            if signal.side.value == "buy":
                buy_signals.append(signal_data)
            else:
                sell_signals.append(signal_data)

        return {
            "equity": {
                "type": "line",
                "data": equity_data,
                "layout": {
                    "title": "Portfolio Equity Curve",
                    "xaxis": {"title": "Date"},
                    "yaxis": {"title": "Portfolio Value ($)"},
                },
            },
            "candlestick": {
                "type": "candlestick",
                "data": candlestick_data,
                "indicators": indicators,
                "signals": {
                    "buy": buy_signals,
                    "sell": sell_signals,
                },
                "layout": {
                    "title": f"Price Chart with Indicators",
                    "xaxis": {"title": "Date"},
                    "yaxis": {"title": "Price ($)"},
                },
            },
        }

    def _calculate_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators matching the CDC ActionZone strategy exactly."""
        indicators = {}

        # Calculate ONLY the indicators used in CDC ActionZone strategy
        fast_period = 12
        slow_period = 26
        smoothing = 1

        # Calculate smoothed price (same as strategy)
        smoothed_price = data["close"].ewm(span=smoothing).mean()

        # Calculate EMAs (same as strategy) - these are the ONLY indicators in CDC ActionZone
        fast_ma = smoothed_price.ewm(span=fast_period).mean()
        slow_ma = smoothed_price.ewm(span=slow_period).mean()

        # Add Fast EMA (12) - Red line in Pine Script
        indicators["Fast EMA (12)"] = [
            {"time": idx.isoformat(), "value": float(value)}
            for idx, value in fast_ma.items()
            if not pd.isna(value)
        ]

        # Add Slow EMA (26) - Blue line in Pine Script
        indicators["Slow EMA (26)"] = [
            {"time": idx.isoformat(), "value": float(value)}
            for idx, value in slow_ma.items()
            if not pd.isna(value)
        ]

        return indicators

    def get_available_strategies(self) -> List[Dict[str, Any]]:
        """Get list of available strategies."""
        return strategy_factory.get_available_strategies()

    def get_strategy_parameters(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """Get parameters for a specific strategy."""
        return strategy_factory.get_strategy_parameters(strategy_name)
