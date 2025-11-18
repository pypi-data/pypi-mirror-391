#!/usr/bin/env python3
"""
Test script for CryptoNews JSON queries.

Tests SQLAlchemy 2.0+ JSONB queries with PostgreSQL.
"""

import asyncio
from datetime import datetime
from prisma_web3_py import init_db, close_db, get_db, CryptoNewsRepository


async def test_json_queries():
    """Test all JSON-based query methods."""

    repo = CryptoNewsRepository()

    async with get_db() as session:
        print("=" * 60)
        print("Testing CryptoNews JSONB Queries")
        print("=" * 60)

        # Test 1: search_by_currency
        print("\n1. Testing search_by_currency with JSONB @> operator")
        btc_news = await repo.search_by_currency(session, "BTC", hours=168)  # 7 days
        print(f"   ✓ Found {len(btc_news)} news mentioning BTC")
        if btc_news:
            print(f"   Sample: {btc_news[0].title[:80]}...")
            print(f"   Currencies: {btc_news[0].get_currency_names()}")

        # Test 2: search_by_entity
        print("\n2. Testing search_by_entity with JSONB @> operator")
        okx_news = await repo.search_by_entity(session, "OKX", hours=168)
        print(f"   ✓ Found {len(okx_news)} news mentioning OKX")
        if okx_news:
            print(f"   Sample: {okx_news[0].title[:80]}...")
            print(f"   Entities: {okx_news[0].entity_list}")

        # Test 3: search_by_tag
        print("\n3. Testing search_by_tag with JSONB @> operator")
        # Note: This will only find results if tags have been added to news
        defi_news = await repo.search_by_tag(session, "defi", hours=168)
        print(f"   ✓ Found {len(defi_news)} news tagged with 'defi'")

        # Test 4: get_trending_currencies
        print("\n4. Testing get_trending_currencies with jsonb_array_elements")
        trending_currencies = await repo.get_trending_currencies(session, hours=168, limit=10)
        print(f"   ✓ Found {len(trending_currencies)} trending currencies")
        if trending_currencies:
            print("   Top 5 trending currencies:")
            for item in trending_currencies[:5]:
                print(f"     - {item['currency']}: {item['mentions']} mentions")

        # Test 5: get_trending_entities
        print("\n5. Testing get_trending_entities with jsonb_array_elements_text")
        trending_entities = await repo.get_trending_entities(session, hours=168, limit=10)
        print(f"   ✓ Found {len(trending_entities)} trending entities")
        if trending_entities:
            print("   Top 5 trending entities:")
            for item in trending_entities[:5]:
                print(f"     - {item['entity']}: {item['mentions']} mentions")

        # Test 6: Verify JSONB array search with multiple currencies
        print("\n6. Testing multiple currency searches")
        test_currencies = ["BTC", "ETH", "SEI", "SOL"]
        for currency in test_currencies:
            results = await repo.search_by_currency(session, currency, hours=168)
            print(f"   {currency}: {len(results)} news")

        # Test 7: Model helper methods
        print("\n7. Testing CryptoNews model helper methods")
        if btc_news:
            news = btc_news[0]
            print(f"   ✓ get_currency_names(): {news.get_currency_names()}")
            print(f"   ✓ has_currency('BTC'): {news.has_currency('BTC')}")
            print(f"   ✓ has_currency('ETH'): {news.has_currency('ETH')}")
            if news.entity_list:
                print(f"   ✓ has_entity('{news.entity_list[0]}'): {news.has_entity(news.entity_list[0])}")

        print("\n" + "=" * 60)
        print("✅ All JSONB query tests completed successfully!")
        print("=" * 60)


async def test_create_sample_news():
    """Create sample news for testing (optional)."""

    repo = CryptoNewsRepository()

    sample_data = {
        "title": "Test: Bitcoin and Ethereum Rally as DeFi Sector Grows",
        "category": 1,
        "source": "TestSource",
        "content": "Bitcoin and Ethereum saw significant gains today...",
        "sector": "DeFi",
        "matched_currencies": [
            {"name": "BTC"},
            {"name": "ETH"}
        ],
        "entity_list": ["Bitcoin", "Ethereum", "DeFi"],
        "tags": ["defi", "rally", "crypto"],
        "news_created_at": datetime.utcnow()
    }

    async with get_db() as session:
        news = await repo.create_news(
            session,
            title=sample_data["title"],
            category=sample_data["category"],
            source=sample_data["source"],
            content=sample_data["content"],
            sector=sample_data["sector"],
            matched_currencies=sample_data["matched_currencies"],
            entity_list=sample_data["entity_list"],
            tags=sample_data["tags"],
            news_created_at=sample_data["news_created_at"]
        )

        if news:
            await session.commit()
            print(f"✅ Created sample news ID: {news.id}")
            return news
        else:
            print("❌ Failed to create sample news")
            return None


async def main():
    """Run tests."""
    await init_db()

    try:
        # Uncomment to create sample data:
        # await test_create_sample_news()

        # Run query tests
        await test_json_queries()

    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
