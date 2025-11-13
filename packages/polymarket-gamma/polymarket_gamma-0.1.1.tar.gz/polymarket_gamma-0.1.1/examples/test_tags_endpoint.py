#!/usr/bin/env python3
"""
Test script for Tags API endpoint.

This script demonstrates the usage of the Tags endpoint in the Py-Gamma SDK.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path to import py_gamma
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from py_gamma import GammaClient, Tag, TagNotFoundError


async def test_get_tag_by_id():
    """Test getting a tag by ID."""
    print("Testing get_tag_by_id...")

    client = GammaClient()

    try:
        # First get a list of tags to find real IDs
        tags = await client.tags.get_tags(limit=5)
        if tags:
            first_tag = tags[0]
            print(f"Using real tag ID: {first_tag.id}")
            tag = await client.tags.get_tag_by_id(first_tag.id)
            print(f"Successfully fetched tag: {tag.label}")
            print(f"Tag details: ID={tag.id}, Slug={tag.slug}, Carousel={tag.is_carousel}")
        else:
            print("No tags found to test with")
    except TagNotFoundError:
        print("Tag not found")
    except Exception as e:
        print(f"Error fetching tag: {e}")


async def test_get_tags():
    """Test getting a list of tags."""
    print("\nTesting get_tags...")

    client = GammaClient()

    try:
        # Get first page of tags
        tags = await client.tags.get_tags(limit=10)
        print(f"Successfully fetched {len(tags)} tags")

        for i, tag in enumerate(tags[:3]):  # Show first 3 tags
            print(f"  {i+1}. {tag.label} (ID: {tag.id}, Slug: {tag.slug})")

        if len(tags) > 3:
            print(f"  ... and {len(tags) - 3} more")

    except Exception as e:
        print(f"Error fetching tags: {e}")


async def test_get_carousel_tags():
    """Test getting carousel tags."""
    print("\nTesting get_carousel_tags...")

    client = GammaClient()

    try:
        carousel_tags = await client.tags.get_carousel_tags(limit=10)
        print(f"Successfully fetched {len(carousel_tags)} carousel tags")

        for i, tag in enumerate(carousel_tags[:3]):  # Show first 3 tags
            print(f"  {i+1}. {tag.label} (ID: {tag.id}, Carousel: {tag.is_carousel})")

        if len(carousel_tags) > 3:
            print(f"  ... and {len(carousel_tags) - 3} more")

    except Exception as e:
        print(f"Error fetching carousel tags: {e}")


async def test_search_tags():
    """Test searching for tags."""
    print("\nTesting search_tags...")

    client = GammaClient()

    try:
        # Search for tags - try different search terms to see what works
        search_terms = ["crypto", "sport", "politic", "market"]

        for term in search_terms:
            try:
                found_tags = await client.tags.search_tags(term, limit=5)
                print(f"Found {len(found_tags)} tags containing '{term}'")

                for tag in found_tags:
                    print(f"  - {tag.label} (ID: {tag.id})")

                if found_tags:
                    break  # Found some tags, no need to try other terms
            except Exception as search_error:
                print(f"Search for '{term}' failed: {search_error}")
                continue

        # If no search terms worked, let user know
        print("Note: Search functionality may need implementation or different search terms")

    except Exception as e:
        print(f"Error searching tags: {e}")


def test_sync_wrapper():
    """Test synchronous convenience wrapper."""
    print("\nTesting synchronous wrapper...")

    client = GammaClient()

    try:
        # Use sync wrapper to get tags (using list_sync)
        tags = client.sync.tags.list_sync(limit=5)
        print(f"Successfully fetched {len(tags)} tags using sync wrapper")

        for i, tag in enumerate(tags):
            print(f"  {i+1}. {tag.label}")

        # Test get_sync method to get a specific tag by ID
        if tags:
            first_tag_id = tags[0].id
            print(f"\nTesting get_sync with tag ID: {first_tag_id}")

            # Note: get_sync is available directly on the tags endpoint, not through sync wrapper
            # We need to create a new instance to test the get_sync method
            from py_gamma.endpoints.tags import TagsEndpoint
            from py_gamma.client import AsyncHTTPClient
            from py_gamma.config import GammaConfig

            sync_client = TagsEndpoint(AsyncHTTPClient(GammaConfig()))
            single_tag = sync_client.get_sync(first_tag_id)
            print(f"Successfully fetched single tag: {single_tag.label}")

    except Exception as e:
        print(f"Error with sync wrapper: {e}")


async def test_tag_model_features():
    """Test Tag model features."""
    print("\nTesting Tag model features...")

    # Create a test tag
    tag_data = {
        "id": "test-1",
        "label": "Test Tag",
        "slug": "test-tag",
        "forceShow": True,
        "forceHide": False,
        "isCarousel": True,
        "publishedAt": "2024-01-01T00:00:00Z",
        "createdBy": 123,
        "updatedBy": 456,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z"
    }

    tag = Tag(**tag_data)

    print(f"Created tag: {tag.label}")
    print(f"  ID: {tag.id}")
    print(f"  Slug: {tag.slug}")
    print(f"  Force Show: {tag.force_show}")
    print(f"  Force Hide: {tag.force_hide}")
    print(f"  Is Carousel: {tag.is_carousel}")
    print(f"  Created At: {tag.created_at}")
    print(f"  Updated At: {tag.updated_at}")

    # Test model serialization using Pydantic methods
    tag_dict = tag.model_dump()
    print(f"  Model dict keys: {list(tag_dict.keys())}")

    tag_json = tag.model_dump_json()
    print(f"  JSON length: {len(tag_json)} characters")


async def main():
    """Run all tests."""
    print("Starting Tags API tests...")
    print("=" * 50)

    # Test model features first
    await test_tag_model_features()

    # Test actual API calls
    await test_get_tag_by_id()
    await test_get_tags()
    await test_get_carousel_tags()
    await test_search_tags()

    # Test sync wrapper - run it separately from the async context
    # We can't call sync functions that use asyncio.run() from within an async context
    # So we'll create a separate task for it
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, test_sync_wrapper)

    print("\n" + "=" * 50)
    print("Tags API tests completed!")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())