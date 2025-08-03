"""Live trading API endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Depends
import structlog

from ....core.database import get_db
from ....models.schemas.common import DataResponse
from ....models.schemas.trading import LiveTradingRequest
from ....services.trading.service import TradingService

router = APIRouter()
logger = structlog.get_logger(__name__)

# Global trading service instance
trading_service = TradingService()


@router.post("/start", response_model=DataResponse[Dict[str, Any]])
async def start_live_trading(
    request: LiveTradingRequest, db=Depends(get_db)
) -> DataResponse[Dict[str, Any]]:
    """Start live trading with the specified parameters."""
    try:
        result = trading_service.start_live_trading(
            symbol=request.symbol,
            strategy_name=request.strategy,
            timeframe=request.timeframe,
        )

        if result["success"]:
            return DataResponse(success=True, data=result, message=result["message"])
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except Exception as e:
        logger.error("Failed to start live trading", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", response_model=DataResponse[Dict[str, Any]])
async def stop_live_trading() -> DataResponse[Dict[str, Any]]:
    """Stop live trading."""
    try:
        result = trading_service.stop_live_trading()

        if result["success"]:
            return DataResponse(success=True, data=result, message=result["message"])
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except Exception as e:
        logger.error("Failed to stop live trading", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=DataResponse[Dict[str, Any]])
async def get_live_status() -> DataResponse[Dict[str, Any]]:
    """Get current live trading status."""
    try:
        status = trading_service.get_live_status()

        return DataResponse(
            success=True,
            data=status,
            message="Live trading status retrieved successfully",
        )

    except Exception as e:
        logger.error("Failed to get live status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trading-status", response_model=DataResponse[Dict[str, Any]])
async def get_trading_service_status() -> DataResponse[Dict[str, Any]]:
    """Get trading service status."""
    try:
        status = trading_service.get_trading_status()

        return DataResponse(
            success=True,
            data=status,
            message="Trading service status retrieved successfully",
        )

    except Exception as e:
        logger.error("Failed to get trading service status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
