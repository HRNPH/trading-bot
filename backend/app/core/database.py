"""
Database connection and management.
"""

from contextlib import contextmanager
from typing import Generator

import structlog
from prisma import Prisma

from .config import config

logger = structlog.get_logger(__name__)


class DatabaseManager:
    """Database connection manager."""

    def __init__(self) -> None:
        self.prisma = Prisma()
        self._is_connected = False

    def connect(self) -> None:
        """Connect to the database."""
        try:
            self.prisma.connect()
            self._is_connected = True
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error("Failed to connect to database", error=str(e))
            raise

    def disconnect(self) -> None:
        """Disconnect from the database."""
        try:
            self.prisma.disconnect()
            self._is_connected = False
            logger.info("Database disconnected successfully")
        except Exception as e:
            logger.error("Failed to disconnect from database", error=str(e))

    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._is_connected

    def get_client(self) -> Prisma:
        """Get the Prisma client instance."""
        if not self._is_connected:
            raise RuntimeError("Database not connected")
        return self.prisma


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Prisma:
    """Get database client for dependency injection."""
    if not db_manager.is_connected:
        db_manager.connect()
    return db_manager.get_client()


@contextmanager
def get_db_context() -> Generator[Prisma, None, None]:
    """Get database connection context manager."""
    if not db_manager.is_connected:
        db_manager.connect()

    try:
        yield db_manager.get_client()
    except Exception as e:
        logger.error("Database operation failed", error=str(e))
        raise


def init_db() -> None:
    """Initialize database connection."""
    db_manager.connect()


def close_db() -> None:
    """Close database connection."""
    db_manager.disconnect()
