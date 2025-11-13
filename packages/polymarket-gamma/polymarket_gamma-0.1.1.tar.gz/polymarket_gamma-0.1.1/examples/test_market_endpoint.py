#!/usr/bin/env python3
"""
Test script to verify the Market endpoint implementation.

This script tests the basic functionality of the Py-Gamma SDK
using the get-market-by-id endpoint as an example.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path to import py_gamma
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from py_gamma import GammaClient, GammaConfig, MarketNotFoundError, GammaAPIError


async def test_market_endpoint():
    """Test the market endpoint functionality."""
    print("🚀 Testing Py-Gamma SDK Market Endpoint")
    print("=" * 50)

    # Create configuration
    config = GammaConfig(
        debug=True,
        enable_cache=True,
        max_retries=2,
        request_timeout=15.0,
    )

    print(f"📋 Configuration: {config}")
    print()

    async with GammaClient(config=config) as client:
        print("✅ GammaClient created successfully")

        try:
            # Test 1: List markets first to get real data
            print("\n📋 Test 1: List markets")
            try:
                markets = await client.markets.get_markets(limit=5)
                print(f"✅ Successfully fetched {len(markets)} markets")

                # Use the first market for subsequent tests
                if markets:
                    first_market = markets[0]
                    print(f"\n   First market summary:")
                    print(f"   Question: {first_market.question}")
                    print(f"   ID: {first_market.id}")
                    print(f"   Slug: {first_market.slug}")
                    print(f"   Active: {first_market.active}, Closed: {first_market.closed}")

                    # Test 2: Get market by ID using real ID
                    print(f"\n🔍 Test 2: Get market by ID")
                    try:
                        market_by_id = await client.markets.get_market_by_id(first_market.id)
                        print(f"✅ Successfully fetched market by ID: {market_by_id.question}")
                        print(f"   Outcomes: {market_by_id.outcomes}")
                        print(f"   Categories: {len(market_by_id.categories)}")
                        print(f"   Tags: {len(market_by_id.tags)}")
                    except MarketNotFoundError:
                        print(f"❌ Market not found by ID: {first_market.id}")
                    except GammaAPIError as e:
                        print(f"❌ API Error: {e}")

                    # Test 3: Get market by slug using real slug
                    print(f"\n🔍 Test 3: Get market by slug")
                    try:
                        market_by_slug = await client.markets.get_market_by_slug(first_market.slug)
                        print(f"✅ Successfully fetched market by slug: {market_by_slug.question}")
                        print(f"   Description: {market_by_slug.description[:100]}...")
                        if market_by_slug.end_date:
                            print(f"   End date: {market_by_slug.end_date}")
                    except MarketNotFoundError:
                        print(f"❌ Market not found by slug: {first_market.slug}")
                    except GammaAPIError as e:
                        print(f"❌ API Error: {e}")

                    # Show more markets if available
                    if len(markets) > 1:
                        print(f"\n📋 Additional markets:")
                        for i, market in enumerate(markets[1:min(4, len(markets))], 2):
                            print(f"   {i}. {market.question}")
                            print(f"      ID: {market.id}")
                            print(f"      Slug: {market.slug}")
                            print(f"      Active: {market.active}, Closed: {market.closed}")
                            print()
                else:
                    print("⚠️  No markets returned from API")

            except GammaAPIError as e:
                print(f"❌ API Error: {e}")
                print("   This might be expected if the API requires authentication")

            # Test 4: Cache statistics
            print("\n💾 Cache Statistics")
            cache_stats = client.get_cache_stats()
            print(f"   Cache enabled: {cache_stats['enabled']}")
            print(f"   Memory cache size: {cache_stats.get('memory_size', 0)}")
            print(f"   Disk cache size: {cache_stats.get('disk_size', 0)}")

        except Exception as e:
            print(f"❌ Unexpected error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n🎉 Test completed!")


async def test_model_validation():
    """Test model validation with sample data."""
    print("\n🧪 Testing Model Validation")
    print("=" * 30)

    from py_gamma.models.markets import Market

    # Test with valid data
    valid_data = {
        "id": "0x1234567890abcdef1234567890abcdef12345678",
        "question": "Will Bitcoin reach $100,000 by end of 2024?",
        "description": "Test market for validation",
        "slug": "bitcoin-100k-2024",
        "active": True,
        "closed": False,
        "outcomes": ["Yes", "No"],
        "categories": [
            {"id": "crypto", "name": "Cryptocurrency"}
        ],
        "tags": [
            {"id": "1", "label": "Bitcoin", "slug": "bitcoin"}
        ]
    }

    try:
        market = Market(**valid_data)
        print("✅ Valid market data created successfully")
        print(f"   Question: {market.question}")
        print(f"   Outcomes: {market.outcomes}")
        print(f"   Categories: {len(market.categories)}")
        print(f"   Tags: {len(market.tags)}")
    except Exception as e:
        print(f"❌ Validation error: {e}")

    # Test with invalid data (intentionally incomplete to test validation)
    invalid_data = {
        # Missing required fields - this should fail validation
        "question": "Test question",
    }

    try:
        market = Market(**invalid_data)
        print("❌ Should have failed validation")
    except Exception as e:
        print(f"✅ Correctly caught validation error: {e}")
        print("   (This demonstrates that model validation is working properly)")


if __name__ == "__main__":
    print("Starting Py-Gamma SDK Tests")
    print("=" * 40)

    # Test model validation first
    asyncio.run(test_model_validation())

    # Test API functionality
    asyncio.run(test_market_endpoint())