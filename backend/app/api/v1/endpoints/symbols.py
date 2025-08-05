"""Symbol API endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Depends
import structlog

from ....core.database import get_db
from ....models.schemas.common import DataResponse
from ....data.alpaca_provider import AlpacaDataProvider
from datetime import datetime, timedelta
import pandas as pd

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/", response_model=DataResponse[Dict[str, Any]])
async def get_symbols(db=Depends(get_db)) -> DataResponse[Dict[str, Any]]:
    """Get list of available symbols."""
    try:
        # For now, return a static list of symbols
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX"]

        return DataResponse(
            success=True,
            data={"symbols": symbols},
            message="Symbols retrieved successfully",
        )

    except Exception as e:
        logger.error("Failed to get symbols", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/price", response_model=DataResponse[Dict[str, Any]])
async def get_symbol_price_data(
    symbol: str, days: int = 30
) -> DataResponse[Dict[str, Any]]:
    """Get price data for a symbol."""
    try:
        data_provider = AlpacaDataProvider()

        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        data = data_provider.get_bars(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe="1Day",
        )

        if data.empty:
            raise HTTPException(
                status_code=404, detail=f"No data available for {symbol}"
            )

        # Format data for TradingView chart
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

        # Calculate CDC ActionZone indicators only
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

        return DataResponse(
            success=True,
            data={
                "symbol": symbol,
                "candlestick": {
                    "data": candlestick_data,
                    "indicators": indicators,
                },
            },
            message=f"Price data for {symbol} retrieved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get symbol price data", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
