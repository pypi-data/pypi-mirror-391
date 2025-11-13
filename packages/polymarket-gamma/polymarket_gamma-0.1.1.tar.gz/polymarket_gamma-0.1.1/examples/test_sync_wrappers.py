#!/usr/bin/env python3
"""
Standalone script to test synchronous wrapper functionality.
"""

import sys
from pathlib import Path

# Add src to path so we can import py_gamma
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from py_gamma import GammaClient, GammaConfig

def test_sync_wrappers():
    """Test synchronous convenience wrappers."""
    print("🔄 Testing synchronous wrappers...")

    try:
        # Test each sync wrapper with a fresh client to avoid event loop issues
        print("📝 Testing search_sync...")
        config = GammaConfig(debug=True)
        client = GammaClient(config)
        result = client.search.search_sync("crypto", limit_per_type=2)
        print(f"✅ Sync search completed!")
        print(f"   Total results: {result.total_count}")

        print("📝 Testing search_markets_sync...")
        config2 = GammaConfig(debug=True)
        client2 = GammaClient(config2)
        markets_result = client2.search.search_markets_sync("btc", limit_per_type=2)
        print(f"✅ Sync market search: {markets_result.total_count} results")

        print("📝 Testing get_trending_tags_sync...")
        config3 = GammaConfig(debug=True)
        client3 = GammaClient(config3)
        tags_result = client3.search.get_trending_tags_sync(limit_per_type=3)
        print(f"✅ Sync trending tags: {tags_result.total_count} results")

    except Exception as e:
        print(f"❌ Error in sync wrappers: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sync_wrappers()