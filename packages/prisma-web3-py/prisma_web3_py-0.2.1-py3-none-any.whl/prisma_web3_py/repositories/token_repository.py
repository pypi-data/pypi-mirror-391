"""
Token repository with specialized query methods.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, func, or_, cast, String, text
from sqlalchemy.dialects.postgresql import insert, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
import logging

from .base_repository import BaseRepository
from ..models.token import Token

logger = logging.getLogger(__name__)


class TokenRepository(BaseRepository[Token]):
    """
    Repository for Token model operations.

    Automatically normalizes chain names to CoinGecko standard format.
    Supports both abbreviations (eth, bsc, sol) and standard names.
    """

    def __init__(self):
        super().__init__(Token)
        self._pg_trgm_available = None  # Cache for pg_trgm availability check

    async def _check_pg_trgm_available(self, session: AsyncSession) -> bool:
        """
        Check if pg_trgm extension is available in the database.

        This method caches the result to avoid repeated checks.

        Args:
            session: Database session

        Returns:
            True if pg_trgm is available, False otherwise
        """
        if self._pg_trgm_available is not None:
            return self._pg_trgm_available

        try:
            # Check if pg_trgm extension exists by querying pg_extension
            result = await session.execute(
                text("SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_trgm'")
            )
            count = result.scalar()
            self._pg_trgm_available = count > 0
        except Exception as e:
            # If check fails, assume pg_trgm is not available
            logger.debug(f"Failed to check pg_trgm availability: {e}")
            self._pg_trgm_available = False

        logger.debug(f"pg_trgm availability: {self._pg_trgm_available}")
        return self._pg_trgm_available

    def _normalize_chain(self, chain: Optional[str]) -> Optional[str]:
        """
        Normalize chain name to standard format.

        Args:
            chain: Chain name or abbreviation (e.g., 'eth', 'ethereum', 'bsc')

        Returns:
            Standardized chain name (e.g., 'ethereum', 'binance-smart-chain')
            or None if input is None

        Example:
            >>> self._normalize_chain('eth')
            'ethereum'
            >>> self._normalize_chain('bsc')
            'binance-smart-chain'
            >>> self._normalize_chain('ethereum')
            'ethereum'
        """
        if chain is None or chain == "":
            return chain
        # Lazy import to avoid circular dependency
        from ..utils.chain_config import ChainConfig
        return ChainConfig.get_standard_name(chain)

    async def get_by_address(
        self,
        session: AsyncSession,
        chain: str,
        token_address: str
    ) -> Optional[Token]:
        """
        Get token by chain and address.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            chain: Chain name or abbreviation (e.g., 'eth', 'ethereum')
            token_address: Token contract address

        Returns:
            Token instance or None

        Example:
            >>> await repo.get_by_address(session, 'eth', '0x...')  # Works!
            >>> await repo.get_by_address(session, 'ethereum', '0x...')  # Also works!
        """
        try:
            # Normalize chain name
            normalized_chain = self._normalize_chain(chain)

            result = await session.execute(
                select(Token)
                .where(Token.chain == normalized_chain, Token.token_address == token_address)
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

        Automatically normalizes chain name to standard format.

        Args:
            session: Database session
            token_data: Dictionary containing token fields
                       chain: Can be abbreviation (e.g., 'bsc') or standard name

        Returns:
            Token ID or None if failed

        Example:
            >>> data = {"chain": "bsc", "token_address": "0x..."}  # bsc auto-converts to binance-smart-chain
            >>> token_id = await repo.upsert_token(session, data)
        """
        try:
            token_address = token_data.get("token_address")
            chain = token_data.get("chain", "solana")  # Default to solana standard name

            if not token_address:
                logger.warning("Token address is required for upsert")
                return None

            # Normalize chain name
            normalized_chain = self._normalize_chain(chain)

            # Prepare upsert data
            upsert_data = {
                "token_address": token_address,
                "chain": normalized_chain,
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
                    Token.chain == normalized_chain,
                    Token.token_address == token_address
                )
                token_result = await session.execute(token_query)
                token_id = token_result.scalar_one()

            logger.debug(f"Upserted token with ID: {token_id}")
            return token_id

        except SQLAlchemyError as e:
            logger.error(f"Error upserting token: {e}")
            return None

    async def get_recent_tokens(
        self,
        session: AsyncSession,
        chain: Optional[str] = None,
        limit: int = 100
    ) -> List[Token]:
        """
        Get recently created tokens.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            chain: Filter by chain name or abbreviation (e.g., 'eth', 'ethereum')
            limit: Maximum number of results

        Returns:
            List of tokens ordered by creation date (most recent first)

        Example:
            >>> await repo.get_recent_tokens(session, 'bsc', 50)  # Works!
        """
        try:
            query = select(Token)

            if chain:
                # Normalize chain name
                normalized_chain = self._normalize_chain(chain)
                query = query.where(Token.chain == normalized_chain)

            query = query.order_by(Token.created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent tokens: {e}")
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

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            search_term: Search string
            chain: Filter by chain name or abbreviation (e.g., 'sol', 'solana')
            limit: Maximum number of results

        Returns:
            List of matching tokens

        Example:
            >>> await repo.search_tokens(session, "UNI", chain="eth")  # Works!
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
                # Normalize chain name
                normalized_chain = self._normalize_chain(chain)
                query = query.where(Token.chain == normalized_chain)

            # Order by creation date (most recent first)
            query = query.order_by(Token.created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error searching tokens: {e}")
            return []

    async def get_recently_updated_tokens(
        self,
        session: AsyncSession,
        hours: int = 24,
        chain: Optional[str] = None,
        limit: int = 100
    ) -> List[Token]:
        """
        Get recently updated tokens.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            hours: Time window in hours
            chain: Filter by chain name or abbreviation (e.g., 'eth', 'ethereum')
            limit: Maximum number of results

        Returns:
            List of recently updated tokens

        Example:
            >>> await repo.get_recently_updated_tokens(session, hours=24, chain='bsc')  # Works!
        """
        try:
            time_threshold = datetime.utcnow() - timedelta(hours=hours)

            query = select(Token).where(Token.updated_at >= time_threshold)

            if chain:
                # Normalize chain name
                normalized_chain = self._normalize_chain(chain)
                query = query.where(Token.chain == normalized_chain)

            query = query.order_by(Token.updated_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting recently updated tokens: {e}")
            return []
        
    async def search_by_symbol(
        self,
        session: AsyncSession,
        symbol: str,
        exact: bool = True
    ) -> List[Token]:
        """
        Search tokens by symbol.

        Args:
            session: Database session
            symbol: Token symbol to search for
            exact: If True, exact match only. If False, case-insensitive LIKE match

        Returns:
            List of matching Token objects

        Example:
            # Exact match
            tokens = await repo.search_by_symbol(session, "BTC", exact=True)

            # Fuzzy match
            tokens = await repo.search_by_symbol(session, "btc", exact=False)
        """
        try:
            normalized_symbol = symbol.strip().upper()

            if exact:
                # Exact match (case-insensitive)
                stmt = select(Token).where(
                    func.upper(Token.symbol) == normalized_symbol
                )
            else:
                # LIKE match for fuzzy search
                stmt = select(Token).where(
                    func.upper(Token.symbol).like(f"%{normalized_symbol}%")
                ).limit(10)

            result = await session.execute(stmt)
            tokens = result.scalars().all()

            logger.debug(
                f"search_by_symbol('{symbol}', exact={exact}): found {len(tokens)} tokens"
            )
            return list(tokens)

        except Exception as e:
            logger.error(f"Error searching by symbol '{symbol}': {e}")
            return []


    async def search_by_name(
        self,
        session: AsyncSession,
        name: str,
        exact: bool = False
    ) -> List[Token]:
        """
        Search tokens by name.

        Args:
            session: Database session
            name: Token name to search for
            exact: If True, exact match. If False, case-insensitive LIKE match (default)

        Returns:
            List of matching Token objects

        Example:
            # Fuzzy match (default)
            tokens = await repo.search_by_name(session, "bitcoin")

            # Exact match
            tokens = await repo.search_by_name(session, "Bitcoin", exact=True)
        """
        try:
            normalized_name = name.strip()

            if exact:
                # Exact match (case-insensitive)
                stmt = select(Token).where(
                    func.lower(Token.name) == normalized_name.lower()
                )
            else:
                # LIKE match for partial matching
                stmt = select(Token).where(
                    func.lower(Token.name).like(f"%{normalized_name.lower()}%")
                ).limit(10)

            result = await session.execute(stmt)
            tokens = result.scalars().all()

            logger.debug(
                f"search_by_name('{name}', exact={exact}): found {len(tokens)} tokens"
            )
            return list(tokens)

        except Exception as e:
            logger.error(f"Error searching by name '{name}': {e}")
            return []


    async def search_by_alias(
        self,
        session: AsyncSession,
        alias: str
    ) -> List[Token]:
        """
        Search tokens by alias using JSONB containment.

        The aliases field is a JSONB array, so we use PostgreSQL's JSONB operators
        to check if the alias exists in the array.

        Args:
            session: Database session
            alias: Alias to search for

        Returns:
            List of matching Token objects

        Example:
            tokens = await repo.search_by_alias(session, "btc")
        """
        try:
            normalized_alias = alias.strip().lower()

            # Use PostgreSQL @> operator (containment) for JSONB array search
            # Cast the search value to JSONB to ensure proper type matching
            stmt = select(Token).where(
                Token.aliases.op('@>')(cast([normalized_alias], JSONB))
            )

            result = await session.execute(stmt)
            tokens = result.scalars().all()

            logger.debug(
                f"search_by_alias('{alias}'): found {len(tokens)} tokens"
            )
            return list(tokens)

        except Exception as e:
            logger.error(f"Error searching by alias '{alias}': {e}")
            return []


    async def fuzzy_search(
        self,
        session: AsyncSession,
        text: str,
        threshold: float = 0.8,
        limit: int = 10
    ) -> List[Token]:
        """
        Fuzzy search tokens using PostgreSQL trigram similarity.

        Requires the pg_trgm extension to be installed:
            CREATE EXTENSION IF NOT EXISTS pg_trgm;

        If pg_trgm is not available, falls back to LIKE matching.

        Args:
            session: Database session
            text: Text to search for
            threshold: Similarity threshold (0.0 to 1.0, default 0.8)
            limit: Maximum number of results

        Returns:
            List of matching Token objects sorted by similarity

        Example:
            # Find tokens similar to "bitcoin"
            tokens = await repo.fuzzy_search(session, "bitcon", threshold=0.7)
        """
        try:
            normalized_text = text.strip().lower()

            # Check if pg_trgm is available before attempting to use it
            pg_trgm_available = await self._check_pg_trgm_available(session)

            if pg_trgm_available:
                # Use similarity() function from pg_trgm
                # Search across symbol, name, and coingecko_id
                stmt = select(Token).where(
                    or_(
                        func.similarity(func.lower(Token.symbol), normalized_text) >= threshold,
                        func.similarity(func.lower(Token.name), normalized_text) >= threshold,
                        func.similarity(func.lower(Token.coingecko_id), normalized_text) >= threshold,
                    )
                ).order_by(
                    # Order by best similarity score
                    func.greatest(
                        func.similarity(func.lower(Token.symbol), normalized_text),
                        func.similarity(func.lower(Token.name), normalized_text),
                        func.similarity(func.lower(Token.coingecko_id), normalized_text),
                    ).desc()
                ).limit(limit)

                result = await session.execute(stmt)
                tokens = result.scalars().all()

                logger.debug(
                    f"fuzzy_search('{text}', threshold={threshold}): "
                    f"found {len(tokens)} tokens using pg_trgm"
                )
                return list(tokens)
            else:
                # Fall back to LIKE matching if pg_trgm is not available
                logger.debug(f"pg_trgm not available, using LIKE matching for fuzzy_search")

                stmt = select(Token).where(
                    or_(
                        func.lower(Token.symbol).like(f"%{normalized_text}%"),
                        func.lower(Token.name).like(f"%{normalized_text}%"),
                        func.lower(Token.coingecko_id).like(f"%{normalized_text}%"),
                    )
                ).limit(limit)

                result = await session.execute(stmt)
                tokens = result.scalars().all()

                logger.debug(
                    f"fuzzy_search('{text}'): found {len(tokens)} tokens using LIKE"
                )
                return list(tokens)

        except Exception as e:
            logger.error(f"Error in fuzzy_search('{text}'): {e}")
            return []

