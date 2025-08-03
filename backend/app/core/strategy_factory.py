"""Strategy factory for creating and managing trading strategies."""

from typing import Any, Dict, List, Optional, Type
import importlib
import sys
import os
import structlog

from .models import StrategyConfig
from .strategy import BaseStrategy


class StrategyFactory:
    """Factory for creating and managing trading strategies."""

    def __init__(self):
        """Initialize strategy factory."""
        self.logger = structlog.get_logger(self.__class__.__name__)
        self._strategies: Dict[str, Type[BaseStrategy]] = {}
        self._register_default_strategies()

    def _register_default_strategies(self):
        """Register default strategies."""
        try:
            # Import strategies from local strategies directory
            from ..strategies.cdc_actionzone import CDCActionZoneStrategy
            
            self.register_strategy("cdc_actionzone", CDCActionZoneStrategy)
            self.logger.info("Default strategies registered")
        except ImportError as e:
            self.logger.warning("Could not import default strategies", error=str(e))

    def register_strategy(self, name: str, strategy_class: Type[BaseStrategy]) -> None:
        """Register a strategy class."""
        self._strategies[name] = strategy_class
        self.logger.info("Strategy registered", name=name)

    def create_strategy(self, name: str, config: StrategyConfig) -> Optional[BaseStrategy]:
        """Create a strategy instance."""
        if name not in self._strategies:
            self.logger.error("Strategy not found", name=name)
            return None

        try:
            strategy_class = self._strategies[name]
            strategy = strategy_class(config)
            self.logger.info("Strategy created", name=name, symbol=config.symbol)
            return strategy
        except Exception as e:
            self.logger.error("Failed to create strategy", name=name, error=str(e))
            return None

    def get_available_strategies(self) -> List[Dict[str, Any]]:
        """Get list of available strategies with their parameters."""
        strategies = []
        
        for name, strategy_class in self._strategies.items():
            # Get default parameters from strategy class if available
            default_params = {}
            if hasattr(strategy_class, 'get_default_parameters'):
                default_params = strategy_class.get_default_parameters()
            
            strategies.append({
                "name": name,
                "display_name": name.replace('_', ' ').title(),
                "description": f"{name.replace('_', ' ').title()} strategy",
                "parameters": default_params,
                "class": strategy_class.__name__,
            })
        
        return strategies

    def get_strategy_parameters(self, name: str) -> Optional[Dict[str, Any]]:
        """Get parameters for a specific strategy."""
        if name not in self._strategies:
            return None
            
        strategy_class = self._strategies[name]
        if hasattr(strategy_class, 'get_default_parameters'):
            return strategy_class.get_default_parameters()
        return {}


# Global strategy factory instance
strategy_factory = StrategyFactory() 