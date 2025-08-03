"""
Application configuration management.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings with environment variable support."""

    # Application
    app_name: str = Field(default="Trading Bot API", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Database
    database_url: str = Field(
        default="file:./data/trading_bot.db", description="Database connection URL"
    )

    # Alpaca API
    alpaca_api_key: Optional[str] = Field(default=None, description="Alpaca API key")
    alpaca_secret_key: Optional[str] = Field(
        default=None, description="Alpaca secret key"
    )
    alpaca_base_url: str = Field(
        default="https://paper-api.alpaca.markets", description="Alpaca API base URL"
    )

    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens",
    )
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time in minutes"
    )

    # CORS
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )


def get_settings() -> Settings:
    """Get application settings from environment variables."""
    return Settings(
        app_name=os.getenv("APP_NAME", "Trading Bot API"),
        version=os.getenv("VERSION", "1.0.0"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        database_url=os.getenv("DATABASE_URL", "file:./data/trading_bot.db"),
        alpaca_api_key=os.getenv("ALPACA_API_KEY"),
        alpaca_secret_key=os.getenv("ALPACA_SECRET_KEY"),
        alpaca_base_url=os.getenv(
            "ALPACA_BASE_URL", "https://paper-api.alpaca.markets"
        ),
        secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        allowed_origins=os.getenv(
            "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
        ).split(","),
    )


# Global settings instance
config = get_settings()
