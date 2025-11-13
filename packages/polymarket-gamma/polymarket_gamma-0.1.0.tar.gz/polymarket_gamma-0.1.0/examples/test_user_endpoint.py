"""
Test script demonstrating the User API endpoints functionality.

Note: Most user endpoints require authentication with a valid API key.
Without authentication, these endpoints will return 404 errors.
"""

import asyncio
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from py_gamma import GammaClient, GammaConfig
from py_gamma.exceptions import ProfileNotFoundError, ProfileAccessDeniedError, AuthenticationError, GammaAPIError


async def test_user_endpoints():
    """Test the User API endpoints."""
    # Check if API key is available
    api_key = os.getenv("POLYMARKET_API_KEY")
    if not api_key:
        print("⚠️  No POLYMARKET_API_KEY environment variable found.")
        print("   User endpoints require authentication. Set the API key to test authenticated endpoints.\n")

    # Initialize client with debug mode
    config = GammaConfig(
        base_url="https://gamma-api.polymarket.com",
        debug=True,
        api_key=api_key,  # Optional: set API key if available
    )

    async with GammaClient(config) as client:
        print("=== Testing User API Endpoints ===\n")

        # Test 1: Get current user profile (requires authentication)
        try:
            print("1. Testing get_profile()...")
            profile = await client.user.get_profile()
            print(f"   Profile: {profile.username}")
            print(f"   Display name: {profile.display_name}")
            print(f"   Email: {profile.email}")
            print(f"   Profile visibility: {profile.profile_visibility}")
            print(f"   Account age: {profile.account_age} days")
            print("   ✓ get_profile() successful\n")
        except AuthenticationError as e:
            print(f"   ✗ get_profile() failed: Authentication required - {e}\n")
        except GammaAPIError as e:
            error_msg = str(e)
            if "Expected JSON response but got" in error_msg or "404 page not found" in error_msg:
                print(f"   ✗ get_profile() failed: Endpoint not found or requires authentication\n")
            else:
                print(f"   ✗ get_profile() failed: {e}\n")
        except Exception as e:
            print(f"   ✗ get_profile() failed: {e}\n")

        # Test 2: Get profile by ID
        try:
            print("2. Testing get_profile_by_id()...")
            # Using a sample user ID - replace with actual ID
            sample_user_id = "0x1234567890123456789012345678901234567890"
            profile = await client.user.get_profile_by_id(sample_user_id)
            print(f"   Profile: {profile.username}")
            print(f"   Follower count: {profile.follower_count}")
            print(f"   Verified: {profile.verified}")
            print("   ✓ get_profile_by_id() successful\n")
        except ProfileNotFoundError:
            print(f"   ✗ get_profile_by_id() failed: User {sample_user_id} not found\n")
        except ProfileAccessDeniedError:
            print(f"   ✗ get_profile_by_id() failed: Access denied to user {sample_user_id}\n")
        except GammaAPIError as e:
            error_msg = str(e)
            if "Expected JSON response but got" in error_msg or "404 page not found" in error_msg:
                print(f"   ✗ get_profile_by_id() failed: Endpoint not found or requires authentication\n")
            else:
                print(f"   ✗ get_profile_by_id() failed: {e}\n")
        except Exception as e:
            print(f"   ✗ get_profile_by_id() failed: {e}\n")

        # Test 3: Get user stats
        try:
            print("3. Testing get_stats()...")
            stats = await client.user.get_stats()
            print(f"   Total positions: {stats.total_positions}")
            print(f"   Active positions: {stats.active_positions}")
            print(f"   Win rate: {stats.win_rate}%")
            print(f"   Experience level: {stats.experience_level}")
            print(f"   Is profitable trader: {stats.is_profitable_trader}")
            print("   ✓ get_stats() successful\n")
        except GammaAPIError as e:
            error_msg = str(e)
            if "Expected JSON response but got" in error_msg or "404 page not found" in error_msg:
                print(f"   ✗ get_stats() failed: Endpoint not found or requires authentication\n")
            else:
                print(f"   ✗ get_stats() failed: {e}\n")
        except Exception as e:
            print(f"   ✗ get_stats() failed: {e}\n")

        # Test 4: Get user positions
        try:
            print("4. Testing get_positions()...")
            positions = await client.user.get_positions(limit=10)
            print(f"   Total positions found: {positions.count}")
            if positions.positions:
                position = positions.positions[0]
                print(f"   Sample position: {position.market_question}")
                print(f"   Outcome: {position.outcome}")
                print(f"   Shares: {position.shares}")
                print(f"   Is profitable: {position.is_profitable}")
                print(f"   Is long: {position.is_long}")
            print("   ✓ get_positions() successful\n")
        except GammaAPIError as e:
            error_msg = str(e)
            if "Expected JSON response but got" in error_msg or "404 page not found" in error_msg:
                print(f"   ✗ get_positions() failed: Endpoint not found or requires authentication\n")
            else:
                print(f"   ✗ get_positions() failed: {e}\n")
        except Exception as e:
            print(f"   ✗ get_positions() failed: {e}\n")

        # Test 5: Get user history
        try:
            print("5. Testing get_history()...")
            history = await client.user.get_history(limit=10)
            print(f"   Total history entries: {history.count}")
            if history.history:
                entry = history.history[0]
                print(f"   Sample entry: {entry.transaction_type}")
                print(f"   Market question: {entry.market_question}")
                print(f"   Amount: {entry.amount}")
                print(f"   Timestamp: {entry.timestamp}")
            print("   ✓ get_history() successful\n")
        except GammaAPIError as e:
            error_msg = str(e)
            if "Expected JSON response but got" in error_msg or "404 page not found" in error_msg:
                print(f"   ✗ get_history() failed: Endpoint not found or requires authentication\n")
            else:
                print(f"   ✗ get_history() failed: {e}\n")
        except Exception as e:
            print(f"   ✗ get_history() failed: {e}\n")

        # Test 6: Get complete user information
        try:
            print("6. Testing get_user()...")
            # Using a sample user ID - replace with actual ID
            user = await client.user.get_user(
                user_id=sample_user_id,
                include_stats=True,
                include_positions=True,
                include_history=True,
                positions_limit=5,
                history_limit=5,
            )
            print(f"   User: {user.username}")
            print(f"   Display name: {user.profile.display_name}")
            print(f"   Stats available: {user.stats is not None}")
            print(f"   Positions count: {len(user.positions) if user.positions else 0}")
            print(f"   History count: {len(user.history) if user.history else 0}")
            print("   ✓ get_user() successful\n")
        except ProfileNotFoundError:
            print(f"   ✗ get_user() failed: User {sample_user_id} not found\n")
        except GammaAPIError as e:
            error_msg = str(e)
            if "Expected JSON response but got" in error_msg or "404 page not found" in error_msg:
                print(f"   ✗ get_user() failed: Endpoint not found or requires authentication\n")
            else:
                print(f"   ✗ get_user() failed: {e}\n")
        except Exception as e:
            print(f"   ✗ get_user() failed: {e}\n")

        # Test 7: Test pagination with iter_all_positions
        try:
            print("7. Testing iter_all_positions()...")
            count = 0
            async for position in client.user.iter_all_positions(page_size=3):
                count += 1
                print(f"   Position {count}: {position.market_question}")
                if count >= 6:  # Limit for demo
                    break
            print(f"   Total positions iterated: {count}")
            print("   ✓ iter_all_positions() successful\n")
        except GammaAPIError as e:
            error_msg = str(e)
            if "Expected JSON response but got" in error_msg or "404 page not found" in error_msg:
                print(f"   ✗ iter_all_positions() failed: Endpoint not found or requires authentication\n")
            else:
                print(f"   ✗ iter_all_positions() failed: {e}\n")
        except Exception as e:
            print(f"   ✗ iter_all_positions() failed: {e}\n")

        print("=== User API Endpoints Test Complete ===")

        # Summary
        print("\n=== Summary ===")
        if not api_key:
            print("🔒 All user endpoints require authentication.")
            print("   To test with authentication:")
            print("   1. Get a valid Polymarket API key")
            print("   2. Set the POLYMARKET_API_KEY environment variable:")
            print("      export POLYMARKET_API_KEY='your_api_key_here'")
            print("   3. Run this script again")
        else:
            print("🔑 API key is configured, but endpoints may still be unavailable")
            print("   This could indicate:")
            print("   - The API key is invalid or expired")
            print("   - User endpoints are not yet implemented in the API")
            print("   - Additional permissions are required")

        print("\n✅ Error handling improvements:")
        print("   - JSON parsing errors now show content type information")
        print("   - Authentication errors are handled gracefully")
        print("   - Method signature conflicts have been resolved")


def test_sync_endpoints():
    """Test synchronous convenience methods."""
    print("\n=== Testing Synchronous Convenience Methods ===\n")

    api_key = os.getenv("POLYMARKET_API_KEY")
    config = GammaConfig(
        base_url="https://gamma-api.polymarket.com",
        debug=True,
        api_key=api_key,
    )

    client = GammaClient(config)

    try:
        # Test sync profile access
        print("Testing get_profile_sync()...")
        # This will likely fail without authentication, but tests the sync wrapper
        profile = client.user.get_profile_sync()
        print(f"   Profile: {profile.username}")
        print("   ✓ get_profile_sync() successful")
    except AuthenticationError as e:
        print(f"   ✗ get_profile_sync() failed: Authentication required - {e}")
    except GammaAPIError as e:
        error_msg = str(e)
        if "Expected JSON response but got" in error_msg or "404 page not found" in error_msg:
            print(f"   ✗ get_profile_sync() failed: Endpoint not found or requires authentication")
        else:
            print(f"   ✗ get_profile_sync() failed: {e}")
    except Exception as e:
        print(f"   ✗ get_profile_sync() failed: {e}")

    print("\n=== Sync Methods Test Complete ===")


if __name__ == "__main__":
    # Run async tests
    asyncio.run(test_user_endpoints())

    # Run sync tests
    test_sync_endpoints()