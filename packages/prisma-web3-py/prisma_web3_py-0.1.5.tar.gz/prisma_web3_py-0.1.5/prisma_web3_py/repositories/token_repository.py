"""
Token repository with specialized query methods.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
import logging

from .base_repository import BaseRepository
from ..models.token import Token

logger = logging.getLogger(__name__)


class TokenRepository(BaseRepository[Token]):
    """Repository for Token model operations."""

    def __init__(self):
        super().__init__(Token)

    async def get_by_address(
        self,
        session: AsyncSession,
        chain: str,
        token_address: str
    ) -> Optional[Token]:
        """
        Get token by chain and address.

        Args:
            session: Database session
            chain: Blockchain name
            token_address: Token contract address

        Returns:
            Token instance or None
        """
        try:
            result = await session.execute(
                select(Token)
                .where(Token.chain == chain, Token.token_address == token_address)
                .options(selectinload(Token.signals))
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting token {chain}:{token_address}: {e}")
            return None

    async def upsert_token(
        self,
        session: AsyncSession,
        token_data: dict
    ) -> Optional[int]:
        """
        Insert or update token information.

        Args:
            session: Database session
            token_data: Dictionary containing token fields

        Returns:
            Token ID or None if failed
        """
        try:
            token_address = token_data.get("token_address")
            chain = token_data.get("chain", "sol")

            if not token_address:
                logger.warning("Token address is required for upsert")
                return None

            # Prepare upsert data
            upsert_data = {
                "token_address": token_address,
                "chain": chain,
                "name": token_data.get("name"),
                "symbol": token_data.get("symbol"),
                "description": token_data.get("description"),
                "website": token_data.get("website"),
                "telegram": token_data.get("telegram"),
                "twitter": token_data.get("twitter"),
                "decimals": token_data.get("decimals"),
                "updated_at": datetime.utcnow(),
            }

            # Remove None values
            upsert_data = {k: v for k, v in upsert_data.items() if v is not None}

            # Execute UPSERT
            stmt = insert(Token).values(upsert_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['chain', 'token_address'],
                set_=upsert_data
            )
            result = await session.execute(stmt)
            await session.flush()

            # Get token ID
            if result.inserted_primary_key:
                token_id = result.inserted_primary_key[0]
            else:
                # For updates, fetch the ID
                token_query = select(Token.id).where(
                    Token.chain == chain,
                    Token.token_address == token_address
                )
                token_result = await session.execute(token_query)
                token_id = token_result.scalar_one()

            logger.debug(f"Upserted token with ID: {token_id}")
            return token_id

        except SQLAlchemyError as e:
            logger.error(f"Error upserting token: {e}")
            return None

    async def get_verified_tokens(
        self,
        session: AsyncSession,
        chain: Optional[str] = None,
        limit: int = 100
    ) -> List[Token]:
        """
        Get verified tokens.

        Args:
            session: Database session
            chain: Filter by specific chain (optional)
            limit: Maximum number of results

        Returns:
            List of verified tokens
        """
        try:
            query = select(Token).where(Token.verification_status == 'verified')

            if chain:
                query = query.where(Token.chain == chain)

            query = query.limit(limit).order_by(Token.score.desc())

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting verified tokens: {e}")
            return []

    async def search_tokens(
        self,
        session: AsyncSession,
        search_term: str,
        chain: Optional[str] = None,
        limit: int = 20
    ) -> List[Token]:
        """
        Search tokens by symbol, name, or address.

        Args:
            session: Database session
            search_term: Search string
            chain: Filter by specific chain (optional)
            limit: Maximum number of results

        Returns:
            List of matching tokens
        """
        try:
            search_pattern = f"%{search_term.lower()}%"

            query = select(Token).where(
                or_(
                    Token.symbol.ilike(search_pattern),
                    Token.name.ilike(search_pattern),
                    Token.token_address.ilike(search_pattern)
                )
            )

            if chain:
                query = query.where(Token.chain == chain)

            query = query.limit(limit).order_by(Token.score.desc())

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error searching tokens: {e}")
            return []

    async def get_top_scored_tokens(
        self,
        session: AsyncSession,
        chain: Optional[str] = None,
        min_score: float = 0.0,
        limit: int = 50
    ) -> List[Token]:
        """
        Get tokens with highest scores.

        Args:
            session: Database session
            chain: Filter by specific chain (optional)
            min_score: Minimum score threshold
            limit: Maximum number of results

        Returns:
            List of top scored tokens
        """
        try:
            query = select(Token).where(Token.score >= min_score)

            if chain:
                query = query.where(Token.chain == chain)

            query = query.order_by(Token.score.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting top scored tokens: {e}")
            return []

    async def update_token_score(
        self,
        session: AsyncSession,
        chain: str,
        token_address: str,
        score: float,
        signal_score: Optional[float] = None,
        metrics_score: Optional[float] = None
    ) -> bool:
        """
        Update token scores.

        Args:
            session: Database session
            chain: Blockchain name
            token_address: Token contract address
            score: Overall score
            signal_score: Signal score (optional)
            metrics_score: Metrics score (optional)

        Returns:
            True if successful
        """
        try:
            token = await self.get_by_address(session, chain, token_address)
            if not token:
                return False

            token.score = score
            if signal_score is not None:
                token.signal_score = signal_score
            if metrics_score is not None:
                token.metrics_score = metrics_score
            token.updated_at = datetime.utcnow()

            await session.flush()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error updating token score: {e}")
            return False

    async def get_recently_updated_tokens(
        self,
        session: AsyncSession,
        hours: int = 24,
        chain: Optional[str] = None,
        limit: int = 100
    ) -> List[Token]:
        """
        Get recently updated tokens.

        Args:
            session: Database session
            hours: Time window in hours
            chain: Filter by specific chain (optional)
            limit: Maximum number of results

        Returns:
            List of recently updated tokens
        """
        try:
            time_threshold = datetime.utcnow() - timedelta(hours=hours)

            query = select(Token).where(Token.updated_at >= time_threshold)

            if chain:
                query = query.where(Token.chain == chain)

            query = query.order_by(Token.updated_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting recently updated tokens: {e}")
            return []
