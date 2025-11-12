"""
Database module for async SQLAlchemy setup.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from .config import config
from .base import Base

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    config.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    """
    Initialize database, create all tables if they don't exist.

    Note: In production, use migrations instead of create_all.
    """
    logger.info("Initializing database...")
    try:
        async with engine.begin() as conn:
            # Reflect existing tables
            await conn.run_sync(Base.metadata.reflect)
            # Create new tables (doesn't drop existing ones)
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database initialized successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session with automatic cleanup.

    Usage:
        async with get_db() as session:
            result = await session.execute(query)
            await session.commit()

    Yields:
        AsyncSession: Database session
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def close_db():
    """Close database engine and all connections."""
    await engine.dispose()
    logger.info("Database connections closed.")
