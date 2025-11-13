"""
Token recognition module - recognizes token symbols from text using database.

Replaces JSON file loading with database queries, supports alias matching,
and provides caching for performance.
"""

import re
import logging
from typing import Dict, List, Optional, Set, Tuple
from functools import lru_cache
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, String

from ..models.token import Token
from .chain_config import ChainConfig

logger = logging.getLogger(__name__)


class TokenRecognition:
    """
    Token recognition service that identifies tokens from text.

    Features:
    - Extract token symbols from text (e.g., "$BTC", "WETH", etc.)
    - Retrieve token addresses for specific chains
    - Support alias matching (e.g., "WETH" -> "ETH")
    - In-memory caching for performance
    - Database-backed token data
    """

    def __init__(self):
        self._cache: Dict[str, Token] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(hours=1)  # Cache for 1 hour

        # Common token symbol patterns
        self.symbol_pattern = re.compile(
            r'\$([A-Z][A-Z0-9]{1,10})|'  # $BTC, $ETH pattern
            r'\b([A-Z][A-Z0-9]{1,10})\b'  # BTC, ETH pattern (word boundary)
        )

        # Exclude common non-token words
        self.exclusions = {
            'THE', 'AND', 'FOR', 'NOT', 'BUT', 'HAS', 'WAS', 'ARE',
            'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT',
            'DAY', 'GET', 'HIM', 'HIS', 'HOW', 'ITS', 'MAY', 'NEW',
            'NOW', 'OLD', 'SEE', 'TWO', 'WHO', 'BOY', 'DID', 'ITS',
            'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE', 'VIA', 'API',
            'URL', 'ETH', 'BSC', 'FAQ', 'CEO', 'CTO', 'USA', 'USD',
            'EUR', 'GBP', 'JPY', 'CNY', 'KRW'
        }

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if self._cache_timestamp is None:
            return False
        return datetime.now() - self._cache_timestamp < self._cache_ttl

    def _invalidate_cache(self):
        """Invalidate the cache."""
        self._cache.clear()
        self._cache_timestamp = None

    async def _load_cache(self, session: AsyncSession, limit: int = 1000):
        """
        Load frequently used tokens into cache.

        Args:
            session: Database session
            limit: Maximum number of tokens to cache (top by market cap)
        """
        if self._is_cache_valid():
            return

        logger.info(f"Loading token cache (limit: {limit})...")

        # Load recently created tokens (most recent first)
        stmt = select(Token).order_by(
            Token.created_at.desc()
        ).limit(limit)

        result = await session.execute(stmt)
        tokens = result.scalars().all()

        # Cache by symbol and aliases
        for token in tokens:
            if token.symbol:
                self._cache[token.symbol.upper()] = token

            # Also cache by aliases
            if token.aliases:
                for alias in token.aliases:
                    if isinstance(alias, str):
                        self._cache[alias.upper()] = token

        self._cache_timestamp = datetime.now()
        logger.info(f"Cached {len(self._cache)} token symbols")

    async def recognize_from_text(
        self,
        session: AsyncSession,
        text: str,
        use_cache: bool = True
    ) -> List[Token]:
        """
        Extract and recognize token symbols from text.

        Args:
            session: Database session
            text: Text to extract tokens from
            use_cache: Whether to use cache for lookups

        Returns:
            List of recognized Token objects

        Example:
            >>> text = "I bought $BTC and WETH yesterday"
            >>> tokens = await recognizer.recognize_from_text(session, text)
            >>> [t.symbol for t in tokens]
            ['BTC', 'ETH']
        """
        if use_cache:
            await self._load_cache(session)

        # Extract potential symbols
        matches = self.symbol_pattern.findall(text)
        symbols = set()

        for match in matches:
            # match is a tuple (group1, group2) from the two patterns
            symbol = match[0] or match[1]
            if symbol and symbol.upper() not in self.exclusions:
                symbols.add(symbol.upper())

        if not symbols:
            return []

        # Look up tokens
        recognized_tokens = []
        uncached_symbols = []

        # Check cache first
        if use_cache:
            for symbol in symbols:
                if symbol in self._cache:
                    recognized_tokens.append(self._cache[symbol])
                else:
                    uncached_symbols.append(symbol)
        else:
            uncached_symbols = list(symbols)

        # Query database for uncached symbols
        if uncached_symbols:
            # Query by symbol or aliases
            stmt = select(Token).where(
                or_(
                    Token.symbol.in_(uncached_symbols),
                    func.jsonb_exists_any(Token.aliases, uncached_symbols)
                )
            )

            result = await session.execute(stmt)
            db_tokens = result.scalars().all()
            recognized_tokens.extend(db_tokens)

        # Remove duplicates (by id)
        seen_ids = set()
        unique_tokens = []
        for token in recognized_tokens:
            if token.id not in seen_ids:
                seen_ids.add(token.id)
                unique_tokens.append(token)

        logger.info(f"Recognized {len(unique_tokens)} tokens from text: {symbols}")
        return unique_tokens

    async def get_token_by_symbol(
        self,
        session: AsyncSession,
        symbol: str,
        use_cache: bool = True
    ) -> Optional[Token]:
        """
        Get token by symbol or alias.

        Args:
            session: Database session
            symbol: Token symbol (e.g., "BTC", "WETH")
            use_cache: Whether to use cache

        Returns:
            Token object or None if not found
        """
        symbol = symbol.upper()

        # Check cache first
        if use_cache:
            await self._load_cache(session)
            if symbol in self._cache:
                return self._cache[symbol]

        # Query database
        stmt = select(Token).where(
            or_(
                Token.symbol == symbol,
                func.jsonb_exists(Token.aliases, symbol)
            )
        )

        result = await session.execute(stmt)
        token = result.scalar_one_or_none()

        # Update cache
        if token and use_cache:
            self._cache[symbol] = token

        return token

    async def get_token_address(
        self,
        session: AsyncSession,
        symbol: str,
        chain: str,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Get token address on a specific chain.

        Supports both standard chain names and abbreviations.

        Args:
            session: Database session
            symbol: Token symbol (e.g., "UNI")
            chain: Chain name or abbreviation (e.g., "ethereum", "eth", "poly")
            use_cache: Whether to use cache

        Returns:
            Token address on that chain, or None if not found

        Example:
            >>> address = await recognizer.get_token_address(session, "UNI", "ethereum")
            >>> print(address)
            '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984'

            >>> address = await recognizer.get_token_address(session, "UNI", "eth")
            >>> print(address)
            '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984'
        """
        token = await self.get_token_by_symbol(session, symbol, use_cache)

        if not token:
            logger.warning(f"Token {symbol} not found in database")
            return None

        # Normalize chain name (convert abbreviation to standard name)
        standard_chain = ChainConfig.get_standard_name(chain)

        # Get address on specific chain
        address = token.get_address_on_chain(standard_chain)

        if not address:
            logger.debug(
                f"Token {symbol} not available on chain {chain} ({standard_chain}). "
                f"Available on: {token.get_all_chains()}"
            )

        return address

    async def get_token_by_address(
        self,
        session: AsyncSession,
        chain: str,
        address: str
    ) -> Optional[Token]:
        """
        Get token by chain and address.

        Supports both standard chain names and abbreviations.

        Args:
            session: Database session
            chain: Chain name or abbreviation (e.g., "ethereum", "eth")
            address: Token address

        Returns:
            Token object or None if not found

        Example:
            >>> token = await recognizer.get_token_by_address(session, "ethereum", "0x1f9840...")
            >>> token = await recognizer.get_token_by_address(session, "eth", "0x1f9840...")  # Same result!
        """
        address = address.lower()

        # Normalize chain name (convert abbreviation to standard name)
        standard_chain = ChainConfig.get_standard_name(chain)

        # Check if it's the primary chain address
        stmt = select(Token).where(
            Token.chain == standard_chain,
            func.lower(Token.token_address) == address
        )

        result = await session.execute(stmt)
        token = result.scalar_one_or_none()

        if token:
            return token

        # Check if it's in platforms
        # Use JSONB query to find tokens where platforms->'chain' = address
        stmt = select(Token).where(
            func.lower(
                func.cast(Token.platforms[standard_chain], type_=String)
            ) == address
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_chain_addresses(
        self,
        session: AsyncSession,
        symbol: str,
        use_cache: bool = True
    ) -> Dict[str, str]:
        """
        Get all chain addresses for a token.

        Args:
            session: Database session
            symbol: Token symbol
            use_cache: Whether to use cache

        Returns:
            Dictionary mapping chain -> address

        Example:
            >>> addresses = await recognizer.get_all_chain_addresses(session, "UNI")
            >>> print(addresses)
            {
                'ethereum': '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',
                'polygon': '0xb33eaad8d922b1083446dc23f610c2567fb5180f',
                'arbitrum': '0xfa7f8980b0f1e64a2062791cc3b0871572f1f7f0'
            }
        """
        token = await self.get_token_by_symbol(session, symbol, use_cache)

        if not token:
            return {}

        addresses = {}

        # Add primary chain address
        if token.chain and token.token_address:
            addresses[token.chain] = token.token_address

        # Add other chain addresses from platforms
        if token.platforms:
            addresses.update(token.platforms)

        return addresses

    async def search_tokens(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20
    ) -> List[Token]:
        """
        Search tokens by symbol, name, or aliases.

        Args:
            session: Database session
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching tokens
        """
        query_upper = query.upper()

        stmt = select(Token).where(
            or_(
                Token.symbol.ilike(f"%{query_upper}%"),
                Token.name.ilike(f"%{query}%"),
                func.jsonb_exists(Token.aliases, query_upper)
            )
        ).order_by(
            Token.created_at.desc()
        ).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())


# Global instance for convenience
_recognizer = None


def get_recognizer() -> TokenRecognition:
    """Get or create global TokenRecognition instance."""
    global _recognizer
    if _recognizer is None:
        _recognizer = TokenRecognition()
    return _recognizer


# Example usage
async def example_usage():
    """Example of using TokenRecognition."""
    from prisma_web3_py import get_db, init_db, close_db

    await init_db()

    recognizer = TokenRecognition()

    async with get_db() as session:
        # Extract tokens from text
        text = "I just bought $BTC and WETH, also looking at UNI on Polygon"
        tokens = await recognizer.recognize_from_text(session, text)

        print("\n=== Recognized Tokens ===")
        for token in tokens:
            print(f"- {token.symbol}: {token.name}")

        # Get specific token address
        print("\n=== Token Addresses ===")
        uni_eth = await recognizer.get_token_address(session, "UNI", "ethereum")
        print(f"UNI on Ethereum: {uni_eth}")

        uni_polygon = await recognizer.get_token_address(session, "UNI", "polygon")
        print(f"UNI on Polygon: {uni_polygon}")

        # Get all chain addresses
        print("\n=== All Chain Addresses for UNI ===")
        all_addresses = await recognizer.get_all_chain_addresses(session, "UNI")
        for chain, address in all_addresses.items():
            print(f"{chain}: {address}")

        # Search tokens
        print("\n=== Search Results for 'uni' ===")
        results = await recognizer.search_tokens(session, "uni", limit=5)
        for token in results:
            print(f"- {token.symbol}: {token.name}")

    await close_db()


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
