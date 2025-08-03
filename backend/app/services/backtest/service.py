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

    def run_backtest(
        self,
        symbol: str,
        strategy_name: str,
        timeframe: str,
        days: int,
        initial_cash: float = 100000,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run a backtest and return detailed results."""
        try:
            self.logger.info(
                "Starting backtest",
                symbol=symbol,
                strategy_name=strategy_name,
                timeframe=timeframe,
                days=days,
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
                name=strategy_name,
                symbol=symbol,
                timeframe=timeframe,
                cash=initial_cash,
                max_position_size=0.1,  # 10% of cash per trade
                parameters=parameters or {},
            )

            # Create and run strategy
            strategy = strategy_factory.create_strategy(strategy_name, config)
            if not strategy:
                raise ValueError(f"Strategy {strategy_name} not found")

            # Run backtest
            result = strategy.run_backtest(data)

            # Generate detailed report
            from ...core.backtest_report import BacktestReport
            report = BacktestReport(result, initial_cash)
            summary = report.generate_summary()

            self.logger.info(
                "Backtest completed successfully",
                total_return=f"{result.total_return:.2%}",
                sharpe_ratio=f"{result.sharpe_ratio:.2f}",
                total_trades=result.total_trades,
            )

            return {
                "summary": summary,
                "trades": report.generate_trade_list(),
                "charts": self._generate_charts(data, result),
                "metadata": {
                    "symbol": symbol,
                    "strategy": strategy_name,
                    "timeframe": timeframe,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "initial_cash": initial_cash,
                    "parameters": parameters or {},
                },
            }

        except Exception as e:
            self.logger.error("Backtest failed", error=str(e))
            raise

    def _generate_charts(self, data: pd.DataFrame, result) -> Dict[str, Any]:
        """Generate chart data for visualization."""
        # Equity curve chart
        equity_data = {
            "x": [d.isoformat() for d in result.equity_curve.index],
            "y": result.equity_curve.values.tolist(),
        }

        # Price chart with signals
        price_data = {
            "x": [d.isoformat() for d in data.index],
            "open": data["open"].values.tolist(),
            "high": data["high"].values.tolist(),
            "low": data["low"].values.tolist(),
            "close": data["close"].values.tolist(),
            "volume": data["volume"].values.tolist(),
        }

        # Add signals to price chart
        buy_signals = []
        sell_signals = []
        
        for signal in result.signals:
            signal_data = {
                "x": signal.timestamp.isoformat(),
                "y": signal.price,
                "text": "BUY" if signal.side.value == "buy" else "SELL",
            }
            
            if signal.side.value == "buy":
                buy_signals.append(signal_data)
            else:
                sell_signals.append(signal_data)

        price_data["signals"] = {
            "buy": buy_signals,
            "sell": sell_signals,
        }

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
            "price": {
                "type": "candlestick",
                "data": price_data,
                "layout": {
                    "title": f"Price Chart with Signals",
                    "xaxis": {"title": "Date"},
                    "yaxis": {"title": "Price ($)"},
                },
            },
        }

    def get_available_strategies(self) -> List[Dict[str, Any]]:
        """Get list of available strategies."""
        return strategy_factory.get_available_strategies()

    def get_strategy_parameters(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """Get parameters for a specific strategy."""
        return strategy_factory.get_strategy_parameters(strategy_name)
