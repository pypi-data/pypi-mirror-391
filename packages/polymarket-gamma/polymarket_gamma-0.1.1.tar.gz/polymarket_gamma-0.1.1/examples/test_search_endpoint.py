#!/usr/bin/env python3
"""
Example script demonstrating the Search API endpoint functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path so we can import py_gamma
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from py_gamma import GammaClient, GammaConfig, SearchResult, SearchValidationError
from py_gamma.exceptions import GammaAPIError


async def test_basic_search():
    """Test basic search functionality."""
    print("🔍 Testing basic search functionality...")

    # Initialize client
    config = GammaConfig(debug=True)
    async with GammaClient(config) as client:
        try:
            # Test a simple search query
            result = await client.search.search("trump", limit_per_type=5)

            print(f"✅ Search completed successfully!")
            print(f"   Total results: {result.total_count}")
            print(f"   Events: {len(result.events)}")
            print(f"   Tags: {len(result.tags)}")
            print(f"   Profiles: {len(result.profiles)}")
            print(f"   Has more: {result.has_more_results}")

            # Display some results
            if result.has_events:
                print(f"\n📅 Sample Event:")
                event = result.events[0]
                print(f"   Title: {event.title}")
                print(f"   Markets: {event.market_count}")

            if result.has_tags:
                print(f"\n🏷️  Sample Tag:")
                tag = result.tags[0]
                print(f"   Label: {tag.label}")
                print(f"   Events: {tag.event_count}")
                print(f"   Popularity: {tag.popularity}")

            if result.has_profiles:
                print(f"\n👤 Sample Profile:")
                profile = result.profiles[0]
                print(f"   Name: {profile.display_name}")
                print(f"   Has image: {profile.has_image}")

        except SearchValidationError as e:
            print(f"❌ Search validation error: {e}")
        except GammaAPIError as e:
            print(f"❌ API error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


async def test_market_search():
    """Test market-specific search."""
    print("\n🏦 Testing market search...")

    config = GammaConfig(debug=True)
    async with GammaClient(config) as client:
        try:
            result = await client.search.search_markets("election", limit_per_type=3)

            print(f"✅ Market search completed!")
            print(f"   Total results: {result.total_count}")
            print(f"   Events (with markets): {len(result.events)}")

            # Show markets in events
            for event in result.events[:2]:  # Show first 2 events
                print(f"\n   Event: {event.title}")
                for market in event.markets[:2]:  # Show first 2 markets per event
                    print(f"     - {market.question}")
                    print(f"       Active: {market.active}, Closed: {market.closed}")

        except Exception as e:
            print(f"❌ Error in market search: {e}")


async def test_profile_search():
    """Test profile search."""
    print("\n👥 Testing profile search...")

    config = GammaConfig(debug=True)
    async with GammaClient(config) as client:
        try:
            result = await client.search.search_profiles("john", limit_per_type=3)

            print(f"✅ Profile search completed!")
            print(f"   Total results: {result.total_count}")
            print(f"   Profiles found: {len(result.profiles)}")

            for profile in result.profiles:
                print(f"   - {profile.display_name}")
                if profile.bio:
                    print(f"     Bio: {profile.bio[:50]}...")

        except Exception as e:
            print(f"❌ Error in profile search: {e}")


async def test_trending_tags():
    """Test trending tags functionality."""
    print("\n🔥 Testing trending tags...")

    config = GammaConfig(debug=True)
    async with GammaClient(config) as client:
        try:
            result = await client.search.get_trending_tags(limit_per_type=5)

            print(f"✅ Trending tags completed!")
            print(f"   Total results: {result.total_count}")
            print(f"   Tags found: {len(result.tags)}")

            for tag in result.tags:
                print(f"   - {tag.label} ({tag.event_count} events, {tag.popularity} popularity)")

        except Exception as e:
            print(f"❌ Error getting trending tags: {e}")




async def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\n⚠️  Testing error handling...")

    config = GammaConfig(debug=True)
    client = GammaClient(config)

    try:
        # Test empty query (should raise SearchValidationError)
        await client.search.search("")
        print("❌ Should have raised SearchValidationError for empty query")

    except SearchValidationError as e:
        print(f"✅ Correctly caught SearchValidationError: {e}")

    try:
        # Test query with only whitespace
        await client.search.search("   ")
        print("❌ Should have raised SearchValidationError for whitespace query")

    except SearchValidationError as e:
        print(f"✅ Correctly caught SearchValidationError for whitespace: {e}")

    finally:
        await client.close()


async def main():
    """Run all tests."""
    print("🚀 Starting Py-Gamma Search API Tests\n")

    # Run async tests
    await test_basic_search()
    await test_market_search()
    await test_profile_search()
    await test_trending_tags()
    await test_error_handling()

    # Test sync wrapper - just test one to avoid event loop conflicts
    print("\n🔄 Testing synchronous wrapper...")
    try:
        config = GammaConfig(debug=True)
        client = GammaClient(config)

        # Test just one sync wrapper to avoid asyncio.run() conflicts
        result = client.search.search_sync("crypto", limit_per_type=2)
        print(f"✅ Sync search completed! Total results: {result.total_count}")
        print(f"   Events: {len(result.events)}, Tags: {len(result.tags)}, Profiles: {len(result.profiles)}")

    except Exception as e:
        print(f"❌ Error in sync wrapper: {e}")
        print("   Note: Sync wrappers work but have limitations in async contexts")

    print("\n🎉 All search API tests completed!")


if __name__ == "__main__":
    asyncio.run(main())