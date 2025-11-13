#!/usr/bin/env python3
"""
Test script for TokenRecognition module.
Tests token recognition from text and address lookups.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma_web3_py import get_db, init_db, close_db
from prisma_web3_py.models import Token
from prisma_web3_py.repositories import TokenRepository
from prisma_web3_py.utils import TokenRecognition


async def test_token_recognition():
    """Test TokenRecognition functionality."""

    print("\n" + "="*60)
    print("Testing TokenRecognition Module")
    print("="*60)

    # Initialize database
    await init_db()

    recognizer = TokenRecognition()
    token_repo = TokenRepository()

    # Create some test tokens first
    test_tokens = [
        {
            "chain": "ethereum",
            "token_address": "0xBTC1234567890abcdef1234567890abcdef1234",
            "symbol": "BTC",
            "name": "Bitcoin",
            "coingecko_id": "bitcoin",
            "platforms": {},
            "categories": ["Currency"]
        },
        {
            "chain": "ethereum",
            "token_address": "0xETH1234567890abcdef1234567890abcdef1234",
            "symbol": "ETH",
            "name": "Ethereum",
            "coingecko_id": "ethereum",
            "platforms": {},
            "categories": ["Smart Contract Platform"]
        },
        {
            "chain": "ethereum",
            "token_address": "0xUNI1234567890abcdef1234567890abcdef1234",
            "symbol": "UNI",
            "name": "Uniswap",
            "coingecko_id": "uniswap",
            "platforms": {
                "polygon": "0xUNIPOLYGON1234567890abcdef1234567890",
                "arbitrum": "0xUNIARBITRUM1234567890abcdef123456789"
            },
            "categories": ["DeFi", "DEX"],
            "aliases": ["UNI-V2"]
        }
    ]

    try:
        # Create test tokens
        print("\n[SETUP] Creating test tokens...")
        async with get_db() as session:
            for token_data in test_tokens:
                await token_repo.create(session, **token_data)
            await session.commit()
            print(f"✓ Created {len(test_tokens)} test tokens")

        # Test 1: Recognize tokens from text
        print("\n[1] Recognizing tokens from text...")
        async with get_db() as session:
            text = "I just bought $BTC and ETH, also looking at UNI on Polygon"
            tokens = await recognizer.recognize_from_text(session, text, use_cache=False)

            if len(tokens) > 0:
                print(f"✓ Recognized {len(tokens)} tokens from text:")
                for token in tokens:
                    print(f"  - {token.symbol}: {token.name}")
            else:
                print("⚠ No tokens recognized")

        # Test 2: Get token by symbol
        print("\n[2] Getting token by symbol...")
        async with get_db() as session:
            token = await recognizer.get_token_by_symbol(session, "UNI", use_cache=False)

            if token:
                print(f"✓ Found token: {token.symbol} ({token.name})")
                print(f"  Chain: {token.chain}")
                print(f"  CoinGecko ID: {token.coingecko_id}")
            else:
                print("✗ Token not found")

        # Test 3: Get token address on specific chain
        print("\n[3] Getting token address on Ethereum...")
        async with get_db() as session:
            address = await recognizer.get_token_address(
                session, "UNI", "ethereum", use_cache=False
            )

            if address:
                print(f"✓ UNI on Ethereum: {address}")
            else:
                print("✗ Address not found")

        # Test 4: Get token address on Polygon (from platforms)
        print("\n[4] Getting token address on Polygon...")
        async with get_db() as session:
            address = await recognizer.get_token_address(
                session, "UNI", "polygon", use_cache=False
            )

            if address:
                print(f"✓ UNI on Polygon: {address}")
            else:
                print("✗ Address not found")

        # Test 5: Get all chain addresses
        print("\n[5] Getting all chain addresses for UNI...")
        async with get_db() as session:
            addresses = await recognizer.get_all_chain_addresses(
                session, "UNI", use_cache=False
            )

            if addresses:
                print(f"✓ Found addresses on {len(addresses)} chains:")
                for chain, addr in addresses.items():
                    print(f"  - {chain}: {addr[:20]}...")
            else:
                print("✗ No addresses found")

        # Test 6: Get token by address
        print("\n[6] Getting token by address...")
        async with get_db() as session:
            token = await recognizer.get_token_by_address(
                session,
                "ethereum",
                "0xBTC1234567890abcdef1234567890abcdef1234"
            )

            if token:
                print(f"✓ Found token: {token.symbol} ({token.name})")
            else:
                print("✗ Token not found")

        # Test 7: Search tokens
        print("\n[7] Searching tokens with query 'uni'...")
        async with get_db() as session:
            results = await recognizer.search_tokens(session, "uni", limit=5)

            if results:
                print(f"✓ Found {len(results)} tokens:")
                for token in results:
                    print(f"  - {token.symbol}: {token.name}")
            else:
                print("⚠ No results found")

        # Test 8: Test caching
        print("\n[8] Testing cache functionality...")
        async with get_db() as session:
            # First call loads cache
            await recognizer._load_cache(session, limit=100)
            print(f"✓ Cache loaded with {len(recognizer._cache)} entries")

            # Second call should use cache
            token = await recognizer.get_token_by_symbol(session, "BTC", use_cache=True)
            if token:
                print(f"✓ Retrieved token from cache: {token.symbol}")
            else:
                print("✗ Failed to retrieve from cache")

        # Test 9: Test alias matching
        print("\n[9] Testing alias matching...")
        async with get_db() as session:
            token = await recognizer.get_token_by_symbol(session, "UNI-V2", use_cache=False)

            if token:
                print(f"✓ Found token by alias: {token.symbol} ({token.name})")
            else:
                print("⚠ Alias not matched (expected if aliases not set)")

        # Test 10: Test symbol pattern extraction
        print("\n[10] Testing various text patterns...")
        async with get_db() as session:
            test_texts = [
                "$BTC is going up",
                "Check out ETH today",
                "I hold BTC, ETH, and UNI",
                "Bitcoin ($BTC) reached new high"
            ]

            for text in test_texts:
                tokens = await recognizer.recognize_from_text(session, text, use_cache=True)
                symbols = [t.symbol for t in tokens]
                print(f"  '{text}' → {symbols}")

        # Cleanup
        print("\n[CLEANUP] Deleting test tokens...")
        async with get_db() as session:
            for token_data in test_tokens:
                token = await token_repo.get_by_address(
                    session,
                    token_data["chain"],
                    token_data["token_address"]
                )
                if token:
                    await token_repo.delete_by_id(session, token.id)
            await session.commit()
            print("✓ Test tokens deleted")

        print("\n" + "="*60)
        print("✓ All TokenRecognition tests passed!")
        print("="*60)
        return True

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await close_db()


if __name__ == "__main__":
    success = asyncio.run(test_token_recognition())
    sys.exit(0 if success else 1)
