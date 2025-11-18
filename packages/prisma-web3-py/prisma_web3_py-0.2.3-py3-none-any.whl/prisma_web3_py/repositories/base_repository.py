"""
Base repository class with common CRUD operations.
"""

from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..base import Base

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing common database operations.

    Args:
        model: SQLAlchemy model class
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.logger = logger

    def _normalize_chain(self, chain: Optional[str]) -> Optional[str]:
        """
        Normalize chain name to standard format.

        This is a default implementation that subclasses can override.
        Returns the chain as-is by default.

        Args:
            chain: Chain name or abbreviation

        Returns:
            Standardized chain name or original chain
        """
        return chain

    def _prepare_kwargs(self, kwargs: dict) -> dict:
        """
        Prepare kwargs before creating/updating a record.

        Automatically normalizes chain field if present.

        Args:
            kwargs: Model field values

        Returns:
            Prepared kwargs with normalized values
        """
        # Create a copy to avoid modifying the original
        prepared = kwargs.copy()

        # Normalize chain if present and model has chain field
        if 'chain' in prepared and hasattr(self.model, 'chain'):
            prepared['chain'] = self._normalize_chain(prepared['chain'])

        return prepared

    async def create(self, session: AsyncSession, **kwargs) -> Optional[ModelType]:
        """
        Create a new record.

        Automatically normalizes chain field if present.

        Args:
            session: Database session
            **kwargs: Model field values

        Returns:
            Created model instance or None if failed
        """
        try:
            # Prepare kwargs (normalize chain, etc.)
            prepared_kwargs = self._prepare_kwargs(kwargs)

            instance = self.model(**prepared_kwargs)
            session.add(instance)
            await session.flush()
            await session.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            return None

    async def get_by_id(self, session: AsyncSession, id: int) -> Optional[ModelType]:
        """
        Get record by ID.

        Args:
            session: Database session
            id: Record ID

        Returns:
            Model instance or None if not found
        """
        try:
            result = await session.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by id {id}: {e}")
            return None

    async def get_all(
        self,
        session: AsyncSession,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[ModelType]:
        """
        Get all records with optional pagination.

        Args:
            session: Database session
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of model instances
        """
        try:
            query = select(self.model)
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model.__name__}: {e}")
            return []

    async def filter_by(
        self,
        session: AsyncSession,
        limit: Optional[int] = None,
        **filters
    ) -> List[ModelType]:
        """
        Filter records by criteria.

        Args:
            session: Database session
            limit: Maximum number of records
            **filters: Field name and value pairs

        Returns:
            List of matching model instances
        """
        try:
            conditions = [
                getattr(self.model, key) == value
                for key, value in filters.items()
                if hasattr(self.model, key)
            ]

            query = select(self.model).where(*conditions)
            if limit:
                query = query.limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error filtering {self.model.__name__}: {e}")
            return []

    async def update_by_id(
        self,
        session: AsyncSession,
        id: int,
        **updates
    ) -> bool:
        """
        Update record by ID.

        Args:
            session: Database session
            id: Record ID
            **updates: Field name and value pairs to update

        Returns:
            True if successful, False otherwise
        """
        try:
            stmt = (
                update(self.model)
                .where(self.model.id == id)
                .values(**updates)
            )
            result = await session.execute(stmt)
            await session.flush()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__} {id}: {e}")
            return False

    async def delete_by_id(self, session: AsyncSession, id: int) -> bool:
        """
        Delete record by ID.

        Args:
            session: Database session
            id: Record ID

        Returns:
            True if successful, False otherwise
        """
        try:
            stmt = delete(self.model).where(self.model.id == id)
            result = await session.execute(stmt)
            await session.flush()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Error deleting {self.model.__name__} {id}: {e}")
            return False

    async def count(self, session: AsyncSession, **filters) -> int:
        """
        Count records matching filters.

        Args:
            session: Database session
            **filters: Field name and value pairs

        Returns:
            Number of matching records
        """
        try:
            conditions = [
                getattr(self.model, key) == value
                for key, value in filters.items()
                if hasattr(self.model, key)
            ]

            query = select(func.count()).select_from(self.model)
            if conditions:
                query = query.where(*conditions)

            result = await session.execute(query)
            return result.scalar_one()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            return 0
