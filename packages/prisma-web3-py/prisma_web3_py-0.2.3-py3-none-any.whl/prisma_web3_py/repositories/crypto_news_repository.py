"""
CryptoNews repository with specialized query methods.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, func, or_, cast, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from ..models.crypto_news import CryptoNews

logger = logging.getLogger(__name__)


class CryptoNewsRepository(BaseRepository[CryptoNews]):
    """
    Repository for CryptoNews model operations.

    Provides specialized query methods for news articles.
    """

    def __init__(self):
        super().__init__(CryptoNews)

    async def create_news(
        self,
        session: AsyncSession,
        title: str,
        category: int,
        source: str,
        content: str,
        source_link: Optional[str] = None,
        sector: Optional[str] = None,
        matched_currencies: Optional[List[dict]] = None,
        matched_stocks: Optional[List[dict]] = None,
        entity_list: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        sentiment: Optional[str] = None,
        importance_score: Optional[float] = None,
        news_created_at: Optional[datetime] = None
    ) -> Optional[CryptoNews]:
        """
        Create a new crypto news article.

        Args:
            session: Database session
            title: News title
            category: News category
            source: Source name
            content: News content
            source_link: Original URL
            sector: Industry sector
            matched_currencies: List of matched cryptocurrencies
            matched_stocks: List of matched stocks
            entity_list: List of extracted entities
            tags: Custom tags
            summary: AI-generated summary
            sentiment: Sentiment analysis result
            importance_score: Importance score (0-1)
            news_created_at: Original publish time

        Returns:
            Created CryptoNews instance or None if failed
        """
        try:
            news = await self.create(
                session,
                title=title,
                category=category,
                source=source,
                content=content,
                source_link=source_link,
                sector=sector,
                matched_currencies=matched_currencies or [],
                matched_stocks=matched_stocks or [],
                entity_list=entity_list or [],
                tags=tags or [],
                summary=summary,
                sentiment=sentiment,
                importance_score=importance_score,
                news_created_at=news_created_at
            )
            logger.debug(f"Created CryptoNews with ID: {news.id if news else None}")
            return news
        except SQLAlchemyError as e:
            logger.error(f"Error creating crypto news: {e}")
            return None

    async def get_recent_news(
        self,
        session: AsyncSession,
        hours: int = 24,
        source: Optional[str] = None,
        sector: Optional[str] = None,
        category: Optional[int] = None,
        limit: int = 100
    ) -> List[CryptoNews]:
        """
        Get recent news within time window.

        Args:
            session: Database session
            hours: Time window in hours (default: 24)
            source: Filter by source (optional)
            sector: Filter by sector (optional)
            category: Filter by category (optional)
            limit: Maximum number of results

        Returns:
            List of recent news
        """
        try:
            time_threshold = datetime.utcnow() - timedelta(hours=hours)

            query = select(CryptoNews).where(
                CryptoNews.news_created_at >= time_threshold
            )

            if source:
                query = query.where(CryptoNews.source == source)

            if sector:
                query = query.where(CryptoNews.sector == sector)

            if category is not None:
                query = query.where(CryptoNews.category == category)

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent news: {e}")
            return []

    async def search_by_currency(
        self,
        session: AsyncSession,
        currency_name: str,
        hours: Optional[int] = None,
        limit: int = 50
    ) -> List[CryptoNews]:
        """
        Search news mentioning a specific cryptocurrency.

        Uses PostgreSQL JSONB @> containment operator for efficient array search.

        Args:
            session: Database session
            currency_name: Currency symbol/name to search (case-insensitive)
            hours: Time window in hours (optional)
            limit: Maximum number of results

        Returns:
            List of news mentioning the currency

        Example:
            >>> await repo.search_by_currency(session, "BTC", hours=24)
        """
        try:
            # Normalize currency name (uppercase)
            normalized_name = currency_name.strip().upper()

            # Use PostgreSQL @> operator (containment) for JSONB array search
            # This checks if matched_currencies contains an object with name = normalized_name
            query = select(CryptoNews).where(
                CryptoNews.matched_currencies.op('@>')(
                    cast([{"name": normalized_name}], JSONB)
                )
            )

            if hours is not None:
                time_threshold = datetime.utcnow() - timedelta(hours=hours)
                query = query.where(CryptoNews.news_created_at >= time_threshold)

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error searching news by currency '{currency_name}': {e}")
            return []

    async def search_by_entity(
        self,
        session: AsyncSession,
        entity_name: str,
        hours: Optional[int] = None,
        limit: int = 50
    ) -> List[CryptoNews]:
        """
        Search news mentioning a specific entity.

        Uses PostgreSQL JSONB @> containment operator for efficient array search.

        Args:
            session: Database session
            entity_name: Entity name to search (case-sensitive)
            hours: Time window in hours (optional)
            limit: Maximum number of results

        Returns:
            List of news mentioning the entity

        Example:
            >>> await repo.search_by_entity(session, "OKX", hours=24)
        """
        try:
            # Normalize entity name (strip whitespace)
            normalized_entity = entity_name.strip()

            # Use PostgreSQL @> operator (containment) for JSONB array search
            # Cast the search value to JSONB to ensure proper type matching
            query = select(CryptoNews).where(
                CryptoNews.entity_list.op('@>')(cast([normalized_entity], JSONB))
            )

            if hours is not None:
                time_threshold = datetime.utcnow() - timedelta(hours=hours)
                query = query.where(CryptoNews.news_created_at >= time_threshold)

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error searching news by entity '{entity_name}': {e}")
            return []

    async def search_news(
        self,
        session: AsyncSession,
        search_term: str,
        search_in_content: bool = False,
        limit: int = 50
    ) -> List[CryptoNews]:
        """
        Search news by keyword in title (and optionally content).

        Args:
            session: Database session
            search_term: Search keyword
            search_in_content: Also search in content (slower)
            limit: Maximum number of results

        Returns:
            List of matching news
        """
        try:
            search_pattern = f"%{search_term.lower()}%"

            if search_in_content:
                query = select(CryptoNews).where(
                    or_(
                        CryptoNews.title.ilike(search_pattern),
                        CryptoNews.content.ilike(search_pattern)
                    )
                )
            else:
                query = select(CryptoNews).where(
                    CryptoNews.title.ilike(search_pattern)
                )

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error searching news: {e}")
            return []

    async def get_news_by_source(
        self,
        session: AsyncSession,
        source: str,
        hours: Optional[int] = None,
        limit: int = 100
    ) -> List[CryptoNews]:
        """
        Get news from a specific source.

        Args:
            session: Database session
            source: Source name
            hours: Time window in hours (optional)
            limit: Maximum number of results

        Returns:
            List of news from the source
        """
        try:
            query = select(CryptoNews).where(CryptoNews.source == source)

            if hours is not None:
                time_threshold = datetime.utcnow() - timedelta(hours=hours)
                query = query.where(CryptoNews.news_created_at >= time_threshold)

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting news by source: {e}")
            return []

    async def get_news_by_sector(
        self,
        session: AsyncSession,
        sector: str,
        hours: Optional[int] = None,
        limit: int = 100
    ) -> List[CryptoNews]:
        """
        Get news for a specific sector.

        Args:
            session: Database session
            sector: Sector name
            hours: Time window in hours (optional)
            limit: Maximum number of results

        Returns:
            List of news for the sector
        """
        try:
            query = select(CryptoNews).where(CryptoNews.sector == sector)

            if hours is not None:
                time_threshold = datetime.utcnow() - timedelta(hours=hours)
                query = query.where(CryptoNews.news_created_at >= time_threshold)

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting news by sector: {e}")
            return []

    async def get_trending_currencies(
        self,
        session: AsyncSession,
        hours: int = 24,
        limit: int = 20
    ) -> List[dict]:
        """
        Get trending cryptocurrencies based on news mentions.

        Uses PostgreSQL jsonb_array_elements to extract and count currency mentions.

        Args:
            session: Database session
            hours: Time window in hours (default: 24)
            limit: Maximum number of results (default: 20)

        Returns:
            List of dicts with currency name and mention count:
            [{"currency": "BTC", "mentions": 15}, ...]

        Example:
            >>> trending = await repo.get_trending_currencies(session, hours=24, limit=10)
            >>> print(f"Top currency: {trending[0]['currency']} with {trending[0]['mentions']} mentions")
        """
        try:
            time_threshold = datetime.utcnow() - timedelta(hours=hours)

            # Use PostgreSQL function to unnest JSONB array and count occurrences
            # This is more efficient than fetching all rows and processing in Python
            query = text("""
                SELECT
                    (jsonb_array_elements(matched_currencies)->>'name') as currency_name,
                    COUNT(*) as mention_count
                FROM public."CryptoNews"
                WHERE news_created_at >= :time_threshold
                  AND matched_currencies IS NOT NULL
                  AND matched_currencies != '[]'::jsonb
                GROUP BY currency_name
                ORDER BY mention_count DESC
                LIMIT :limit
            """)

            result = await session.execute(
                query,
                {"time_threshold": time_threshold, "limit": limit}
            )

            trending = [
                {"currency": row[0], "mentions": row[1]}
                for row in result.fetchall()
                if row[0] is not None  # Filter out null currency names
            ]

            logger.debug(
                f"get_trending_currencies(hours={hours}): found {len(trending)} currencies"
            )
            return trending

        except SQLAlchemyError as e:
            logger.error(f"Error getting trending currencies: {e}")
            return []

    async def get_trending_entities(
        self,
        session: AsyncSession,
        hours: int = 24,
        limit: int = 20
    ) -> List[dict]:
        """
        Get trending entities based on news mentions.

        Uses PostgreSQL jsonb_array_elements to extract and count entity mentions.

        Args:
            session: Database session
            hours: Time window in hours (default: 24)
            limit: Maximum number of results (default: 20)

        Returns:
            List of dicts with entity name and mention count:
            [{"entity": "OKX", "mentions": 10}, ...]

        Example:
            >>> trending = await repo.get_trending_entities(session, hours=24, limit=10)
        """
        try:
            time_threshold = datetime.utcnow() - timedelta(hours=hours)

            # Use PostgreSQL function to unnest JSONB array and count occurrences
            query = text("""
                SELECT
                    jsonb_array_elements_text(entity_list) as entity_name,
                    COUNT(*) as mention_count
                FROM public."CryptoNews"
                WHERE news_created_at >= :time_threshold
                  AND entity_list IS NOT NULL
                  AND entity_list != '[]'::jsonb
                GROUP BY entity_name
                ORDER BY mention_count DESC
                LIMIT :limit
            """)

            result = await session.execute(
                query,
                {"time_threshold": time_threshold, "limit": limit}
            )

            trending = [
                {"entity": row[0], "mentions": row[1]}
                for row in result.fetchall()
                if row[0] is not None
            ]

            logger.debug(
                f"get_trending_entities(hours={hours}): found {len(trending)} entities"
            )
            return trending

        except SQLAlchemyError as e:
            logger.error(f"Error getting trending entities: {e}")
            return []

    async def search_by_tag(
        self,
        session: AsyncSession,
        tag: str,
        hours: Optional[int] = None,
        limit: int = 50
    ) -> List[CryptoNews]:
        """
        Search news by custom tag.

        Uses PostgreSQL JSONB @> containment operator for efficient array search.

        Args:
            session: Database session
            tag: Tag to search for
            hours: Time window in hours (optional)
            limit: Maximum number of results

        Returns:
            List of news with the specified tag

        Example:
            >>> await repo.search_by_tag(session, "defi", hours=24)
        """
        try:
            # Normalize tag (lowercase)
            normalized_tag = tag.strip().lower()

            # Use PostgreSQL @> operator for JSONB array search
            query = select(CryptoNews).where(
                CryptoNews.tags.op('@>')(cast([normalized_tag], JSONB))
            )

            if hours is not None:
                time_threshold = datetime.utcnow() - timedelta(hours=hours)
                query = query.where(CryptoNews.news_created_at >= time_threshold)

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error searching news by tag '{tag}': {e}")
            return []

    async def get_news_statistics(
        self,
        session: AsyncSession,
        hours: int = 24
    ) -> dict:
        """
        Get news statistics for the given time window.

        Args:
            session: Database session
            hours: Time window in hours

        Returns:
            Dictionary with various statistics
        """
        try:
            time_threshold = datetime.utcnow() - timedelta(hours=hours)

            # Total count
            total_count_query = select(func.count(CryptoNews.id)).where(
                CryptoNews.news_created_at >= time_threshold
            )
            total_count = await session.execute(total_count_query)

            # Count by source
            source_count_query = (
                select(CryptoNews.source, func.count(CryptoNews.id))
                .where(CryptoNews.news_created_at >= time_threshold)
                .group_by(CryptoNews.source)
            )
            source_counts = await session.execute(source_count_query)

            # Count by sector
            sector_count_query = (
                select(CryptoNews.sector, func.count(CryptoNews.id))
                .where(CryptoNews.news_created_at >= time_threshold)
                .group_by(CryptoNews.sector)
            )
            sector_counts = await session.execute(sector_count_query)

            return {
                "total": total_count.scalar(),
                "by_source": dict(source_counts.all()),
                "by_sector": dict(sector_counts.all()),
                "time_window_hours": hours
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting news statistics: {e}")
            return {
                "total": 0,
                "by_source": {},
                "by_sector": {},
                "time_window_hours": hours
            }
