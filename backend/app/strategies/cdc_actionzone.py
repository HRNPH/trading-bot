"""CDC ActionZone V3 2025 Strategy implementation."""

from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import structlog

from ..core.models import OrderSide, Signal, StrategyConfig
from ..core.strategy import BaseStrategy


class CDCActionZoneStrategy(BaseStrategy):
    """CDC ActionZone V3 2025 Strategy implementation."""

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        """Get default parameters for the strategy."""
        return {
            "fast_period": {"type": "int", "default": 12, "min": 5, "max": 50},
            "slow_period": {"type": "int", "default": 26, "min": 10, "max": 100},
            "smoothing": {"type": "int", "default": 1, "min": 1, "max": 10},
        }

    def __init__(self, config: StrategyConfig) -> None:
        """Initialize CDC ActionZone strategy."""
        super().__init__(config)

        # Extract parameters with defaults
        self.fast_period = config.parameters.get("fast_period", 12)
        self.slow_period = config.parameters.get("slow_period", 26)
        self.smoothing = config.parameters.get("smoothing", 1)

        self.logger.info(
            "CDC ActionZone strategy initialized",
            fast_period=self.fast_period,
            slow_period=self.slow_period,
            smoothing=self.smoothing,
        )

    def get_indicators(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate technical indicators for CDC ActionZone."""
        # Calculate smoothed price
        price = data["close"].ewm(span=self.smoothing).mean()

        # Calculate EMAs
        fast_ma = price.ewm(span=self.fast_period).mean()
        slow_ma = price.ewm(span=self.slow_period).mean()

        # Calculate zones
        bull = fast_ma > slow_ma
        bear = fast_ma < slow_ma

        green = bull & (price > fast_ma)
        blue = bear & (price > fast_ma) & (price > slow_ma)
        light_blue = bear & (price > fast_ma) & (price < slow_ma)
        red = bear & (price < fast_ma)
        orange = bull & (price < fast_ma) & (price < slow_ma)
        yellow = bull & (price < fast_ma) & (price > slow_ma)

        return {
            "price": price,
            "fast_ma": fast_ma,
            "slow_ma": slow_ma,
            "bull": bull,
            "bear": bear,
            "green": green,
            "blue": blue,
            "light_blue": light_blue,
            "red": red,
            "orange": orange,
            "yellow": yellow,
        }

    def calculate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """Calculate trading signals based on CDC ActionZone logic."""
        indicators = self.get_indicators(data)

        signals = []

        # Calculate buy/sell conditions
        buy_condition = indicators["green"] & (
            ~indicators["green"].shift(1).fillna(False)
        )
        sell_condition = indicators["red"] & (~indicators["red"].shift(1).fillna(False))

        # Determine trend - simplified logic
        bullish = (
            buy_condition.rolling(window=5).sum()
            > sell_condition.rolling(window=5).sum()
        )
        bearish = (
            sell_condition.rolling(window=5).sum()
            > buy_condition.rolling(window=5).sum()
        )

        # Generate signals
        for i, (timestamp, row) in enumerate(data.iterrows()):
            if i == 0:
                continue

            # Buy signal: bearish trend ends and buy condition occurs
            if bearish.iloc[i - 1] and buy_condition.iloc[i]:
                signal = Signal(
                    timestamp=timestamp,
                    symbol=self.config.symbol,
                    side=OrderSide.BUY,
                    price=row["close"],
                    quantity=self.config.cash
                    * self.config.max_position_size
                    / row["close"],
                    signal_type="CDC_ActionZone_Buy",
                    metadata={
                        "strategy": "CDC_ActionZone",
                        "fast_ma": indicators["fast_ma"].iloc[i],
                        "slow_ma": indicators["slow_ma"].iloc[i],
                        "zone": "green" if indicators["green"].iloc[i] else "unknown",
                    },
                )
                signals.append(signal)
                self.logger.info(
                    "Buy signal generated",
                    timestamp=timestamp,
                    price=row["close"],
                    zone="green",
                )

            # Sell signal: bullish trend ends and sell condition occurs
            elif bullish.iloc[i - 1] and sell_condition.iloc[i]:
                signal = Signal(
                    timestamp=timestamp,
                    symbol=self.config.symbol,
                    side=OrderSide.SELL,
                    price=row["close"],
                    quantity=0,  # Will be calculated in simulation
                    signal_type="CDC_ActionZone_Sell",
                    metadata={
                        "strategy": "CDC_ActionZone",
                        "fast_ma": indicators["fast_ma"].iloc[i],
                        "slow_ma": indicators["slow_ma"].iloc[i],
                        "zone": "red" if indicators["red"].iloc[i] else "unknown",
                    },
                )
                signals.append(signal)
                self.logger.info(
                    "Sell signal generated",
                    timestamp=timestamp,
                    price=row["close"],
                    zone="red",
                )

        self.logger.info(
            "Signals calculated",
            total_signals=len(signals),
            buy_signals=len([s for s in signals if s.side == OrderSide.BUY]),
            sell_signals=len([s for s in signals if s.side == OrderSide.SELL]),
        )

        return signals

    def get_zone_colors(self, data: pd.DataFrame) -> Dict[str, str]:
        """Get zone colors for visualization."""
        indicators = self.get_indicators(data)

        colors = {}
        for i, timestamp in enumerate(data.index):
            if indicators["green"].iloc[i]:
                colors[timestamp] = "green"
            elif indicators["blue"].iloc[i]:
                colors[timestamp] = "blue"
            elif indicators["light_blue"].iloc[i]:
                colors[timestamp] = "lightblue"
            elif indicators["red"].iloc[i]:
                colors[timestamp] = "red"
            elif indicators["orange"].iloc[i]:
                colors[timestamp] = "orange"
            elif indicators["yellow"].iloc[i]:
                colors[timestamp] = "yellow"
            else:
                colors[timestamp] = "black"

        return colors
