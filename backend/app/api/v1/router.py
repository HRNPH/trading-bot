"""
Main API router for v1 endpoints.
"""

from fastapi import APIRouter

from .endpoints import symbols, backtest, trading

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(symbols.router, prefix="/symbols", tags=["symbols"])
api_router.include_router(backtest.router, prefix="/backtest", tags=["backtest"])
api_router.include_router(trading.router, prefix="/trading", tags=["trading"])
