"""Real-time trading service with live data streaming and trade execution."""

import asyncio
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable

import pandas as pd
import structlog
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide as AlpacaOrderSide
from alpaca.data.live import StockDataStream
from alpaca.data.requests import StockLatestQuoteRequest

from ..core.config import config
from ..core.models import OrderSide, Signal, StrategyConfig
from ..core.strategy import BaseStrategy


class LiveTrader:
    """Real-time trading service with live data and trade execution."""

    def __init__(self, strategy: BaseStrategy) -> None:
        """Initialize live trader."""
        self.strategy = strategy
        self.logger = structlog.get_logger(self.__class__.__name__)

        # Initialize Alpaca clients
        self.trading_client = TradingClient(
            api_key=config.alpaca_api_key,
            secret_key=config.alpaca_secret_key,
            paper=True,
        )

        self.data_stream = StockDataStream(
            api_key=config.alpaca_api_key,
            secret_key=config.alpaca_secret_key,
            feed="iex",  # type: ignore
        )

        # Trading state
        self.is_running = False
        self.current_position = 0.0
        self.cash = strategy.config.cash
        self.portfolio_value = strategy.config.cash
        self.trade_history: List[Dict[str, Any]] = []
        self.price_history: List[Dict[str, Any]] = []

        # Callbacks
        self.on_signal_callback: Optional[Callable[[Signal], None]] = None
        self.on_trade_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_price_update_callback: Optional[Callable[[Dict[str, Any]], None]] = None

        self.logger.info("Live trader initialized", symbol=strategy.config.symbol)

    def set_callbacks(
        self,
        on_signal: Optional[Callable[[Signal], None]] = None,
        on_trade: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_price_update: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        """Set callback functions for real-time updates."""
        self.on_signal_callback = on_signal
        self.on_trade_callback = on_trade
        self.on_price_update_callback = on_price_update

    async def start_trading(self) -> None:
        """Start real-time trading."""
        if self.is_running:
            self.logger.warning("Trading already running")
            return

        self.is_running = True
        self.logger.info("Starting live trading", symbol=self.strategy.config.symbol)

        # Subscribe to data stream
        await self.data_stream.subscribe_trades(self._handle_trade_update)
        await self.data_stream.subscribe_quotes(self._handle_quote_update)

        # Start data stream
        await self.data_stream.run()  # type: ignore

    async def stop_trading(self) -> None:
        """Stop real-time trading."""
        if not self.is_running:
            return

        self.is_running = False
        await self.data_stream.stop()
        self.logger.info("Live trading stopped")

    async def _handle_trade_update(self, trade: Any) -> None:
        """Handle incoming trade data."""
        if not self.is_running:
            return

        # Update price history
        price_data = {
            "timestamp": trade.timestamp,
            "price": trade.price,
            "volume": trade.size,
            "symbol": trade.symbol,
        }

        self.price_history.append(price_data)

        # Keep only last 1000 price points
        if len(self.price_history) > 1000:
            self.price_history = self.price_history[-1000:]

        # Call price update callback
        if self.on_price_update_callback:
            self.on_price_update_callback(price_data)

        # Check for signals every 10 price updates
        if len(self.price_history) % 10 == 0:
            await self._check_for_signals()

    async def _handle_quote_update(self, quote: Any) -> None:
        """Handle incoming quote data."""
        if not self.is_running:
            return

        # Update portfolio value
        if self.current_position > 0:
            self.portfolio_value = self.cash + (self.current_position * quote.ask_price)
        else:
            self.portfolio_value = self.cash

    async def _check_for_signals(self) -> None:
        """Check for trading signals based on current price data."""
        if len(self.price_history) < 50:  # Need minimum data
            return

        # Convert price history to DataFrame
        df = pd.DataFrame(self.price_history)
        df = df.set_index("timestamp")

        # Resample to strategy timeframe
        timeframe_map = {
            "1Min": "1T",
            "5Min": "5T",
            "15Min": "15T",
            "1Hour": "1H",
            "1Day": "1D",
        }

        resample_freq = timeframe_map.get(self.strategy.config.timeframe, "1T")
        df_resampled = (
            df.resample(resample_freq).agg({"price": "ohlc", "volume": "sum"}).dropna()
        )

        # Rename columns to match expected format
        df_resampled.columns = ["open", "high", "low", "close", "volume"]

        # Calculate signals
        signals = self.strategy.calculate_signals(df_resampled)

        # Process new signals
        for signal in signals:
            if signal.timestamp > datetime.now() - timedelta(
                minutes=5
            ):  # Recent signal
                await self._execute_signal(signal)

    async def _execute_signal(self, signal: Signal) -> None:
        """Execute a trading signal."""
        try:
            if signal.side == OrderSide.BUY and self.current_position <= 0:
                # Buy signal
                shares_to_buy = (
                    self.cash * self.strategy.config.max_position_size / signal.price
                )

                if shares_to_buy > 0:
                    # Place market order
                    order_request = MarketOrderRequest(
                        symbol=signal.symbol,
                        qty=shares_to_buy,
                        side=AlpacaOrderSide.BUY,
                    )

                    order = self.trading_client.submit_order(order_request)

                    # Update position
                    self.current_position += shares_to_buy
                    self.cash -= shares_to_buy * signal.price

                    # Record trade
                    order_id = (
                        getattr(order, "id", "unknown")
                        if hasattr(order, "id")
                        else "unknown"
                    )
                    trade_record = {
                        "timestamp": signal.timestamp,
                        "type": "BUY",
                        "price": signal.price,
                        "quantity": shares_to_buy,
                        "value": shares_to_buy * signal.price,
                        "order_id": order_id,
                        "signal_type": signal.signal_type,
                    }

                    self.trade_history.append(trade_record)

                    self.logger.info(
                        "Buy order executed",
                        price=signal.price,
                        quantity=shares_to_buy,
                        order_id=order_id,
                    )

                    # Call signal callback
                    if self.on_signal_callback:
                        self.on_signal_callback(signal)

                    # Call trade callback
                    if self.on_trade_callback:
                        self.on_trade_callback(trade_record)

            elif signal.side == OrderSide.SELL and self.current_position > 0:
                # Sell signal
                order_request = MarketOrderRequest(
                    symbol=signal.symbol,
                    qty=self.current_position,
                    side=AlpacaOrderSide.SELL,
                )

                order = self.trading_client.submit_order(order_request)
                sell_order_id = (
                    getattr(order, "id", "unknown")
                    if hasattr(order, "id")
                    else "unknown"
                )

                # Calculate proceeds
                proceeds = self.current_position * signal.price

                # Update position
                self.cash += proceeds
                self.current_position = 0.0

                # Record trade
                trade_record = {
                    "timestamp": signal.timestamp,
                    "type": "SELL",
                    "price": signal.price,
                    "quantity": self.current_position,
                    "value": proceeds,
                    "order_id": sell_order_id,
                    "signal_type": signal.signal_type,
                }

                self.trade_history.append(trade_record)

                self.logger.info(
                    "Sell order executed",
                    price=signal.price,
                    quantity=self.current_position,
                    order_id=sell_order_id,
                )

                # Call signal callback
                if self.on_signal_callback:
                    self.on_signal_callback(signal)

                # Call trade callback
                if self.on_trade_callback:
                    self.on_trade_callback(trade_record)

        except Exception as e:
            self.logger.error(
                "Failed to execute signal", error=str(e), signal=signal.signal_type
            )

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get current portfolio summary."""
        return {
            "cash": self.cash,
            "position": self.current_position,
            "portfolio_value": self.portfolio_value,
            "total_trades": len(self.trade_history),
            "current_position_value": self.current_position * self._get_current_price(),
        }

    def get_trade_history(self) -> List[Dict[str, Any]]:
        """Get trade history."""
        return self.trade_history

    def get_price_history(self) -> List[Dict[str, Any]]:
        """Get price history."""
        return self.price_history

    def _get_current_price(self) -> float:
        """Get current price from latest data."""
        if self.price_history:
            price = self.price_history[-1]["price"]
            return float(price) if price is not None else 0.0
        return 0.0

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Calculate real-time performance metrics."""
        if not self.trade_history:
            return {}

        # Calculate basic metrics
        total_trades = len(self.trade_history)
        winning_trades = len([t for t in self.trade_history if t["type"] == "SELL"])

        # Calculate P&L
        total_pnl = 0
        for i in range(0, len(self.trade_history) - 1, 2):
            if i + 1 < len(self.trade_history):
                buy_trade = self.trade_history[i]
                sell_trade = self.trade_history[i + 1]
                if buy_trade["type"] == "BUY" and sell_trade["type"] == "SELL":
                    pnl = sell_trade["value"] - buy_trade["value"]
                    total_pnl += pnl

        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "win_rate": winning_trades / total_trades if total_trades > 0 else 0,
            "total_pnl": total_pnl,
            "current_portfolio_value": self.portfolio_value,
            "initial_cash": self.strategy.config.cash,
            "total_return": (self.portfolio_value - self.strategy.config.cash)
            / self.strategy.config.cash,
        }
