#!/usr/bin/env python3
"""
Demo of working Py-Gamma SDK endpoints.

This script demonstrates the endpoints that work without authentication
and shows real data from the Polymarket Gamma API.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path to import py_gamma
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from py_gamma import GammaClient, GammaConfig


async def demo_markets():
    """Demo Markets endpoint."""
    print("🏪 Markets Endpoint Demo")
    print("=" * 40)

    client = GammaClient()

    try:
        # List markets
        markets = await client.markets.get_markets(limit=5)
        print(f"✅ Found {len(markets)} markets")

        for i, market in enumerate(markets[:3], 1):
            print(f"{i}. {market.question}")
            print(f"   ID: {market.id}")
            print(f"   Slug: {market.slug}")
            print(f"   Active: {market.active}, Closed: {market.closed}")
            print(f"   Outcomes: {market.outcomes}")
            if market.end_date:
                print(f"   Ends: {market.end_date.strftime('%Y-%m-%d')}")
            print()

        # Test fetching by ID using real data
        if markets:
            first_market = markets[0]
            market_detail = await client.markets.get_market_by_id(first_market.id)
            print(f"✅ Fetched market by ID: {market_detail.question}")
            print(f"   Description: {market_detail.description[:100]}...")

    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_tags():
    """Demo Tags endpoint."""
    print("\n🏷️  Tags Endpoint Demo")
    print("=" * 40)

    client = GammaClient()

    try:
        # List tags
        tags = await client.tags.get_tags(limit=10)
        print(f"✅ Found {len(tags)} tags")

        for i, tag in enumerate(tags[:5], 1):
            print(f"{i}. {tag.label}")
            print(f"   ID: {tag.id}, Slug: {tag.slug}")
            if tag.is_carousel:
                print(f"   🎠 Featured in carousel")
            print()

        # Get carousel tags
        carousel_tags = await client.tags.get_carousel_tags()
        print(f"✅ Found {len(carousel_tags)} carousel tags")
        for tag in carousel_tags:
            print(f"   🎠 {tag.label}")

    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_search():
    """Demo Search endpoint."""
    print("\n🔍 Search Endpoint Demo")
    print("=" * 40)

    client = GammaClient()

    try:
        # Search for markets
        result = await client.search.search("bitcoin", limit_per_type=3)
        print(f"✅ Search for 'bitcoin': {result.total_count} total results")
        print(f"   Events: {len(result.events)}")
        print(f"   Tags: {len(result.tags)}")
        print(f"   Profiles: {len(result.profiles)}")

        # Show some events
        if result.events:
            print("\n   Sample events:")
            for event in result.events[:2]:
                print(f"   - {event.title}")
                if hasattr(event, 'markets') and event.markets:
                    print(f"     Markets: {len(event.markets)}")

    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_events():
    """Demo Events endpoint."""
    print("\n📅 Events Endpoint Demo")
    print("=" * 40)

    client = GammaClient()

    try:
        # List events
        events = await client.events.get_events(limit=5)
        print(f"✅ Found {len(events)} events")

        for i, event in enumerate(events[:3], 1):
            print(f"{i}. {event.title}")
            print(f"   ID: {event.id}")
            print(f"   Slug: {event.slug}")
            print(f"   Active: {event.active}")
            if hasattr(event, 'markets') and event.markets:
                print(f"   Markets: {len(event.markets)}")
            print()

    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_series():
    """Demo Series endpoint."""
    print("\n📚 Series Endpoint Demo")
    print("=" * 40)

    client = GammaClient()

    try:
        # List series
        series_list = await client.series.get_series(limit=5)
        print(f"✅ Found {len(series_list)} series")

        for i, series in enumerate(series_list[:3], 1):
            print(f"{i}. {series.title}")
            print(f"   ID: {series.id}")
            print(f"   Active: {series.active}")
            if hasattr(series, 'description') and series.description:
                print(f"   Description: {series.description[:80]}...")
            print()

    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_sports():
    """Demo Sports endpoint."""
    print("\n⚽ Sports Endpoint Demo")
    print("=" * 40)

    client = GammaClient()

    try:
        # List sports (no limit parameter available)
        sports = await client.sports.get_sports()
        print(f"✅ Found {len(sports)} sports")

        for i, sport in enumerate(sports[:3], 1):
            print(f"{i}. {sport.sport}")
            print(f"   Image: {sport.image}")
            print(f"   Resolution: {sport.resolution}")
            print()

        # Test a sport with leagues if available
        if sports:
            first_sport = sports[0]
            try:
                leagues = await client.sports.get_leagues_for_sport(first_sport.sport, limit=3)
                print(f"✅ Found {len(leagues)} leagues for {first_sport.sport}")
                for league in leagues[:2]:
                    print(f"   - {league.name}")
            except Exception as e:
                print(f"⚠️  No leagues found for {first_sport.sport}: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all demos."""
    print("🚀 Py-Gamma SDK Demo - Working Endpoints")
    print("=" * 60)
    print("This demo shows endpoints that work without authentication")
    print()

    # Run async demos
    await demo_markets()
    await demo_tags()
    await demo_search()
    await demo_events()
    await demo_series()
    await demo_sports()

    print("\n🎉 Demo completed!")
    print("\nNote: Some endpoints (User, Comments with auth features) may require")
    print("authentication and are not included in this demo.")
    print("Sync convenience wrappers are available but not demonstrated in this async demo.")


if __name__ == "__main__":
    asyncio.run(main())