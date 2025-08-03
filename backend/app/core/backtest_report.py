"""Detailed backtest report generator."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import structlog

from .models import OrderSide, Signal, StrategyResult


class BacktestReport:
    """Generate detailed backtest reports with trade analysis."""

    def __init__(self, result: StrategyResult, initial_cash: float) -> None:
        """Initialize backtest report."""
        self.result = result
        self.initial_cash = initial_cash
        self.logger = structlog.get_logger(self.__class__.__name__)

        # Analyze trades
        self.trades = self._analyze_trades()
        self.monthly_returns = self._calculate_monthly_returns()
        self.drawdown_periods = self._calculate_drawdown_periods()

    def _analyze_trades(self) -> List[Dict[str, Any]]:
        """Analyze individual trades for detailed reporting."""
        trades = []
        current_position = None

        for signal in self.result.signals:
            if signal.side == OrderSide.BUY:
                # Open position
                current_position = {
                    "entry_time": signal.timestamp,
                    "entry_price": signal.price,
                    "entry_signal": signal.signal_type,
                    "quantity": signal.quantity,
                    "exit_time": None,
                    "exit_price": None,
                    "exit_signal": None,
                    "profit_loss": None,
                    "profit_loss_pct": None,
                    "duration_days": None,
                }
            elif signal.side == OrderSide.SELL and current_position:
                # Close position
                current_position["exit_time"] = signal.timestamp
                current_position["exit_price"] = signal.price
                current_position["exit_signal"] = signal.signal_type

                # Calculate P&L
                entry_value = float(current_position["entry_price"]) * float(
                    current_position["quantity"]
                )
                exit_value = float(current_position["exit_price"]) * float(
                    current_position["quantity"]
                )
                profit_loss = exit_value - entry_value
                profit_loss_pct = (profit_loss / entry_value) * 100

                current_position["profit_loss"] = profit_loss
                current_position["profit_loss_pct"] = profit_loss_pct
                current_position["duration_days"] = (
                    signal.timestamp - current_position["entry_time"]
                ).days

                trades.append(current_position)
                current_position = None

        # Handle open position at end
        if current_position:
            current_position["status"] = "OPEN"
            trades.append(current_position)

        return trades

    def _calculate_monthly_returns(self) -> pd.Series:
        """Calculate monthly returns."""
        returns = self.result.equity_curve.pct_change().dropna()
        monthly_returns = returns.resample("M").apply(lambda x: (1 + x).prod() - 1)
        return monthly_returns

    def _calculate_drawdown_periods(self) -> List[Dict[str, Any]]:
        """Calculate drawdown periods."""
        equity = self.result.equity_curve
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max

        drawdown_periods = []
        in_drawdown = False
        start_date = None
        max_drawdown = 0

        for date, dd in drawdown.items():
            if dd < 0 and not in_drawdown:
                # Start of drawdown
                in_drawdown = True
                start_date = date
                max_drawdown = dd
            elif dd < 0 and in_drawdown:
                # Continue drawdown
                if dd < max_drawdown:
                    max_drawdown = dd
            elif dd >= 0 and in_drawdown:
                # End of drawdown
                drawdown_periods.append(
                    {
                        "start_date": start_date,
                        "end_date": date,
                        "max_drawdown": max_drawdown,
                        "duration_days": (date - start_date).days,
                    }
                )
                in_drawdown = False
                max_drawdown = 0

        return drawdown_periods

    def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive backtest summary."""
        trades = self.trades
        closed_trades = [t for t in trades if t.get("exit_time") is not None]
        open_trades = [t for t in trades if t.get("status") == "OPEN"]

        # Calculate trade statistics
        if closed_trades:
            winning_trades = [t for t in closed_trades if t["profit_loss"] > 0]
            losing_trades = [t for t in closed_trades if t["profit_loss"] <= 0]

            avg_win = (
                sum(t["profit_loss"] for t in winning_trades) / len(winning_trades)
                if winning_trades
                else 0
            )
            avg_loss = (
                sum(t["profit_loss"] for t in losing_trades) / len(losing_trades)
                if losing_trades
                else 0
            )
            max_win = (
                max(t["profit_loss"] for t in closed_trades) if closed_trades else 0
            )
            max_loss = (
                min(t["profit_loss"] for t in closed_trades) if closed_trades else 0
            )
            avg_duration = (
                sum(t["duration_days"] for t in closed_trades) / len(closed_trades)
                if closed_trades
                else 0
            )
        else:
            avg_win = avg_loss = max_win = max_loss = avg_duration = 0
            winning_trades = losing_trades = []

        # Calculate risk metrics
        returns = self.result.equity_curve.pct_change().dropna()
        volatility = returns.std() * (252**0.5)
        var_95 = returns.quantile(0.05)
        cvar_95 = returns[returns <= var_95].mean()

        summary = {
            "performance": {
                "total_return": self.result.total_return,
                "annualized_return": self.result.total_return * (252 / len(returns)),
                "sharpe_ratio": self.result.sharpe_ratio,
                "max_drawdown": self.result.max_drawdown,
                "win_rate": self.result.win_rate,
                "profit_factor": (
                    abs(avg_win / avg_loss) if avg_loss != 0 else float("inf")
                ),
            },
            "risk_metrics": {
                "volatility": volatility,
                "var_95": var_95,
                "cvar_95": cvar_95,
                "calmar_ratio": (
                    (self.result.total_return * (252 / len(returns)))
                    / abs(self.result.max_drawdown)
                    if self.result.max_drawdown != 0
                    else 0
                ),
            },
            "trade_statistics": {
                "total_trades": len(closed_trades),
                "winning_trades": len(winning_trades),
                "losing_trades": len(losing_trades),
                "open_trades": len(open_trades),
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "max_win": max_win,
                "max_loss": max_loss,
                "avg_duration_days": avg_duration,
                "best_trade": (
                    max(closed_trades, key=lambda x: x["profit_loss"])
                    if closed_trades
                    else None
                ),
                "worst_trade": (
                    min(closed_trades, key=lambda x: x["profit_loss"])
                    if closed_trades
                    else None
                ),
            },
            "drawdown_periods": self.drawdown_periods,
            "monthly_returns": self.monthly_returns.to_dict(),
            "trades": trades,
        }

        return summary

    def generate_trade_list(self) -> List[Dict[str, Any]]:
        """Generate detailed trade list for display."""
        trade_list = []

        for i, trade in enumerate(self.trades, 1):
            trade_info = {
                "trade_id": i,
                "entry_time": trade["entry_time"].strftime("%Y-%m-%d %H:%M"),
                "entry_price": f"${trade['entry_price']:.2f}",
                "entry_signal": trade["entry_signal"],
                "quantity": f"{trade['quantity']:.2f}",
                "exit_time": (
                    trade["exit_time"].strftime("%Y-%m-%d %H:%M")
                    if trade.get("exit_time")
                    else "OPEN"
                ),
                "exit_price": (
                    f"${trade['exit_price']:.2f}" if trade.get("exit_price") else "OPEN"
                ),
                "exit_signal": trade.get("exit_signal", "OPEN"),
                "profit_loss": (
                    f"${trade['profit_loss']:.2f}"
                    if trade.get("profit_loss") is not None
                    else "OPEN"
                ),
                "profit_loss_pct": (
                    f"{trade['profit_loss_pct']:.2f}%"
                    if trade.get("profit_loss_pct") is not None
                    else "OPEN"
                ),
                "duration_days": trade.get("duration_days", "OPEN"),
                "status": trade.get("status", "CLOSED"),
            }
            trade_list.append(trade_info)

        return trade_list
