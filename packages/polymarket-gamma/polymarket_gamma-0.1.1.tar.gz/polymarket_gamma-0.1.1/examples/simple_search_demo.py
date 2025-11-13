#!/usr/bin/env python3
"""
Simple demonstration of the Py-Gamma Search API functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path so we can import py_gamma
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from py_gamma import GammaClient, GammaConfig, SearchResult


async def demo_search():
    """Demonstrate search functionality."""
    print("🔍 Py-Gamma Search API Demo\n")

    # Initialize client
    config = GammaConfig(debug=True)
    async with GammaClient(config) as client:
        try:
            # Example 1: Search for crypto markets
            print("💰 Searching for crypto-related markets...")
            crypto_result = await client.search.search("bitcoin", limit_per_type=3)

            print(f"Found {crypto_result.total_count} total results:")
            print(f"  - Events: {len(crypto_result.events)}")
            print(f"  - Tags: {len(crypto_result.tags)}")
            print(f"  - Profiles: {len(crypto_result.profiles)}")

            if crypto_result.has_events:
                print("\n📅 Featured Events:")
                for event in crypto_result.events[:2]:
                    print(f"  • {event.title}")
                    print(f"    Markets: {event.market_count}")
                    if event.description:
                        print(f"    Description: {event.description[:100]}...")

            # Example 2: Get trending tags
            print("\n🔥 Getting trending tags...")
            trending_result = await client.search.get_trending_tags(limit_per_type=5)

            print(f"Found {trending_result.total_count} total tags:")
            for tag in trending_result.tags:
                print(f"  • {tag.label} ({tag.event_count} events)")

            # Example 3: Search for user profiles
            print("\n👥 Searching for user profiles...")
            profiles_result = await client.search.search_profiles("alice", limit_per_type=2)

            print(f"Found {profiles_result.total_count} total results:")
            print(f"  - Profiles: {len(profiles_result.profiles)}")

            if profiles_result.has_profiles:
                print("\n📋 Found Profiles:")
                for profile in profiles_result.profiles:
                    print(f"  • {profile.display_name}")
                    if profile.profile_image:
                        print(f"    🖼️  Has profile image")
                    if profile.bio:
                        print(f"    💭 {profile.bio[:80]}...")

            print("\n✅ Demo completed successfully!")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(demo_search())