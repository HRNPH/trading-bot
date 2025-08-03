"""Trading service for real-time trading operations."""

import asyncio
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog

from ...core.strategy_factory import strategy_factory
from ...core.models import StrategyConfig
from ...trading.live_trader import LiveTrader

logger = structlog.get_logger(__name__)


class TradingService:
    """Service for real-time trading operations."""

    def __init__(self):
        """Initialize trading service."""
        self.is_trading = False
        self.current_symbol = None
        self.current_strategy = None
        self.start_time = None
        self.live_trader = None
        self.logger = logger

    def start_live_trading(
        self,
        symbol: str,
        strategy_name: str,
        timeframe: str,
        initial_cash: float = 100000,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Start live trading with the specified strategy."""
        try:
            if self.is_trading:
                return {"success": False, "error": "Trading already in progress"}

            # Create strategy configuration
            config = StrategyConfig(
                name=strategy_name,
                symbol=symbol,
                timeframe=timeframe,
                cash=initial_cash,
                max_position_size=0.1,  # 10% of cash per trade
                parameters=parameters or {},
            )

            # Create strategy instance
            strategy = strategy_factory.create_strategy(strategy_name, config)
            if not strategy:
                return {"success": False, "error": f"Strategy {strategy_name} not found"}

            # Create live trader
            self.live_trader = LiveTrader(strategy)
            
            # Start trading in background thread
            def start_trading_thread():
                asyncio.run(self.live_trader.start_trading())

            self.trading_thread = threading.Thread(target=start_trading_thread, daemon=True)
            self.trading_thread.start()

            # Update state
            self.is_trading = True
            self.current_symbol = symbol
            self.current_strategy = strategy_name
            self.start_time = datetime.now()

            self.logger.info(
                "Live trading started",
                symbol=symbol,
                strategy=strategy_name,
                timeframe=timeframe,
            )

            return {
                "success": True,
                "message": f"Live trading started for {symbol} with {strategy_name} strategy",
            }

        except Exception as e:
            self.logger.error("Failed to start live trading", error=str(e))
            return {"success": False, "error": str(e)}

    def stop_live_trading(self) -> Dict[str, Any]:
        """Stop live trading."""
        try:
            if not self.is_trading:
                return {"success": False, "error": "No trading session active"}

            # Stop live trader
            if self.live_trader:
                asyncio.run(self.live_trader.stop_trading())

            self.is_trading = False
            self.current_symbol = None
            self.current_strategy = None
            self.start_time = None
            self.live_trader = None

            self.logger.info("Live trading stopped")
            return {"success": True, "message": "Live trading stopped"}

        except Exception as e:
            self.logger.error("Failed to stop live trading", error=str(e))
            return {"success": False, "error": str(e)}

    def get_live_status(self) -> Dict[str, Any]:
        """Get current live trading status."""
        try:
            if not self.is_trading or not self.live_trader:
                return {"is_trading": False, "message": "No active trading session"}

            # Get portfolio summary
            portfolio = self.live_trader.get_portfolio_summary()
            
            # Get performance metrics
            performance = self.live_trader.get_performance_metrics()
            
            # Get recent trades
            recent_trades = self.live_trader.get_trade_history()
            
            # Get price history
            price_history = self.live_trader.get_price_history()

            return {
                "is_trading": True,
                "portfolio": portfolio,
                "performance": performance,
                "recent_trades": recent_trades,
                "price_history": price_history,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error("Failed to get live status", error=str(e))
            return {"is_trading": False, "error": str(e)}

    def get_trading_status(self) -> Dict[str, Any]:
        """Get overall trading service status."""
        return {
            "is_trading": self.is_trading,
            "current_symbol": self.current_symbol,
            "current_strategy": self.current_strategy,
            "start_time": self.start_time.isoformat() if self.start_time else None,
        }
