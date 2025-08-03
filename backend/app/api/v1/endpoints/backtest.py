"""Backtest API endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Depends
import structlog

from ....core.database import get_db
from ....models.schemas.common import DataResponse
from ....models.schemas.backtest import BacktestRequest
from ....services.backtest.service import BacktestService

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/", response_model=DataResponse[Dict[str, Any]])
async def run_backtest(
    request: BacktestRequest, db=Depends(get_db)
) -> DataResponse[Dict[str, Any]]:
    """Run a backtest with the specified parameters."""
    try:
        backtest_service = BacktestService()

        result = backtest_service.run_backtest(
            symbol=request.symbol,
            strategy_name=request.strategy,
            timeframe=request.timeframe,
            days=request.days,
        )

        return DataResponse(
            success=True, data=result, message="Backtest completed successfully"
        )

    except Exception as e:
        logger.error("Backtest failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies", response_model=DataResponse[Dict[str, Any]])
async def get_available_strategies() -> DataResponse[Dict[str, Any]]:
    """Get list of available trading strategies."""
    try:
        backtest_service = BacktestService()
        strategies = backtest_service.get_available_strategies()

        return DataResponse(
            success=True,
            data={"strategies": strategies},
            message="Strategies retrieved successfully",
        )

    except Exception as e:
        logger.error("Failed to get strategies", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies/{strategy_name}/parameters", response_model=DataResponse[Dict[str, Any]])
async def get_strategy_parameters(strategy_name: str) -> DataResponse[Dict[str, Any]]:
    """Get parameters for a specific strategy."""
    try:
        backtest_service = BacktestService()
        parameters = backtest_service.get_strategy_parameters(strategy_name)

        if parameters is None:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy_name} not found")

        return DataResponse(
            success=True,
            data={"parameters": parameters},
            message="Strategy parameters retrieved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get strategy parameters", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
