"""
Configuration module for Prisma Web3 Python package.
Loads database configuration from environment variables.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file if exists
load_dotenv()


class Config:
    """Configuration class for database settings."""

    def __init__(self):
        self._database_url: Optional[str] = None

    @property
    def database_url(self) -> str:
        """
        Get database URL from environment variable.

        Returns:
            str: PostgreSQL database URL

        Raises:
            ValueError: If DATABASE_URL is not set
        """
        if self._database_url:
            return self._database_url

        url = os.environ.get("DATABASE_URL")
        if not url:
            raise ValueError(
                "DATABASE_URL environment variable is not set. "
                "Please set it in your environment or .env file."
            )

        # Convert sync URL to async if needed
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)

        self._database_url = url
        return self._database_url

    def set_database_url(self, url: str):
        """
        Manually set database URL (useful for testing).

        Args:
            url: Database connection URL
        """
        self._database_url = url


# Global config instance
config = Config()
