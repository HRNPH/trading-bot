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
        """Calculate trading signals based on CDC ActionZone logic (matching Pine Script)."""
        indicators = self.get_indicators(data)

        signals = []

        # Calculate buy/sell conditions (exact match to Pine Script)
        buycond = indicators["green"] & (~indicators["green"].shift(1).fillna(False))
        sellcond = indicators["red"] & (~indicators["red"].shift(1).fillna(False))

        # Calculate bars since last buy/sell condition (equivalent to ta.barssince in Pine Script)
        def bars_since(condition_series):
            """Calculate bars since last True condition."""
            result = pd.Series(index=condition_series.index, dtype=float)
            last_true_idx = None

            for i, (idx, value) in enumerate(condition_series.items()):
                if value:
                    last_true_idx = i
                    result.iloc[i] = 0
                elif last_true_idx is not None:
                    result.iloc[i] = i - last_true_idx
                else:
                    result.iloc[i] = float("inf")  # No previous occurrence
            return result

        bars_since_buy = bars_since(buycond)
        bars_since_sell = bars_since(sellcond)

        # Determine trend (exact match to Pine Script logic)
        bullish = bars_since_buy < bars_since_sell
        bearish = bars_since_sell < bars_since_buy

        # Generate buy/sell signals (exact match to Pine Script)
        buy = bearish.shift(1).fillna(False) & buycond
        sell = bullish.shift(1).fillna(False) & sellcond

        # Generate signals
        for i, (timestamp, row) in enumerate(data.iterrows()):
            if i == 0:
                continue

            # Buy signal: bearish[1] and buycond (exact Pine Script logic)
            if buy.iloc[i]:
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
                        "was_bearish": bearish.iloc[i - 1] if i > 0 else False,
                        "buycond": buycond.iloc[i],
                    },
                )
                signals.append(signal)
                self.logger.info(
                    "Buy signal generated",
                    timestamp=timestamp,
                    price=row["close"],
                    zone="green",
                    was_bearish=bearish.iloc[i - 1] if i > 0 else False,
                )

            # Sell signal: bullish[1] and sellcond (exact Pine Script logic)
            elif sell.iloc[i]:
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
                        "was_bullish": bullish.iloc[i - 1] if i > 0 else False,
                        "sellcond": sellcond.iloc[i],
                    },
                )
                signals.append(signal)
                self.logger.info(
                    "Sell signal generated",
                    timestamp=timestamp,
                    price=row["close"],
                    zone="red",
                    was_bullish=bullish.iloc[i - 1] if i > 0 else False,
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
